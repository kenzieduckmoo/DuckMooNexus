#requires -Version 5.1
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$BackupPath,
 [string]$InstallPath = "$env:USERPROFILE\AppData\Local\DuckMooNexusSync"
)
$ErrorActionPreference='Stop'
$installation=[IO.Path]::GetFullPath($InstallPath).TrimEnd('\') + '\'
$backup=[IO.Path]::GetFullPath($BackupPath).TrimEnd('\') + '\'
if (-not $backup.StartsWith($installation,[StringComparison]::OrdinalIgnoreCase)) {
 throw 'Backup must be inside the existing sync installation'
}
if (-not (Test-Path -LiteralPath (Join-Path $backup 'task.xml'))) { throw 'Backup task XML not found' }
$task=Get-ScheduledTask -TaskName 'DuckMoo Nexus Additional Sources'
if ($task.State -eq 'Running') { throw 'Wait for the active sync to finish before restoring its task' }
# The original Journalator task/helper/config were never replaced by this upgrade.
Unregister-ScheduledTask -TaskName $task.TaskName -TaskPath $task.TaskPath -Confirm:$false
Write-Host 'Additional-source task removed. Original Journalator task, source archives and pending packets retained.'
