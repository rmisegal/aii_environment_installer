@echo off
REM ================================================================
REM AI Environment & Lab Master Uninstaller
REM Version 3.0.28
REM ================================================================

SETLOCAL EnableDelayedExpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SRC_DIR=%SCRIPT_DIR%src"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if required Python modules exist
if not exist "%SRC_DIR%\automated_uninstaller.py" (
    echo.
    echo [ERROR] Uninstaller files are missing
    echo Expected location: %SRC_DIR%\automated_uninstaller.py
    echo.
    echo Please ensure you have all files from the installer package
    echo.
    pause
    exit /b 1
)

REM Clear screen and show header
cls
echo.
echo ================================================================
echo     AI Environment ^& Lab Master Uninstaller
echo     Version 3.0.28
echo ================================================================
echo.
echo This tool will help you uninstall AI_Environment and/or AI_Lab
echo.
echo IMPORTANT: This will permanently delete installed components
echo.
pause

REM Run the automated uninstaller Python script
echo.
echo Starting uninstaller...
echo.

python "%SRC_DIR%\automated_uninstaller.py"

REM Capture exit code
set "EXIT_CODE=%errorlevel%"

REM Show result
echo.
if %EXIT_CODE% equ 0 (
    echo.
    echo ================================================================
    echo     Uninstall process completed successfully
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo     Uninstall process ended with errors or was cancelled
    echo     Exit code: %EXIT_CODE%
    echo ================================================================
)

echo.
pause

exit /b %EXIT_CODE%
