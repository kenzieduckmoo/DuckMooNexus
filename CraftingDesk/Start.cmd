@echo off
cd /d "%~dp0"
if /I "%~1"=="--local" (
  python server.py
) else (
  start "" "http://10.20.30.239/crafting"
)
