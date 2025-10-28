@echo off
setlocal enabledelayedexpansion

REM ================================================================
REM AI Environment Path Finder
REM Searches all drives for AI_Environment installation
REM ================================================================

set "FOUND_PATH="

REM Search for AI_Lab\AI_Environment first (external drives)
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Lab\AI_Environment" (
        if exist "%%D:\AI_Lab\AI_Environment\Ollama\ollama.exe" (
            set "FOUND_PATH=%%D:\AI_Lab\AI_Environment"
            goto :found
        )
    )
)

REM Search for root AI_Environment (internal drives)
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\AI_Environment" (
        if exist "%%D:\AI_Environment\Ollama\ollama.exe" (
            set "FOUND_PATH=%%D:\AI_Environment"
            goto :found
        )
    )
)

:not_found
echo AI_Environment not found on any drive
exit /b 1

:found
echo %FOUND_PATH%
exit /b 0
