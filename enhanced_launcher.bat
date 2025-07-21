@echo off
setlocal EnableDelayedExpansion

:: Enhanced ReadySearch Launcher
:: Version 2.0 - Integrated CLI and GUI options

title ReadySearch Enhanced Launcher v2.0

:main_menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    🔍 ReadySearch Enhanced Launcher v2.0                     ║
echo ║                                                              ║
echo ║    Choose Your Interface Experience                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🎨 Enhanced Interfaces:
echo   1. 💻 Enhanced CLI (Beautiful Terminal Interface)
echo   2. 🖼️  Advanced GUI (Modern Desktop Application)
echo.
echo 🔧 Original Tools:
echo   3. ⚡ Production CLI (Original Semicolon-Separated)
echo   4. 🎯 Single Name Test (Interactive Original)
echo   5. 🚀 PowerShell Launcher (Full Development Menu)
echo.
echo 🌐 Development Environment:
echo   6. 📊 Start Full-Stack Development Environment
echo   7. 🌍 Start with Ngrok Tunnel
echo.
echo 📋 System:
echo   8. 🔍 Check System Status
echo   9. 📖 Help and Documentation
echo   0. ❌ Exit
echo.
echo ════════════════════════════════════════════════════════════════

set /p choice="Select an option (0-9): "

if "%choice%"=="1" goto enhanced_cli
if "%choice%"=="2" goto advanced_gui
if "%choice%"=="3" goto production_cli
if "%choice%"=="4" goto single_test
if "%choice%"=="5" goto powershell_launcher
if "%choice%"=="6" goto start_dev_environment
if "%choice%"=="7" goto start_with_ngrok
if "%choice%"=="8" goto check_status
if "%choice%"=="9" goto show_help
if "%choice%"=="0" goto exit_launcher

echo Invalid choice. Please try again.
pause
goto main_menu

:enhanced_cli
cls
echo 🚀 Starting Enhanced CLI...
echo.
echo ✨ Features:
echo   • Beautiful terminal interface with colors and formatting
echo   • Structured results display with tables
echo   • Export functionality (JSON, CSV, TXT)
echo   • Continuous searching without restart
echo   • Session statistics and progress tracking
echo.
echo 📋 Requirements: Rich library (will auto-install if needed)
echo.
pause
python "%~dp0enhanced_cli.py"
echo.
echo 🎉 Enhanced CLI session completed!
pause
goto main_menu

:advanced_gui
cls
echo 🖼️ Starting Advanced GUI...
echo.
echo ✨ Features:
echo   • Modern desktop interface with professional styling
echo   • Real-time search progress with visual feedback
echo   • Tabbed results view (Summary + Detailed)
echo   • Interactive export options with file browser
echo   • Batch search with file loading capability
echo   • Session management and statistics
echo.
echo 📋 Requirements: Tkinter (included with Python)
echo.
pause
python readysearch_gui.py
echo.
echo 🎉 GUI session completed!
pause
goto main_menu

:production_cli
cls
echo ⚡ Starting Production CLI (Original)...
echo.
echo 💡 Examples:
echo   • Single name: John Smith
echo   • With birth year: John Smith,1990
echo   • Multiple names: John Smith;Jane Doe,1985;Bob Jones
echo.
set /p names="Enter names (semicolon-separated): "
if "%names%"=="" (
    echo Using demo data...
    set names=Andro Cutuk,1975;Anthony Bek,1993
)
python production_cli.py "%names%"
echo.
echo Production CLI completed!
pause
goto main_menu

:single_test
cls
echo 🎯 Starting Single Name Test...
python production_launcher.py
echo.
echo Single name test completed!
pause
goto main_menu

:powershell_launcher
cls
echo 🚀 Starting PowerShell Launcher...
echo This will open the full development environment menu.
echo.
pause
powershell -ExecutionPolicy Bypass -File launcher.ps1
goto main_menu

:start_dev_environment
cls
echo 📊 Starting Full-Stack Development Environment...
echo.
echo This will start:
echo   • Frontend Development Server (React/Vite)
echo   • Backend API Server (Python)
echo.
powershell -ExecutionPolicy Bypass -File launcher.ps1 -Action server
pause
goto main_menu

:start_with_ngrok
cls
echo 🌍 Starting Development Environment with Ngrok...
echo.
echo This will start:
echo   • Full-Stack Development Environment
echo   • Ngrok Tunnel for external access
echo.
powershell -ExecutionPolicy Bypass -Command "& { .\launcher.ps1; if ((Start-DevServer)) { Start-Sleep -Seconds 3; Start-NgrokTunnel } }"
pause
goto main_menu

:check_status
cls
echo 🔍 System Status Check...
echo.
echo Checking required components...
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python: Not found
) else (
    echo ✅ Python: Available
    python --version
)

:: Check required Python packages
echo.
echo Checking Python packages...
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo ❌ Playwright: Not installed
) else (
    echo ✅ Playwright: Available
)

python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Rich: Not installed (will auto-install for Enhanced CLI)
) else (
    echo ✅ Rich: Available
)

:: Check files
echo.
echo Checking application files...
if exist "enhanced_cli.py" (
    echo ✅ Enhanced CLI: Available
) else (
    echo ❌ Enhanced CLI: Missing
)

if exist "readysearch_gui.py" (
    echo ✅ Advanced GUI: Available
) else (
    echo ❌ Advanced GUI: Missing
)

if exist "production_cli.py" (
    echo ✅ Production CLI: Available
) else (
    echo ❌ Production CLI: Missing
)

if exist "launcher.ps1" (
    echo ✅ PowerShell Launcher: Available
) else (
    echo ❌ PowerShell Launcher: Missing
)

echo.
echo Status check completed!
pause
goto main_menu

:show_help
cls
echo 📖 ReadySearch Enhanced Launcher Help
echo ════════════════════════════════════════
echo.
echo 🎨 ENHANCED INTERFACES:
echo.
echo 💻 Enhanced CLI:
echo   • Beautiful terminal interface with Rich library
echo   • Structured output with tables and panels
echo   • Color-coded results and progress indicators
echo   • Export functionality (JSON, CSV, TXT)
echo   • Continuous searching without restart
echo   • Session statistics and performance metrics
echo.
echo 🖼️  Advanced GUI:
echo   • Modern desktop application with Tkinter
echo   • Professional styling and layout
echo   • Real-time search progress windows
echo   • Tabbed results view (Summary + Detailed)
echo   • Interactive export with file browser
echo   • Batch search with file loading
echo   • Visual feedback and notifications
echo.
echo 🔧 ORIGINAL TOOLS:
echo.
echo ⚡ Production CLI:
echo   • Original high-performance CLI
echo   • Semicolon-separated input format
echo   • Optimized for speed (30s target per search)
echo   • Direct browser automation
echo.
echo 🎯 Single Name Test:
echo   • Interactive single name search
echo   • Step-by-step guidance
echo   • Detailed result analysis
echo.
echo 🚀 PowerShell Launcher:
echo   • Full development environment menu
echo   • Build, test, and deployment options
echo   • Ngrok tunnel management
echo   • Process monitoring
echo.
echo 📋 USAGE TIPS:
echo.
echo • Use Enhanced CLI or GUI for best experience
echo • Original tools provide maximum performance
echo • Birth years improve search accuracy
echo • Export results for record keeping
echo • Check system status if experiencing issues
echo.
echo 🔧 TROUBLESHOOTING:
echo.
echo • If Enhanced CLI fails: Install Rich with 'pip install rich'
echo • If GUI doesn't start: Ensure Python has Tkinter support
echo • If searches fail: Check internet connection
echo • For development: Use PowerShell Launcher option 5
echo.
pause
goto main_menu

:exit_launcher
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    Thank you for using ReadySearch Enhanced Launcher!       ║
echo ║                                                              ║
echo ║    🔍 Professional Name Search Tool v2.0                     ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Session completed. Goodbye!
echo.
pause
exit /b 0