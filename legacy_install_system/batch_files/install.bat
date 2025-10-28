@echo off
setlocal enabledelayedexpansion
title AI Environment Installer

REM Initialize variables
set "START_STEP="
set "SHOW_HELP="
set "SHOW_STATUS="

REM Simple argument parsing
if "%1"=="--help" set "SHOW_HELP=1"
if "%1"=="-h" set "SHOW_HELP=1"
if "%1"=="--status" set "SHOW_STATUS=1"
if "%1"=="--step" set "START_STEP=%2"
if "%1"=="-s" set "START_STEP=%2"

REM Show help if requested
if defined SHOW_HELP goto show_help
if "%1"=="--step" if "%2"=="" goto show_help
if "%1"=="-s" if "%2"=="" goto show_help

REM Show status if requested
if defined SHOW_STATUS goto show_status

REM If --step provided, validate step number
if defined START_STEP (
    if !START_STEP! lss 1 goto invalid_step
    if !START_STEP! gtr 8 goto invalid_step
)

REM Continue to main installation
goto main_install

:show_help
echo.
echo ================================================================
echo                   AI Environment Installer
echo                    Command Line Options
echo ================================================================
echo.
echo Usage: install.bat [options]
echo.
echo Options:
echo   --step N, -s N     Start installation from step N (1-8)
echo   --status           Show current installation status
echo   --help, -h         Show this help message
echo.
echo Installation Steps:
echo   1. Check prerequisites
echo   2. Create directory structure
echo   3. Install Miniconda
echo   4. Create AI2025 environment
echo   5. Install VS Code
echo   6. Install Python packages
echo   7. Install Ollama and LLM models
echo   8. Finalize installation
echo.
echo Examples:
echo   install.bat                    # Start from last failed step
echo   install.bat --step 3           # Start from step 3 (Miniconda)
echo   install.bat --status           # Show installation status
echo.
pause
exit /b 0

:show_status
echo.
echo ================================================================
echo                AI Environment Installation Status
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found. Cannot show detailed status.
    echo.
    echo Basic status check (searching all drives):
    set "FOUND_INSTALL="
    for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        REM Check for AI_Lab\AI_Environment first
        if exist "%%D:\AI_Lab\AI_Environment" (
            echo [OK] AI Environment found at %%D:\AI_Lab\AI_Environment
            if exist "%%D:\AI_Lab\AI_Environment\Miniconda" echo     [OK] Miniconda installed
            if exist "%%D:\AI_Lab\AI_Environment\VSCode" echo     [OK] VS Code installed
            if exist "%%D:\AI_Lab\AI_Environment\Ollama" echo     [OK] Ollama installed
            if exist "%%D:\AI_Lab\AI_Environment\activate_ai_env.bat" echo     [OK] Activation script exists
            set "FOUND_INSTALL=1"
        ) else if exist "%%D:\AI_Environment" (
            echo [OK] AI Environment found at %%D:\AI_Environment
            if exist "%%D:\AI_Environment\Miniconda" echo     [OK] Miniconda installed
            if exist "%%D:\AI_Environment\VSCode" echo     [OK] VS Code installed
            if exist "%%D:\AI_Environment\Ollama" echo     [OK] Ollama installed
            if exist "%%D:\AI_Environment\activate_ai_env.bat" echo     [OK] Activation script exists
            set "FOUND_INSTALL=1"
        )
    )
    if not defined FOUND_INSTALL (
        echo [ERROR] AI Environment not found on any drive
    )
    echo.
    echo For detailed status, ensure Python is installed.
    pause
    exit /b 0
)

REM Run status checker
echo Checking installation status...
echo.
python "%~dp0src\status_checker.py"
echo.
pause
exit /b 0

:invalid_step
echo ERROR: Invalid step number '%START_STEP%'. Must be between 1 and 8.
pause
exit /b 1

:main_install
echo.
echo ================================================================
echo                    AI Environment Installer
echo                     Portable AI Development
echo ================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer must be run as administrator.
    echo Please right-click install.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found.
    echo Please install Python 3.7+ and ensure it's in your PATH.
    echo.
    pause
    exit /b 1
)

REM Run drive selector
echo Analyzing available drives...
echo.
python "%~dp0src\drive_selector.py" > "%TEMP%\selected_drive.txt"
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Drive selection cancelled or failed.
    echo.
    pause
    exit /b 1
)

REM Read selected drive and AI_Lab path from temp file
REM First line is the drive letter, second line is the AI_Lab path (may be empty)
set "LINE_NUM=0"
for /f "usebackq delims=" %%a in ("%TEMP%\selected_drive.txt") do (
    if !LINE_NUM!==0 (
        set "SELECTED_DRIVE=%%a"
    ) else if !LINE_NUM!==1 (
        set "AILAB_PATH=%%a"
    )
    set /a LINE_NUM+=1
)
del "%TEMP%\selected_drive.txt" 2>nul

if not defined SELECTED_DRIVE (
    echo ERROR: No drive was selected.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting AI Environment installation...
echo Target drive: %SELECTED_DRIVE%:

REM Show installation path based on whether AI_Lab folder was found
if defined AILAB_PATH (
    if not "%AILAB_PATH%"=="" (
        echo Installation path: %AILAB_PATH%\AI_Environment
    ) else (
        echo Installation path: %SELECTED_DRIVE%:\AI_Environment
    )
) else (
    echo Installation path: %SELECTED_DRIVE%:\AI_Environment
)
echo.

REM Validate start step parameter
if defined START_STEP (
    echo Starting installation from step !START_STEP!...
    echo.
)

echo Running installation manager...

REM Run the installation manager with selected drive
REM Include --ailab parameter if AILab folder path was found
if defined START_STEP (
    if defined AILAB_PATH (
        if not "%AILAB_PATH%"=="" (
            python "%~dp0src\install_manager.py" --step !START_STEP! --drive %SELECTED_DRIVE% --ailab "%AILAB_PATH%"
        ) else (
            python "%~dp0src\install_manager.py" --step !START_STEP! --drive %SELECTED_DRIVE%
        )
    ) else (
        python "%~dp0src\install_manager.py" --step !START_STEP! --drive %SELECTED_DRIVE%
    )
) else (
    if defined AILAB_PATH (
        if not "%AILAB_PATH%"=="" (
            python "%~dp0src\install_manager.py" --drive %SELECTED_DRIVE% --ailab "%AILAB_PATH%"
        ) else (
            python "%~dp0src\install_manager.py" --drive %SELECTED_DRIVE%
        )
    ) else (
        python "%~dp0src\install_manager.py" --drive %SELECTED_DRIVE%
    )
)

REM Check installation result and save it
set "INSTALL_RESULT=%errorlevel%"

if %INSTALL_RESULT% equ 0 (
    echo.
    echo ================================================================
    echo                   INSTALLATION COMPLETED!
    echo ================================================================
    echo.
    echo The AI Environment has been successfully installed on %SELECTED_DRIVE%: drive.
    echo.
    if defined AILAB_PATH (
        if not "%AILAB_PATH%"=="" (
            echo Installation Location: %AILAB_PATH%\AI_Environment
            echo.
            echo To start using the AI Environment:
            echo 1. Open: %AILAB_PATH%\AI_Environment\activate_ai_env.bat
            echo 2. Or run: install.bat --status ^(to verify installation^)
        ) else (
            echo Installation Location: %SELECTED_DRIVE%:\AI_Environment
            echo.
            echo To start using the AI Environment:
            echo 1. Open: %SELECTED_DRIVE%:\AI_Environment\activate_ai_env.bat
            echo 2. Or run: install.bat --status ^(to verify installation^)
        )
    ) else (
        echo Installation Location: %SELECTED_DRIVE%:\AI_Environment
        echo.
        echo To start using the AI Environment:
        echo 1. Open: %SELECTED_DRIVE%:\AI_Environment\activate_ai_env.bat
        echo 2. Or run: install.bat --status ^(to verify installation^)
    )
    echo.
    echo The environment includes:
    echo - Python 3.10 with conda ^(AI2025 environment^)
    echo - VS Code with AI/ML extensions
    echo - Ollama with local LLM models
    echo - 30+ AI/ML Python packages
    echo - Project templates and examples
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
) else (
    echo.
    echo ================================================================
    echo                   INSTALLATION FAILED!
    echo ================================================================
    echo.
    echo Installation completed with errors.
    echo Please check the log files in the logs folder for details.
    echo.
    echo Common solutions:
    echo - Ensure you have administrator privileges
    echo - Check internet connection
    echo - Verify sufficient disk space on %SELECTED_DRIVE%: drive
    echo - Temporarily disable antivirus software
    echo.
    echo To retry:
    echo - Full retry: install.bat
    echo - From specific step: install.bat --step N
    echo - Check status: install.bat --status
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

