@echo off
echo.
echo 🤖 BRINGING JARVIS ONLINE...
echo.

:: Check for dependencies
set /p response="Would you like to install/update dependencies first? (y/n) [default: n]: "
if /i "%response%"=="y" (
    echo [SYSTEM] Running setup...
    python setup.py
)

:: Run JARVIS
echo [SYSTEM] Launching main session...
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: JARVIS session ended unexpectedly.
    pause
)
