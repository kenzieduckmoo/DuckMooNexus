#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Server = '10.20.30.239',
    [string]$AdminUser = 'kenzieduckmoo',
    [string]$SavedVariables,
    [string]$TsmAppData,
    [string]$AdminIdentity,
    [string]$HistoricalSnapshots,
    [string]$Python = 'python',
    [string]$InstallPath = "$env:LOCALAPPDATA\DuckMooNexusClean"
)
$ErrorActionPreference = 'Stop'
if ($Server -notmatch '^[a-zA-Z0-9.-]+$' -or $AdminUser -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Invalid SSH server/user' }
$release = $PSScriptRoot
if (-not $SavedVariables) {
    $roots = @('C:\Program Files (x86)\World of Warcraft','C:\Program Files\World of Warcraft','D:\World of Warcraft','E:\World of Warcraft')
    $matches = @($roots | ForEach-Object { Get-ChildItem -Path (Join-Path $_ '_retail_\WTF\Account\*\SavedVariables') -Directory -ErrorAction SilentlyContinue } |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'Journalator.lua') })
    if ($matches.Count -eq 1) { $SavedVariables = $matches[0].FullName }
    else { throw 'Supply -SavedVariables with your account SavedVariables directory.' }
}
$SavedVariables = (Resolve-Path -LiteralPath $SavedVariables).Path
if (-not $TsmAppData) {
    $client = Split-Path (Split-Path (Split-Path (Split-Path $SavedVariables)))
    $candidate = Join-Path $client 'Interface\AddOns\TradeSkillMaster_AppHelper\AppData.lua'
    if (Test-Path -LiteralPath $candidate) { $TsmAppData = $candidate }
}
$pythonPath = (Get-Command $Python -ErrorAction Stop).Source
& $pythonPath -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11 or later is required'"
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required' }
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
$InstallPath = (Resolve-Path -LiteralPath $InstallPath).Path
if ($InstallPath -eq $release) { throw 'Extract the release outside the installed sync directory' }
# Only this release's files are replaced; retained archives/state are never deleted.
Copy-Item -Path (Join-Path $release '*') -Destination $InstallPath -Recurse -Force
foreach ($taskName in 'DuckMoo Nexus Journalator Sync','DuckMoo Nexus Additional Sources','DuckMoo Nexus Sync') {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
}
$key = Join-Path $InstallPath 'sync-key'
if (-not (Test-Path -LiteralPath $key)) {
    # Windows PowerShell drops empty native arguments; explicit quoted empty string is required.
    & ssh-keygen.exe -q -t ed25519 -N '""' -f $key
    if ($LASTEXITCODE -ne 0) { throw 'SSH key generation failed' }
}
$adminArgs = @('-o','StrictHostKeyChecking=accept-new')
if ($AdminIdentity) { $adminArgs += @('-o','IdentitiesOnly=yes','-i',(Resolve-Path -LiteralPath $AdminIdentity).Path) }
else { $adminArgs += @('-o','PubkeyAuthentication=no') }
$destination = "$AdminUser@$Server"
$remote = 'duckmoo-nexus-clean-upload'
& ssh.exe @adminArgs $destination "mkdir -p ~/$remote"
if ($LASTEXITCODE -ne 0) { throw 'Admin SSH connection failed' }
$archive = Join-Path $InstallPath 'server-release.tar'
& tar.exe -cf $archive -C $InstallPath app provisioning compose.yaml receiver.py install-server.sh verify-server.py sync-key.pub
if ($LASTEXITCODE -ne 0) { throw 'Server package creation failed' }
& scp.exe @adminArgs $archive "${destination}:$remote/release.tar"
if ($LASTEXITCODE -ne 0) { throw 'Release transfer failed' }
& ssh.exe -t @adminArgs $destination "cd ~/$remote && tar -xf release.tar && sudo bash install-server.sh"
if ($LASTEXITCODE -ne 0) { throw 'Server installation failed' }
$knownHosts = Join-Path $env:USERPROFILE '.ssh\known_hosts'
@{
    HostName=$Server; UserName='duckmoo-nexus-sync'; IdentityFile=$key; KnownHostsFile=$knownHosts
    SavedVariables=$SavedVariables; TsmAppData=$TsmAppData; Python=$pythonPath
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $InstallPath 'config.json') -Encoding UTF8
if ($HistoricalSnapshots) {
    & $pythonPath (Join-Path $InstallPath 'app\queue_history.py') $HistoricalSnapshots (Join-Path $InstallPath 'state\packets')
    if ($LASTEXITCODE -ne 0) { throw 'Historical snapshot queueing failed' }
}
& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $InstallPath 'Sync-Nexus.ps1')
if ($LASTEXITCODE -ne 0) { throw "Initial ingestion failed. See $InstallPath\state\sync.log" }
& ssh.exe -t @adminArgs $destination 'sudo python3 /opt/duckmoo-nexus-clean/verify-server.py'
if ($LASTEXITCODE -ne 0) { throw 'Database/dashboard verification failed' }
# WScript starts PowerShell with no console and propagates its real exit status.
$action = New-ScheduledTaskAction -Execute "$env:WINDIR\System32\wscript.exe" -Argument ('//B //Nologo "' + (Join-Path $InstallPath 'Run-Hidden.vbs') + '"') -WorkingDirectory $InstallPath
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 5)
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 6) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'DuckMoo Nexus Sync' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host "Installed and verified. Grafana: http://${Server}:3000"
Write-Host "Invisible sync every five minutes while signed in. Failures: $InstallPath\state\last-result.json and Task Scheduler Last Run Result."
