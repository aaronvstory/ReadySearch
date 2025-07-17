# ReadySearch Project

Advanced search application with comprehensive development tooling.

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
- **Start Dev Server** - Launches development server on port 3000

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

- **Node.js** - JavaScript runtime
- **NPM** - Package manager
- **Git** - Version control
- **Ngrok** - Tunneling service (optional)
- **PowerShell** - Script execution

## Configuration

The launcher automatically configures:
- Base port: 3000
- Ngrok region: US
- Log file: launcher.log
- Backup directory: backups/
- Archive directory: archive/

## Directory Structure

```
ReadySearch/
├── launch.bat          # Windows launcher
├── launcher.ps1        # PowerShell advanced launcher
├── package.json        # NPM configuration
├── src/                # Source code
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

## Troubleshooting

**Port conflicts**: Launcher automatically detects and stops conflicting processes

**Ngrok not found**: Install from https://ngrok.com/ and ensure it's in PATH

**PowerShell execution**: If scripts are blocked, run `Set-ExecutionPolicy RemoteSigned`

**Missing tools**: Use Option 10 to check system status and missing requirements

## Built with Claude AI

This project was created using Claude AI Development Partner with:
- Automated file management
- Comprehensive error handling
- Professional logging system
- Secure configuration management

---

Ready to launch your search application! 🚀
