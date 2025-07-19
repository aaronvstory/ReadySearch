@echo off
chcp 65001 >nul 2>&1

REM Enhanced launcher for ReadySearch automation
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo      READYSEARCH AUTOMATION LAUNCHER  
echo ========================================
echo.

REM Check Python
set "PYTHON_EXE="
for %%P in (py python python3) do (
    if not defined PYTHON_EXE (
        %%P --version >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=%%P"
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check main components
if not exist "main.py" (
    echo [ERROR] main.py not found
    pause
    exit /b 1
)

if not exist "api.py" (
    echo [ERROR] api.py not found
    pause
    exit /b 1
)

if not exist "input_names.csv" (
    echo [ERROR] input_names.csv not found
    echo Please create this file with names to search
    pause
    exit /b 1
)

echo [INFO] ✅ Python found: %PYTHON_EXE%
echo [INFO] ✅ All required files present
echo.

REM Show options
echo Select an option:
echo   1. Run Python automation (command line)
echo   2. Start API server for web interface
echo   3. Build web frontend
echo   4. Run comprehensive tests
echo   5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto run_automation
if "%choice%"=="2" goto start_api
if "%choice%"=="3" goto build_frontend
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto exit
goto invalid_choice

:run_automation
echo.
echo ========================================
echo      RUNNING PYTHON AUTOMATION
echo ========================================
echo.
"%PYTHON_EXE%" main.py
goto end

:start_api
echo.
echo ========================================
echo      STARTING API SERVER
echo ========================================
echo.
echo API will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
"%PYTHON_EXE%" api.py
goto end

:build_frontend
echo.
echo ========================================
echo      BUILDING WEB FRONTEND
echo ========================================
echo.
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found. Please install Node.js
    pause
    exit /b 1
)
npm run build
echo.
echo ✅ Frontend built successfully!
echo Files are in the 'dist' folder
goto end

:run_tests
echo.
echo ========================================
echo      RUNNING COMPREHENSIVE TESTS
echo ========================================
echo.
"%PYTHON_EXE%" test_project.py
goto end

:invalid_choice
echo.
echo [ERROR] Invalid choice. Please enter 1-5.
echo.
pause
goto end

:exit
echo.
echo Goodbye!
goto end

:end
echo.
echo ========================================
echo.
pause
