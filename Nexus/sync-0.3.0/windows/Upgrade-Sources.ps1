#requires -Version 5.1
[CmdletBinding()]
param([string]$InstallPath = "$env:USERPROFILE\AppData\Local\DuckMooNexusSync")
$ErrorActionPreference='Stop'
$config=Join-Path $InstallPath 'config.json'
if (-not (Test-Path -LiteralPath $config)) { throw 'Existing sync installation not found' }
$task=Get-ScheduledTask -TaskName 'DuckMoo Nexus Journalator Sync'
$sourceTaskName='DuckMoo Nexus Additional Sources'
if (Get-ScheduledTask -TaskName $sourceTaskName -ErrorAction SilentlyContinue) {
 throw 'Additional source task already exists; inspect it before upgrading'
}
# Fail before changing files or the task when collection cannot run.
& python -c "import sys; assert sys.version_info >= (3,13), 'Python 3.13+ required'"
if ($LASTEXITCODE -ne 0) { throw 'Python 3.13+ is required before enabling sources' }
if ($task.State -eq 'Running') { throw 'Sync is running; retry after it finishes' }
$release=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
foreach ($name in 'collect_sources.py','snapshots.py','bundle.py','acknowledge.py') {
 if (-not (Test-Path -LiteralPath (Join-Path $release "duckmoo-nexus\$name"))) { throw "Missing collector file: $name" }
}
$backup=Join-Path $InstallPath ('before-sources-' + (Get-Date -Format 'yyyyMMddTHHmmss'))
New-Item -ItemType Directory -Path $backup | Out-Null
Export-ScheduledTask -TaskName $task.TaskName | Set-Content -LiteralPath (Join-Path $backup 'task.xml') -Encoding UTF8
foreach ($name in 'Sync-Journalator.ps1','Sync-Helpers.ps1','config.json') {
 Copy-Item -LiteralPath (Join-Path $InstallPath $name) -Destination $backup
}
# No credentials or original Journalator script are overwritten.
foreach ($name in 'Sync-Sources.ps1','Sync-All.ps1') {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $InstallPath -Force
}
$collector=Join-Path $InstallPath 'collector'
New-Item -ItemType Directory -Force -Path $collector | Out-Null
foreach ($name in 'collect_sources.py','snapshots.py','bundle.py','acknowledge.py') {
 Copy-Item -LiteralPath (Join-Path $release "duckmoo-nexus\$name") -Destination $collector -Force
}
$exe="$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments='-NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File "' + (Join-Path $InstallPath 'Sync-Sources.ps1') + '"'
$action=New-ScheduledTaskAction -Execute $exe -Argument $arguments -WorkingDirectory $InstallPath
Register-ScheduledTask -TaskName $sourceTaskName -TaskPath $task.TaskPath -Action $action -Trigger $task.Triggers -Principal $task.Principal -Settings $task.Settings | Out-Null
Write-Host "Separate additional-source task installed. Backup: $backup"
Write-Host 'Server v0.3.0 and its source timer must already be tested and enabled. The existing Journalator task and shortcut stay unchanged.'
