@echo off
REM ================================================================
REM AI Environment & Lab Master Installer
REM Version 3.0.28
REM ================================================================

SETLOCAL EnableDelayedExpansion

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Not running as administrator
    echo Some operations may fail without admin privileges
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit
    pause >nul
)

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
if not exist "%SRC_DIR%\master_installer.py" (
    echo.
    echo [ERROR] Installation files are missing
    echo Expected location: %SRC_DIR%\master_installer.py
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
echo     AI Environment ^& Lab Master Installer
echo     Version 3.0.28
echo ================================================================
echo.

REM Run the master installer Python script
echo Starting master installer...
echo.

python "%SRC_DIR%\master_installer.py"

REM Capture exit code
set "EXIT_CODE=%errorlevel%"

REM Show result
echo.
if %EXIT_CODE% equ 0 (
    echo.
    echo ================================================================
    echo     Installation process completed
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo     Installation process ended with errors
    echo     Exit code: %EXIT_CODE%
    echo ================================================================
)

echo.
pause

exit /b %EXIT_CODE%
