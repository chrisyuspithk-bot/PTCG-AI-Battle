@echo off
REM Fetch official kiyotah rule samples (needs .kaggle\kaggle.json).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fetch_official_rule_samples.ps1"
exit /b %ERRORLEVEL%
