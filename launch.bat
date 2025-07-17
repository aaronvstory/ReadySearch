@echo off
title ReadySearch - Advanced Launcher
chcp 65001 >nul 2>&1

REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo     READYSEARCH ADVANCED LAUNCHER
echo ========================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell available'" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell not found or not accessible.
    echo [INFO] This launcher requires PowerShell to run.
    echo [INFO] Please ensure PowerShell is installed and accessible.
    pause
    exit /b 1
)

echo [INFO] Starting PowerShell Advanced Launcher...
echo.

REM Launch the PowerShell script with execution policy bypass
powershell -ExecutionPolicy Bypass -File "%~dp0launcher.ps1"

REM Capture exit code
set "EXIT_CODE=%errorlevel%"

echo.
echo ========================================
if %EXIT_CODE% equ 0 (
    echo      LAUNCHER COMPLETED SUCCESSFULLY
) else (
    echo      LAUNCHER ERROR (Exit Code: %EXIT_CODE%)
)
echo ========================================
echo.
pause
exit /b %EXIT_CODE%
