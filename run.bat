@echo off
title AeroVision AI - Launching
echo ===================================================
echo   AeroVision-AI: Touchless Vision Workspace
echo   Author: Suprabha Regmi (suprabha080)
echo ===================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found in system PATH. Attempting Local AppData Python...
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" main.py
        goto end
    )
    echo Error: Please install Python 3.10+ and add it to your system PATH.
    pause
    exit /b 1
)

python main.py

:end
pause
