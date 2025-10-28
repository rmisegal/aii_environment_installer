@echo off
title AI Environment Status Updater

echo.
echo ================================================================
echo                AI Environment Status Updater
echo                  Detect and Update Installation State
echo ================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This tool must be run as administrator.
    echo Please right-click update_status.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found.
    echo Please ensure Python is installed and in your PATH.
    echo.
    pause
    exit /b 1
)

REM Run status updater
echo Running status detection and update...
echo.
python "%~dp0src\status_updater.py"

echo.
echo Press any key to exit...
pause >nul
exit /b 0

