param([switch]$Local)
if ($Local) {
    Set-Location -LiteralPath $PSScriptRoot
    python server.py
} else {
    Start-Process 'http://10.20.30.239/crafting'
}
