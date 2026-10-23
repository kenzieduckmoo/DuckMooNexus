#requires -Version 5.1
[CmdletBinding()]
param([string]$ConfigPath = "$PSScriptRoot\config.json", [string]$Python = 'python', [switch]$Manual)
$ErrorActionPreference='Stop'
. "$PSScriptRoot\Sync-Helpers.ps1"
$config=Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
if ($config.HostName -ne '10.20.30.239' -or $config.UserName -ne 'kenzieduckmoo') { throw 'Unexpected server identity' }
$state=Join-Path $PSScriptRoot 'sources-state'
New-Item -ItemType Directory -Force -Path $state | Out-Null
$lock=$null
try {
    try { $lock=[IO.File]::Open((Join-Path $state 'sync.lock'),'OpenOrCreate','ReadWrite','None') }
    catch [IO.IOException] { exit 0 }
    $sourceDirectory=Split-Path -Parent $config.SourcePath
    # Existing SourcePath is .../WTF/Account/account/SavedVariables.
    $clientRoot=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $sourceDirectory)))
    $appdata=Join-Path $clientRoot 'Interface\AddOns\TradeSkillMaster_AppHelper\AppData.lua'
    $collector=Join-Path $PSScriptRoot 'collector\collect_sources.py'
    $json=& $Python $collector $sourceDirectory $state --tsm-appdata $appdata
    if ($LASTEXITCODE -ne 0) { throw 'Source collector failed' }
    $packets=$json | ConvertFrom-Json
    foreach ($packet in $packets) {
        $status=Invoke-SyncSsh -Config $config -Command "status $($packet.hash)" | ConvertFrom-Json
        if ($status.sha256 -ne $packet.hash) { throw 'Receipt hash mismatch' }
        if ($status.status -in @('imported','already_imported','archived')) {
            $checkpoints=Join-Path $state 'source-checkpoints.json'
            # JSON acknowledgement by Python preserves precise numeric fingerprints.
            & $Python (Join-Path $PSScriptRoot 'collector\acknowledge.py') $checkpoints $packet.hash
            if ($LASTEXITCODE -ne 0) { throw 'Checkpoint update failed' }
            Remove-Item -LiteralPath $packet.path -Force
        } elseif ($status.status -ne 'queued') {
            $queued=Invoke-SyncSsh -Config $config -Command "put2 $($packet.hash) $($packet.bytes)" -InputFile $packet.path | ConvertFrom-Json
            if ($queued.status -ne 'queued' -or $queued.sha256 -ne $packet.hash) { throw 'Packet was not acknowledged' }
        }
    }
} finally { if ($lock) { $lock.Dispose() } }
