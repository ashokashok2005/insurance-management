@echo off
echo Starting Insurance Policy Manager...
echo.

:: 1. Navigate to project folder (ensure we are in the right place)
cd /d "%~dp0"

:: 2. Start the python server in the background
start "Insurance App Server" cmd /k "python run.py"

:: 3. Wait a few seconds for server to boot
timeout /t 3 /nobreak >nul

:: 4. Open the browser
start http://127.0.0.1:5000

echo.
echo App started! You can close this window, but keep the "Insurance App Server" window open.
pause
