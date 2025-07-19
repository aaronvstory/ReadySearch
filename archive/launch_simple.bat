@echo off
chcp 65001 >nul 2>&1

REM Simple launcher for ReadySearch automation
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo      READYSEARCH AUTOMATION LAUNCHER
echo ========================================
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory.
    echo Expected: %SCRIPT_DIR%main.py
    pause
    exit /b 1
)

REM Find Python executable
set "PYTHON_EXE="
for %%P in (py python python3) do (
    if not defined PYTHON_EXE (
        %%P --version >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=%%P"
            echo [INFO] Using python: %%P
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

REM Launch application
echo [INFO] Launching ReadySearch automation...
echo ========================================
echo.

"%PYTHON_EXE%" main.py
set "EXIT_CODE=%errorlevel%"

echo.
echo ========================================
if %EXIT_CODE% equ 0 (
    echo      APPLICATION COMPLETED SUCCESSFULLY
) else (
    echo      APPLICATION ERROR (Exit Code: %EXIT_CODE%)
)
echo ========================================
echo.
pause
exit /b %EXIT_CODE%
