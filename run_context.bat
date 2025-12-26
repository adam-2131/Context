@echo off
REM Context Assistant Launcher for Windows
REM This script launches the Context GUI application

echo Starting Context Assistant...
echo.
echo Note: If global hotkey (Ctrl+Shift+X) doesn't work, you may need to run as Administrator.
echo.

python context_gui.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start Context Assistant
    echo Make sure Python is installed and dependencies are installed:
    echo   pip install -r requirements.txt
    pause
)

