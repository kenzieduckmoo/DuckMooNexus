#requires -Version 5.1
# Run in a normal Windows user session: packaged-app AppData redirection can hide new folders from Task Scheduler.
[CmdletBinding()]
param([string]$WowRoot='D:\World of Warcraft',[string]$RetailSync=(Join-Path $env:LOCALAPPDATA 'DuckMooNexusClean'),[string]$ForeverSync=(Join-Path $env:LOCALAPPDATA 'DuckMooNexusForever'))
$ErrorActionPreference='Stop'
$workspace=Split-Path $PSScriptRoot -Parent
$client=Join-Path $WowRoot '_forever_'
if (-not (Test-Path -LiteralPath (Join-Path $client 'Wow.exe'))) { throw 'Installed Forever client not found' }
$base=Get-Content -LiteralPath (Join-Path $RetailSync 'config.json') -Raw | ConvertFrom-Json
$account=Split-Path (Split-Path ([string]$base.SavedVariables) -Parent) -Leaf
$sv=Join-Path $client ('WTF\Account\'+$account+'\SavedVariables')
$backup=Join-Path $PSScriptRoot ('forever-preparation\backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $backup,$ForeverSync,(Join-Path $ForeverSync 'app'),$sv | Out-Null
$source=Join-Path $workspace 'AddOns\DuckMooOmniCapture'
$runtime=@('DuckMooOmniCapture.toc','DuckMooOmniCapture_Camelot.toc','Model.lua','Capture.lua','Life.lua','Extended.lua','Core.lua','USER-GUIDE.txt','README.md','NOTICE.txt','Acknowledgements.lua')
foreach($flavor in @('_retail_','_forever_')) {
 $destination=Join-Path $WowRoot ($flavor+'\Interface\AddOns\DuckMooOmniCapture')
 New-Item -ItemType Directory -Force -Path $destination | Out-Null
 foreach($name in $runtime) {
  $target=Join-Path $destination $name
  if(Test-Path -LiteralPath $target) {
   $saved=Join-Path $backup ($flavor+'\DuckMooOmniCapture');New-Item -ItemType Directory -Force -Path $saved | Out-Null
   Copy-Item -LiteralPath $target -Destination (Join-Path $saved $name)
   if($name -eq 'Acknowledgements.lua') { continue }
  }
  Copy-Item -LiteralPath (Join-Path $source $name) -Destination $target
 }
}
foreach($name in @('collect_sources.py','snapshots.py','bundle.py','write_omni_ack.py','savedvariables.py')) {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('clean-install\app\'+$name)) -Destination (Join-Path $ForeverSync ('app\'+$name))
}
foreach($name in @('Sync-Nexus.ps1','Sync-Helpers.ps1','Run-Hidden.vbs')) {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('clean-install\'+$name)) -Destination (Join-Path $ForeverSync $name)
}
$configPath=Join-Path $ForeverSync 'config.json'
if(Test-Path -LiteralPath $configPath) {
 $config=Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
 if($config.Namespace -ne 'forever-main-account') { throw 'Existing destination belongs to another channel' }
} else {
 $config=$base
 $config.SavedVariables=$sv;$config.TsmAppData=$null
 $config | Add-Member -NotePropertyName Namespace -NotePropertyValue 'forever-main-account'
 $config | Add-Member -NotePropertyName AllowEmpty -NotePropertyValue $true
 $config | Add-Member -NotePropertyName MinimumSavedAt -NotePropertyValue ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())
 $config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
}
$action=New-ScheduledTaskAction -Execute "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ('-WindowStyle Hidden -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+(Join-Path $ForeverSync 'Sync-Nexus.ps1')+'"')
$trigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 5)
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 6) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'DuckMoo Nexus Forever Sync' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host ('Omni 0.2.0 installed for Retail and Forever. Separate hidden Forever sync registered. Backups: '+$backup)
