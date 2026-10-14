Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  AeroVision-AI: Touchless Vision Workspace" -ForegroundColor Yellow
Write-Host "  Author: Suprabha Regmi (suprabha080)" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

$pyPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pyPath) {
    $fallback = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    if (Test-Path $fallback) {
        $pyPath = $fallback
    } else {
        Write-Error "Python 3.10+ not found. Please install Python and ensure it is in PATH."
        exit 1
    }
}

Write-Host "Launching with: $pyPath" -ForegroundColor DarkGray
& $pyPath main.py
