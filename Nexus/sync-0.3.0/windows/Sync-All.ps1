# Preserve the deployed Journalator script and run it first. New sources use the
# same restricted SSH identity, server inbox, worker and database.
$ErrorActionPreference='Stop'
& powershell.exe -NoProfile -NonInteractive -File "$PSScriptRoot\Sync-Journalator.ps1"
$journalatorCode=$LASTEXITCODE
& powershell.exe -NoProfile -NonInteractive -File "$PSScriptRoot\Sync-Sources.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
exit $journalatorCode
