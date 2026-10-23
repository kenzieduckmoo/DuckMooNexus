#requires -Version 5.1
[CmdletBinding()]
param([string]$ConfigPath, [switch]$Manual)
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path $PSScriptRoot 'config.json'
}
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Sync-Helpers.ps1"
$lock = $null
$snapshot = $null
$exitCode = 0
try {
    $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    $state = Join-Path $PSScriptRoot 'state'
    New-Item -ItemType Directory -Force -Path $state | Out-Null
    try {
        $lock = [IO.File]::Open((Join-Path $state 'sync.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
    } catch [IO.IOException] {
        Write-Host 'Another sync is running.'
        exit 0
    }
    $log = Join-Path $state 'sync.log'
    if ((Test-Path $log) -and (Get-Item $log).Length -gt 2MB) {
        Move-Item -LiteralPath $log -Destination "$log.1" -Force
    }
    function Log([string]$Message) {
        $line = '{0} {1}' -f [DateTime]::UtcNow.ToString('o'), $Message
        Add-Content -LiteralPath $log -Value $line -Encoding UTF8
        if ($Manual) { Write-Host $line }
    }
    foreach ($field in 'SourcePath','IdentityFile','KnownHostsFile') {
        if (-not (Test-Path -LiteralPath $config.$field -PathType Leaf)) { throw "Missing $field" }
    }
    if ($config.HostName -ne '10.20.30.239' -or $config.UserName -ne 'kenzieduckmoo') {
        throw 'Unexpected server identity; review configuration and scripts together.'
    }
    $snapshot = Join-Path $state 'snapshot.tmp'
    try {
        $hash = New-StableSnapshot -Source $config.SourcePath -Destination $snapshot -QuietSeconds 15 -SampleSeconds 10
    } catch [IO.IOException] {
        Log 'DEFERRED source is busy or changed; next scheduled run will retry.'
        $exitCode = 2
    }
    if ($exitCode -eq 0) {
        # Always ask the server; a lost local checkpoint or server DB recovery must not
        # be hidden by a permanent client-side same-hash skip.
        $status = Invoke-SyncSsh -Config $config -Command "status $hash" | ConvertFrom-Json
        if ($status.sha256 -ne $hash) { throw 'Server receipt hash mismatch' }
        if ($status.status -notin @('imported','already_imported')) {
            $size = (Get-Item -LiteralPath $snapshot).Length
            $queued = Invoke-SyncSsh -Config $config -Command "put $hash $size" -InputFile $snapshot | ConvertFrom-Json
            if ($queued.status -ne 'queued' -or $queued.sha256 -ne $hash) { throw 'Upload was not acknowledged' }
            Log "QUEUED sha256=$hash bytes=$size"
            # The durable server timer continues even if Windows disconnects now.
            for ($i = 0; $i -lt 18; $i++) {
                Start-Sleep -Seconds 10
                $status = Invoke-SyncSsh -Config $config -Command "status $hash" | ConvertFrom-Json
                if ($status.sha256 -ne $hash) { throw 'Server receipt hash mismatch' }
                if ($status.status -in @('imported','already_imported','failed')) { break }
            }
        }
        if ($status.status -in @('imported','already_imported')) {
            $checkpoint = Join-Path $state 'last-success.json'
            $status | ConvertTo-Json | Set-Content -LiteralPath "$checkpoint.tmp" -Encoding UTF8
            Move-Item -LiteralPath "$checkpoint.tmp" -Destination $checkpoint -Force
            Log "SUCCESS sha256=$hash status=$($status.status) inserted=$($status.inserted) records=$($status.records)"
        } elseif ($status.status -eq 'failed') {
            throw "Server import failed ($($status.error)); inspect server journal and receipt."
        } else {
            Log "PENDING sha256=$hash; server worker will continue; next run checks again."
            $exitCode = 2
        }
    }
} catch {
    $exitCode = 1
    if (Get-Command Log -ErrorAction SilentlyContinue) { Log "ERROR $($_.Exception.Message)" }
    else { Write-Error $_ -ErrorAction Continue }
} finally {
    if ($snapshot -and (Test-Path -LiteralPath $snapshot)) { Remove-Item -LiteralPath $snapshot -Force }
    if ($lock) { $lock.Dispose() }
}
if ($Manual) { Write-Host "Sync exit code: $exitCode (0 success, 1 error, 2 deferred/pending)."; Read-Host 'Press Enter to close' | Out-Null }
exit $exitCode

