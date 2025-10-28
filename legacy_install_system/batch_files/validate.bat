@echo off
title AI Environment Validator

echo.
echo ================================================================
echo                    AI Environment Validator                    
echo                     Comprehensive Testing                      
echo ================================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as administrator
    echo Some tests may not work properly.
    echo.
    pause
)

:: Try to get installation path from saved installation status
set "AI_ENV_PATH="
set "STATUS_FILE=%~dp0installation_status.json"
set "TEMP_PATH_FILE=%TEMP%\ai_env_path.txt"

if exist "%STATUS_FILE%" (
    echo Reading installation path from: %STATUS_FILE%
    REM Use PowerShell to parse JSON and write to temp file (more reliable than for /f)
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $json = Get-Content '%STATUS_FILE%' -Raw | ConvertFrom-Json; $json.installation_path | Out-File -FilePath '%TEMP_PATH_FILE%' -Encoding ASCII -NoNewline } catch { }" >nul 2>&1

    REM Read from temp file
    if exist "%TEMP_PATH_FILE%" (
        set /p AI_ENV_PATH=<"%TEMP_PATH_FILE%"
        del "%TEMP_PATH_FILE%" 2>nul
    )
)

REM If we got a path from the status file, verify it exists
if defined AI_ENV_PATH (
    REM Remove quotes if present
    set "AI_ENV_PATH=%AI_ENV_PATH:"=%"

    if exist "%AI_ENV_PATH%" (
        echo Found AI Environment from installation record.
        goto found_env
    ) else (
        echo WARNING: Installation path from record does not exist: %AI_ENV_PATH%
        echo Searching all drives...
        set "AI_ENV_PATH="
    )
)

REM Fallback: Search for AI Environment on all drives if not found in status
if not defined AI_ENV_PATH (
    echo No installation record found. Searching all drives...
    for %%D in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        REM Check for AI_Lab\AI_Environment first
        if exist "%%D:\AI_Lab\AI_Environment" (
            set "AI_ENV_PATH=%%D:\AI_Lab\AI_Environment"
            goto found_env
        )
        REM Then check root AI_Environment
        if exist "%%D:\AI_Environment" (
            set "AI_ENV_PATH=%%D:\AI_Environment"
            goto found_env
        )
    )
)

:found_env
if not defined AI_ENV_PATH (
    echo ERROR: AI Environment not found
    echo Please run the installer first.
    echo.
    pause
    exit /b 1
)

echo Found AI Environment at: %AI_ENV_PATH%
echo.

:: Set paths
set "VALIDATOR_PATH=%~dp0validator\system_validator.py"

:: Detect Python location dynamically from installation status
set "PYTHON_PATH="
set "PYTHON_LOCATION="
set "CONDA_ALLUSERS_PATH="
set "CONDA_PORTABLE_PATH="

REM Try to get conda paths from installation status JSON using temp files
if exist "%STATUS_FILE%" (
    set "TEMP_CONDA_ALLUSERS=%TEMP%\conda_allusers.txt"
    set "TEMP_CONDA_PORTABLE=%TEMP%\conda_portable.txt"

    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $json = Get-Content '%STATUS_FILE%' -Raw | ConvertFrom-Json; $json.pre_install_state.conda_installations.allusers_path | Out-File -FilePath '%TEMP%\conda_allusers.txt' -Encoding ASCII -NoNewline } catch { }" >nul 2>&1
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $json = Get-Content '%STATUS_FILE%' -Raw | ConvertFrom-Json; $json.pre_install_state.conda_installations.portable_path | Out-File -FilePath '%TEMP%\conda_portable.txt' -Encoding ASCII -NoNewline } catch { }" >nul 2>&1

    if exist "!TEMP_CONDA_ALLUSERS!" (
        set /p CONDA_ALLUSERS_PATH=<"!TEMP_CONDA_ALLUSERS!"
        del "!TEMP_CONDA_ALLUSERS!" 2>nul
    )

    if exist "!TEMP_CONDA_PORTABLE!" (
        set /p CONDA_PORTABLE_PATH=<"!TEMP_CONDA_PORTABLE!"
        del "!TEMP_CONDA_PORTABLE!" 2>nul
    )
)

REM Check portable conda from JSON first (if available)
if defined CONDA_PORTABLE_PATH (
    if not "%CONDA_PORTABLE_PATH%"=="null" (
        if exist "%CONDA_PORTABLE_PATH%\envs\AI2025\python.exe" (
            set "PYTHON_PATH=%CONDA_PORTABLE_PATH%\envs\AI2025\python.exe"
            set "PYTHON_LOCATION=Portable ^(from installation record^)"
            goto python_found
        )
    )
)

REM Check system/AllUsers conda from JSON
if defined CONDA_ALLUSERS_PATH (
    if not "%CONDA_ALLUSERS_PATH%"=="null" (
        if exist "%CONDA_ALLUSERS_PATH%\envs\AI2025\python.exe" (
            set "PYTHON_PATH=%CONDA_ALLUSERS_PATH%\envs\AI2025\python.exe"
            set "PYTHON_LOCATION=System ^(from installation record^)"
            goto python_found
        )
    )
)

REM Check portable location in AI_Environment directory structure
if exist "%AI_ENV_PATH%\Miniconda\envs\AI2025\python.exe" (
    set "PYTHON_PATH=%AI_ENV_PATH%\Miniconda\envs\AI2025\python.exe"
    set "PYTHON_LOCATION=Portable ^(in AI_Environment^)"
    goto python_found
)

REM Fallback: Check common conda locations
if exist "C:\ProgramData\miniconda3\envs\AI2025\python.exe" (
    set "PYTHON_PATH=C:\ProgramData\miniconda3\envs\AI2025\python.exe"
    set "PYTHON_LOCATION=System ^(C:\ProgramData\miniconda3^)"
    goto python_found
)

if exist "%USERPROFILE%\miniconda3\envs\AI2025\python.exe" (
    set "PYTHON_PATH=%USERPROFILE%\miniconda3\envs\AI2025\python.exe"
    set "PYTHON_LOCATION=User Profile"
    goto python_found
)

if exist "%LOCALAPPDATA%\miniconda3\envs\AI2025\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\miniconda3\envs\AI2025\python.exe"
    set "PYTHON_LOCATION=Local AppData"
    goto python_found
)

REM Last resort: Try to find conda in PATH and ask it
where conda >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE_PATH=%%i"
    if defined CONDA_BASE_PATH (
        if exist "!CONDA_BASE_PATH!\envs\AI2025\python.exe" (
            set "PYTHON_PATH=!CONDA_BASE_PATH!\envs\AI2025\python.exe"
            set "PYTHON_LOCATION=System ^(found via conda^)"
            goto python_found
        )
    )
)

REM Python not found anywhere
echo ERROR: Python not found in conda environment AI2025
echo.
echo Searched locations:
if defined CONDA_BASE_PATH echo   - %CONDA_BASE_PATH%\envs\AI2025\python.exe ^(from installation record^)
echo   - %AI_ENV_PATH%\Miniconda\envs\AI2025\python.exe ^(portable^)
echo   - C:\ProgramData\miniconda3\envs\AI2025\python.exe
echo   - %USERPROFILE%\miniconda3\envs\AI2025\python.exe
echo   - %LOCALAPPDATA%\miniconda3\envs\AI2025\python.exe
echo.
echo Please ensure the AI2025 conda environment is installed.
echo.
pause
exit /b 1

:python_found

echo Using Python from %PYTHON_LOCATION% installation: %PYTHON_PATH%
echo.

echo Starting AI Environment validation...
echo.

:: Run the validator with AI_ENV_PATH as argument
"%PYTHON_PATH%" "%VALIDATOR_PATH%" "%AI_ENV_PATH%"

set "VALIDATION_RESULT=%ERRORLEVEL%"

echo.
if %VALIDATION_RESULT% equ 0 (
    echo ================================================================
    echo                 VALIDATION COMPLETED SUCCESSFULLY!            
    echo ================================================================
    echo All systems are operational.
) else (
    echo ================================================================
    echo                 VALIDATION COMPLETED WITH ISSUES              
    echo ================================================================
    echo Please check the validation report for details.
)

echo.
echo Validation report saved to: %AI_ENV_PATH%\validation_report.json
echo Detailed logs available in: %AI_ENV_PATH%\Logs\
echo.

pause
exit /b %VALIDATION_RESULT%

