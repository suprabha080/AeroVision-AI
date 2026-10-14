@echo off
title AeroVision-AI - Push to GitHub
echo =========================================================
echo   Pushing AeroVision-AI to https://github.com/suprabha080
echo =========================================================
echo.

echo 1. Checking remote URL...
git remote -v
echo.

echo 2. Pushing main branch to origin...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =========================================================
    echo   SUCCESS! AeroVision-AI is live on GitHub:
    echo   https://github.com/suprabha080/AeroVision-AI
    echo =========================================================
) else (
    echo.
    echo ---------------------------------------------------------
    echo Notice: If you have not created the repository on GitHub yet:
    echo 1. Go to: https://github.com/new
    echo 2. Repository name: AeroVision-AI
    echo 3. Click "Create repository" (leave checkboxes unchecked)
    echo 4. Run this push_to_github.bat script again!
    echo ---------------------------------------------------------
)

pause
