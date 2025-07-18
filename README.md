# ReadySearch Project

Advanced search application with React, TypeScript, and Vite frontend plus comprehensive development tooling and automation.

## Quick Start

1. **Launch Development Environment:**
   ```bash
   launch.bat
   ```

2. **Command Line Usage:**
   ```bash
   # Build project
   powershell -File launcher.ps1 -Action build
   
   # Start dev server
   powershell -File launcher.ps1 -Action server
   
   # Start ngrok tunnel
   powershell -File launcher.ps1 -Action ngrok
   
   # Check system status
   powershell -File launcher.ps1 -Action status
   ```

## Features

- 🔧 **Project Initialization** - Automated project structure setup
- 🏗️ **Build Management** - NPM dependency management and building
- 🧪 **Testing Suite** - Automated test execution
- 🚀 **Development Server** - Local development with hot reload
- 🌐 **Ngrok Integration** - Secure tunneling for external access
- 📊 **Connection Monitoring** - Real-time tunnel and connection tracking
- 🔄 **Process Management** - Automated cleanup and port management
- 📋 **System Status** - Comprehensive development environment checking

## Launcher Options

### Development
- **Initialize Project** - Sets up directory structure and package.json
- **Build Project** - Installs dependencies and runs build scripts
- **Run Tests** - Executes test suite
- **Start Dev Server** - Launches Vite development server on port 5173

### Deployment & Tunneling
- **Start Ngrok Tunnel** - Creates secure public tunnel
- **Monitor Connections** - Shows active connections and metrics
- **Stop Tunnels** - Cleanly terminates all ngrok processes

### Combined Actions
- **Dev Server + Ngrok** - Starts both server and tunnel
- **Full Deploy** - Complete build, server, and tunnel setup

### System Management
- **System Status** - Validates all required tools
- **Process Monitor** - Shows active development processes

## Requirements

- **Node.js** - JavaScript runtime (v18+)
- **NPM** - Package manager
- **Git** - Version control
- **Vite** - Build tool and dev server
- **Ngrok** - Tunneling service (optional)
- **PowerShell** - Script execution

## Configuration

The launcher automatically configures:
- Base port: 5173 (Vite default)
- Ngrok region: US
- Log file: launcher.log
- Backup directory: backups/
- Archive directory: archive/
- Vite dev server with hot reload

## Directory Structure

```
ReadySearch/
├── launch.bat          # Windows launcher
├── launcher.ps1        # PowerShell advanced launcher
├── package.json        # NPM configuration
├── vite.config.ts      # Vite configuration
├── src/                # React TypeScript source
│   ├── App.tsx         # Main application
│   ├── components/     # React components
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── tests/              # Test files
├── docs/               # Documentation
├── logs/               # Application logs
├── backups/            # Automatic backups
└── archive/            # Old/test files
```

## Ngrok Setup

1. Install ngrok from https://ngrok.com/
2. Get auth token from ngrok dashboard
3. Run: `ngrok authtoken YOUR_TOKEN`
4. Launcher will handle the rest automatically

## Development Workflow

1. **Start**: `launch.bat` → Option 1 (Initialize)
2. **Build**: Option 2 (Build Project)
3. **Test**: Option 3 (Run Tests)
4. **Develop**: Option 8 (Dev Server + Ngrok)
5. **Monitor**: Option 6 (Show Connections)

## Recent Updates

### ✅ Launcher Fixes (Latest)
- **Fixed** npm command execution on Windows (resolved "not a valid Win32 application" error)
- **Added** Vite support with proper port configuration
- **Updated** port monitoring to include Vite ports (5173, 5174)
- **Improved** development server startup reliability

## Troubleshooting

**"Not a valid Win32 application"**: Fixed in latest update - launcher now uses cmd wrapper for npm commands

**Port conflicts**: Launcher automatically detects and stops conflicting processes

**Vite server issues**: Launcher now properly handles Vite's default port (5173) and startup

**Ngrok not found**: Install from https://ngrok.com/ and ensure it's in PATH

**PowerShell execution**: If scripts are blocked, run `Set-ExecutionPolicy RemoteSigned`

**Missing tools**: Use Option 10 to check system status and missing requirements

## Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite for build tooling and dev server
- Tailwind CSS for styling
- Lucide React for icons

**Development:**
- Advanced PowerShell launcher with menu system
- Automated port management and process monitoring
- Ngrok integration for secure tunneling
- Comprehensive error handling and logging

## Built with Claude AI

This project was created using Claude AI Development Partner with:
- Automated file management
- Comprehensive error handling
- Professional logging system
- Secure configuration management
- Latest launcher fixes for Windows compatibility

---

Ready to launch your search application! 🚀
