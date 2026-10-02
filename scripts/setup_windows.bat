@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-dev.ps1"
if errorlevel 1 exit /b %errorlevel%
