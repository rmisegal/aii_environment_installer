@echo off
setlocal enabledelayedexpansion
title AI Environment Uninstaller v2.0 - Automated

:: ================================================================
::                   AI Environment Uninstaller v2.0
::          Automated Path Detection & Smart Cleanup
:: ================================================================

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ================================================================
    echo ERROR: Administrator privileges required
    echo ================================================================
    echo.
    echo This uninstaller must be run as administrator to remove all components.
    echo Please right-click uninstall.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Display header
echo.
echo ================================================================
echo            AI Environment Uninstaller v2.0
echo          Automated Detection ^& Smart Cleanup
echo ================================================================
echo.

:: Parse command line arguments
set "AUTO_MODE="
set "DRY_RUN="
set "KEEP_PROJECTS="
set "DELETE_PROJECTS="
set "BACKUP="
set "LIST_ONLY="
set "SPECIFIC_PATH="
set "SHOW_HELP="

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--auto" (
    set "AUTO_MODE=--auto"
    shift
    goto parse_args
)
if /i "%~1"=="--dry-run" (
    set "DRY_RUN=--dry-run"
    shift
    goto parse_args
)
if /i "%~1"=="--keep-projects" (
    set "KEEP_PROJECTS=--keep-projects"
    shift
    goto parse_args
)
if /i "%~1"=="--delete-projects" (
    set "DELETE_PROJECTS=--delete-projects"
    shift
    goto parse_args
)
if /i "%~1"=="--backup" (
    set "BACKUP=--backup"
    shift
    goto parse_args
)
if /i "%~1"=="--list" (
    set "LIST_ONLY=--list"
    shift
    goto parse_args
)
if /i "%~1"=="--path" (
    set "SPECIFIC_PATH=--path %~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    set "SHOW_HELP=1"
    shift
    goto parse_args
)
if /i "%~1"=="-h" (
    set "SHOW_HELP=1"
    shift
    goto parse_args
)
shift
goto parse_args

:args_done

:: Show help if requested
if defined SHOW_HELP (
    echo.
    echo ================================================================
    echo                   AI Environment Uninstaller
    echo                      Command Line Options
    echo ================================================================
    echo.
    echo Usage: uninstall.bat [options]
    echo.
    echo Options:
    echo   --auto                  Fully automated mode ^(no prompts^)
    echo   --dry-run               Preview what would be deleted without removing
    echo   --keep-projects         Keep user projects in Projects/ folder
    echo   --delete-projects       Delete user projects ^(default behavior^)
    echo   --backup                Create backup before uninstall
    echo   --list                  List all detected installations
    echo   --path ^<path^>           Specify installation path manually
    echo   --help, -h              Show this help message
    echo.
    echo Examples:
    echo   uninstall.bat                        # Interactive uninstall
    echo   uninstall.bat --auto                 # Fully automated
    echo   uninstall.bat --dry-run              # Preview only
    echo   uninstall.bat --auto --backup        # Auto with backup
    echo   uninstall.bat --list                 # Show installations
    echo   uninstall.bat --path "E:\AI_Environment"  # Specific path
    echo.
    echo Features:
    echo   - Automatic path detection across all drives
    echo   - Detects both internal and external drive installations
    echo   - Supports AI_Lab\AI_Environment ^(external^) and Drive:\AI_Environment ^(internal^)
    echo   - Complete cleanup ^(removes all installed files^)
    echo   - Preserves pre-existing Conda installations
    echo   - Deletes everything by default ^(use --keep-projects to preserve^)
    echo   - Optional backup before deletion
    echo.
    pause
    exit /b 0
)

:: Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ================================================================
    echo ERROR: Python is not available
    echo ================================================================
    echo.
    echo The automated uninstaller requires Python to run.
    echo.
    echo Falling back to basic manual uninstall...
    echo.
    pause
    goto manual_uninstall
)

:: Run the automated uninstaller
echo Starting automated uninstaller...
echo.

python "%~dp0src\automated_uninstaller.py" %AUTO_MODE% %DRY_RUN% %KEEP_PROJECTS% %DELETE_PROJECTS% %BACKUP% %LIST_ONLY% %SPECIFIC_PATH%

set "RESULT=%errorlevel%"

if %RESULT% equ 0 (
    echo.
    echo ================================================================
    echo                 UNINSTALL COMPLETED SUCCESSFULLY
    echo ================================================================
    echo.
    if defined DRY_RUN (
        echo Dry run complete - no files were deleted.
        echo Run without --dry-run to perform actual uninstall.
    ) else if defined LIST_ONLY (
        echo Installation listing complete.
    ) else (
        echo AI Environment has been successfully uninstalled.
        echo.
        echo To reinstall:
        echo   1. Run install.bat from the installer package
        echo   2. Follow the installation prompts
    )
    echo.
) else if %RESULT% equ 1 (
    echo.
    echo ================================================================
    echo                    UNINSTALL STATUS
    echo ================================================================
    echo.
    echo Check the output above for details.
    echo.
    if defined LIST_ONLY (
        echo No installations were found on this system.
        echo The system is clean - nothing to uninstall.
    ) else (
        echo Some components may not have been removed completely.
        echo Check the log files in: %~dp0logs\
    )
    echo.
) else (
    echo.
    echo ================================================================
    echo              UNINSTALL COMPLETED WITH ERRORS
    echo ================================================================
    echo.
    echo An unexpected error occurred during uninstall.
    echo Check the log files in: %~dp0logs\
    echo.
)

echo.
pause
exit /b %RESULT%

:: ================================================================
:: Manual Uninstall Fallback (if Python not available)
:: ================================================================
:manual_uninstall

echo.
echo ================================================================
echo              MANUAL UNINSTALL MODE
echo           (Python not available for automation)
echo ================================================================
echo.

:: Search all available drives for AI_Environment
echo Scanning all drives for AI_Environment installations...
echo.

set "FOUND="
set "FOUND_COUNT=0"

REM Check for external drive installations first (AI_Lab\AI_Environment)
for %%D in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Lab\AI_Environment" (
        echo Found installation at %%D:\AI_Lab\AI_Environment ^(external drive^)
        set "FOUND_!FOUND_COUNT!=%%D:\AI_Lab\AI_Environment"
        set /a FOUND_COUNT+=1
    )
)

REM Check for internal drive installations (root AI_Environment)
for %%D in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Environment" (
        REM Only add if not already found in AI_Lab
        if not exist "%%D:\AI_Lab\AI_Environment" (
            echo Found installation at %%D:\AI_Environment ^(internal drive^)
            set "FOUND_!FOUND_COUNT!=%%D:\AI_Environment"
            set /a FOUND_COUNT+=1
        )
    )
)

if %FOUND_COUNT%==0 (
    echo No AI Environment installations found on any drive.
    echo Nothing to uninstall.
    echo.
    pause
    exit /b 0
)

REM If multiple installations found, let user choose
if %FOUND_COUNT% gtr 1 (
    echo.
    echo Multiple installations found:
    echo.
    for /L %%i in (0,1,!FOUND_COUNT!) do (
        if defined FOUND_%%i (
            set /a "DISPLAY_NUM=%%i+1"
            echo !DISPLAY_NUM!. !FOUND_%%i!
        )
    )
    echo.
    set /p "CHOICE=Select installation to uninstall (1-%FOUND_COUNT%): "
    set /a "INDEX=!CHOICE!-1"
    set "FOUND=!FOUND_%INDEX%!"
) else (
    set "FOUND=!FOUND_0!"
)

echo.
echo Found AI Environment at: !FOUND!
echo.
echo WARNING: This will completely remove the AI Environment installation.
echo All files will be permanently deleted.
echo.
echo This includes:
echo - Miniconda and Python environment
echo - VS Code portable
echo - Ollama and all AI models
echo - User projects and data
echo - Configuration files
echo.

set /p "confirm=Are you sure you want to continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo.
    echo Uninstall cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo Starting manual uninstallation...
echo.

:: Stop running processes
echo Stopping AI Environment processes...
taskkill /f /im ollama.exe >nul 2>&1
taskkill /f /im Code.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im conda.exe >nul 2>&1
taskkill /f /im jupyter.exe >nul 2>&1
echo Processes stopped.
echo.

:: Wait for processes to terminate
timeout /t 3 /nobreak >nul

:: Remove the directory
echo Removing !FOUND!...
rmdir /s /q "!FOUND!" 2>nul

if exist "!FOUND!" (
    echo.
    echo WARNING: Some files could not be removed.
    echo They may be in use by running processes.
    echo Please close all AI Environment applications and try again.
    echo.
) else (
    echo.
    echo AI Environment successfully removed!
    echo.
)

:: Check for AllUsers Miniconda
if exist "C:\ProgramData\miniconda3" (
    echo.
    echo Found Miniconda at C:\ProgramData\miniconda3
    set /p "remove_conda=Remove it? (y/N): "
    if /i "!remove_conda!"=="y" (
        echo Removing Miniconda...
        rmdir /s /q "C:\ProgramData\miniconda3" 2>nul
        if not exist "C:\ProgramData\miniconda3" (
            echo Miniconda removed successfully!
        ) else (
            echo WARNING: Could not remove Miniconda completely.
        )
    ) else (
        echo Skipping Miniconda removal.
    )
)

echo.
echo ================================================================
echo                    MANUAL UNINSTALL COMPLETED
echo ================================================================
echo.
pause
exit /b 0
