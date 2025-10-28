@echo off
REM ================================================================
REM AI Environment Validator v3.0
REM Compatible with MasterInstall.bat system
REM ================================================================

SETLOCAL EnableDelayedExpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "VALIDATOR_SCRIPT=%SCRIPT_DIR%validator\system_validator.py"

REM Clear screen and show header
cls
echo.
echo ================================================================
echo     AI Environment Validator v3.0
echo     Testing MasterInstall.bat Installation
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please ensure Python is installed and accessible
    echo.
    pause
    exit /b 1
)

REM Check if validator script exists
if not exist "%VALIDATOR_SCRIPT%" (
    echo [ERROR] Validator script not found
    echo Expected location: %VALIDATOR_SCRIPT%
    echo.
    pause
    exit /b 1
)

REM Try to find installation path from master_installation_status.json
set "AI_ENV_PATH="
set "STATUS_FILE=%SCRIPT_DIR%master_installation_status.json"

if exist "%STATUS_FILE%" (
    echo [INFO] Reading installation status from master_installation_status.json
    echo.

    REM Use PowerShell to parse JSON
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "try { $json = Get-Content '%STATUS_FILE%' -Raw | ConvertFrom-Json; $path = $json.ai_environment.install_path; if ($path) { Write-Output $path } } catch { }"`) do (
        set "AI_ENV_PATH=%%i"
    )

    if defined AI_ENV_PATH (
        REM Remove quotes if present
        set "AI_ENV_PATH=!AI_ENV_PATH:"=!"

        if exist "!AI_ENV_PATH!" (
            echo [OK] Found AI_Environment at: !AI_ENV_PATH!
            echo.
            goto run_validation
        ) else (
            echo [WARNING] Status file points to non-existent path: !AI_ENV_PATH!
            echo [INFO] Searching for installation...
            echo.
        )
    ) else (
        echo [INFO] No installation path found in status file
        echo [INFO] Searching for installation...
        echo.
    )
)

REM If not found in status file, search common locations
echo [INFO] Searching all drives for AI_Environment installation...
echo.

set "FOUND_COUNT=0"

REM Search for AI_Lab\AI_Environment (External drive mode)
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Lab\AI_Environment\" (
        if !FOUND_COUNT! equ 0 (
            set "AI_ENV_PATH=%%D:\AI_Lab\AI_Environment"
            echo [OK] Found AI_Environment at: !AI_ENV_PATH! ^(External mode^)
            set /a FOUND_COUNT+=1
        ) else (
            echo [INFO] Also found at: %%D:\AI_Lab\AI_Environment ^(External mode^)
            set /a FOUND_COUNT+=1
        )
    )
)

REM Search for standalone AI_Environment (Internal drive mode)
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Environment\" (
        REM Only count if not already found as AI_Lab\AI_Environment
        if not exist "%%D:\AI_Lab\AI_Environment\" (
            if !FOUND_COUNT! equ 0 (
                set "AI_ENV_PATH=%%D:\AI_Environment"
                echo [OK] Found AI_Environment at: !AI_ENV_PATH! ^(Internal mode^)
                set /a FOUND_COUNT+=1
            ) else (
                echo [INFO] Also found at: %%D:\AI_Environment ^(Internal mode^)
                set /a FOUND_COUNT+=1
            )
        )
    )
)

if !FOUND_COUNT! equ 0 (
    echo.
    echo [ERROR] No AI_Environment installation found
    echo.
    echo Searched locations:
    echo   - [Drive]:\AI_Lab\AI_Environment  ^(External drive mode^)
    echo   - [Drive]:\AI_Environment          ^(Internal drive mode^)
    echo.
    echo Please run MasterInstall.bat first to install AI_Environment
    echo.
    pause
    exit /b 1
)

if !FOUND_COUNT! gtr 1 (
    echo.
    echo [WARNING] Multiple installations found
    echo [INFO] Validating the first one: !AI_ENV_PATH!
    echo.
)

:run_validation
echo ================================================================
echo Starting Validation
echo ================================================================
echo.
echo Installation Path: !AI_ENV_PATH!
echo.
echo Running comprehensive validation tests...
echo.

REM Set UTF-8 encoding to handle Unicode characters in Python script
chcp 65001 >nul 2>&1

REM Run the validator
python "%VALIDATOR_SCRIPT%" "!AI_ENV_PATH!"

REM Capture exit code
set "RESULT=%errorlevel%"

REM Restore default code page
chcp 437 >nul 2>&1

echo.
echo ================================================================
if %RESULT% equ 0 (
    echo     VALIDATION PASSED
    echo ================================================================
    echo.
    echo All components are functioning correctly
) else (
    echo     VALIDATION COMPLETED WITH ISSUES
    echo ================================================================
    echo.
    echo Please review the validation output above for details
    echo Check logs in: !AI_ENV_PATH!\Logs\
)
echo.

REM Show where validation report was saved
if exist "!AI_ENV_PATH!\validation_report.json" (
    echo Validation report saved to: !AI_ENV_PATH!\validation_report.json
    echo.
)

pause
exit /b %RESULT%
