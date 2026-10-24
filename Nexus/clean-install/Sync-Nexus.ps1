#requires -Version 5.1
[CmdletBinding()]
param([string]$ConfigPath)
$ErrorActionPreference = 'Stop'
# Resolve after parameter binding, in this script's scope (also safe when dot sourced).
$scriptDirectory = $PSScriptRoot
if (-not $ConfigPath) { $ConfigPath = Join-Path $scriptDirectory 'config.json' }
. (Join-Path $scriptDirectory 'Sync-Helpers.ps1')
$state = Join-Path $scriptDirectory 'state'
if ($ConfigPath -and (Test-Path -LiteralPath $ConfigPath)) {
    $stateConfig = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    if ($stateConfig.StateDirectory) { $state = [string]$stateConfig.StateDirectory }
}
New-Item -ItemType Directory -Force -Path $state | Out-Null
$lock = $null
try {
    try { $lock = [IO.File]::Open((Join-Path $state 'sync.lock'),'OpenOrCreate','ReadWrite','None') }
    catch [IO.IOException] { exit 0 }
    $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    $arguments = @((Join-Path $scriptDirectory 'app\collect_sources.py'), $config.SavedVariables, $state)
    if ($config.TsmAppData) { $arguments += @('--tsm-appdata', $config.TsmAppData) }
    $namespace = if ($config.Namespace) { [string]$config.Namespace } else { 'retail-main-account' }
    if ($namespace -notin @('retail-main-account','forever-main-account')) { throw 'Unsupported client namespace' }
    $arguments += @('--namespace', $namespace)
    if ($config.MinimumSavedAt) { $arguments += @('--minimum-saved-at', [string]$config.MinimumSavedAt) }
    $collectorError = Join-Path $state 'collector-error.log'
    $packetsJson = & $config.Python @arguments 2> $collectorError
    if ($LASTEXITCODE -ne 0) { throw ("Source collection failed: " + (Get-Content -LiteralPath $collectorError -Raw)) }
    $packets = ConvertFrom-Json -InputObject ($packetsJson -join "`n")
    if ($packets.Count -eq 0) {
        if ($config.AllowEmpty) {
            @{success=$true; status='awaiting_first_save'; namespace=$namespace; at=[DateTime]::UtcNow.ToString('o'); packets=0} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $state 'last-result.json') -Encoding UTF8
            exit 0
        }
        throw 'No source packets found; check SavedVariables path and allow recent saves 15 seconds to settle.'
    }
    # One small receipt query avoids uploading the entire retained history each run.
    # The server checks its current generation, so reinstall/recovery still replays
    # any packets whose committed receipt is no longer valid. Local archives stay.
    $queryPath = Join-Path $state 'receipt-query.json'
    $digests = @($packets | ForEach-Object { $_.hash })
    $committed = New-Object 'System.Collections.Generic.HashSet[string]'
    for ($offset=0; $offset -lt $digests.Count; $offset+=5000) {
        $last = [Math]::Min($offset+4999,$digests.Count-1)
        $batch = @($digests[$offset..$last])
        [IO.File]::WriteAllText($queryPath, (ConvertTo-Json -InputObject $batch -Compress), (New-Object Text.UTF8Encoding($false)))
        $known = Invoke-SyncSsh -Config $config -Command 'receipts' -InputFile $queryPath | ConvertFrom-Json
        foreach ($digest in $known.committed) { [void]$committed.Add([string]$digest) }
    }
    $previouslyCommitted = $committed.Count
    $count = 0
    foreach ($packet in $packets) {
        if ($committed.Contains([string]$packet.hash)) { continue }
        $receipt = Invoke-SyncSsh -Config $config -Command "put $($packet.hash) $($packet.bytes)" -InputFile $packet.path | ConvertFrom-Json
        if ($receipt.sha256 -ne $packet.hash -or $receipt.status -notin @('imported','already_imported','archived')) {
            throw "Server did not commit packet $($packet.hash)"
        }
        [void]$committed.Add([string]$packet.hash)
        $count++
    }
    # Give the independent addon only receipts backed by this run's server ACKs.
    # A receipt problem must retain the local journal, not fail other source syncs.
    $omniAck = @{ status='not_attempted' }
    try {
        [IO.File]::WriteAllText((Join-Path $state 'omni-committed-packets.json'), (ConvertTo-Json -InputObject @($committed) -Compress), (New-Object Text.UTF8Encoding($false)))
        $ackOutput = & $config.Python (Join-Path $scriptDirectory 'app\write_omni_ack.py') $config.SavedVariables $state --namespace $namespace 2> (Join-Path $state 'omni-ack-error.log')
        if ($LASTEXITCODE -ne 0) { throw 'Omni receipt update failed; local journal retained.' }
        $omniAck = ConvertFrom-Json -InputObject ($ackOutput -join "`n")
    } catch {
        $omniAck = @{ status='retained'; error=$_.ToString() }
        Add-Content -LiteralPath (Join-Path $state 'sync.log') -Value "$([DateTime]::UtcNow.ToString('o')) Omni receipt deferred; local journal retained"
    }
    @{ success=$true; at=[DateTime]::UtcNow.ToString('o'); packets=$count; alreadyCommitted=$previouslyCommitted; omniAck=$omniAck } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $state 'last-result.json') -Encoding UTF8
    Add-Content -LiteralPath (Join-Path $state 'sync.log') -Value "$([DateTime]::UtcNow.ToString('o')) OK $count packets uploaded; $previouslyCommitted already committed"
} catch {
    $message = $_.ToString()
    @{ success=$false; at=[DateTime]::UtcNow.ToString('o'); error=$message } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $state 'last-result.json') -Encoding UTF8
    Add-Content -LiteralPath (Join-Path $state 'sync.log') -Value "$([DateTime]::UtcNow.ToString('o')) FAILED $message"
    [Console]::Error.WriteLine($message)
    exit 1
} finally { if ($lock) { $lock.Dispose() } }
