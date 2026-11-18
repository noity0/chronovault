@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.12+ install karein: https://www.python.org/downloads/
  pause
  exit /b 1
)
echo ChronoVault 2.0 shuru ho raha hai...
echo Browser: http://127.0.0.1:8765
python chrono.py cockpit %*
endlocal
