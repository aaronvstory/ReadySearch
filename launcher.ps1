# ReadySearch Advanced PowerShell Launcher
# Version 1.0 - Advanced Development & Deployment Manager

param(
    [string]$Action = ""
)

# Set console title and encoding
$Host.UI.RawUI.WindowTitle = "ReadySearch - Advanced Development Launcher"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color configuration
$Colors = @{
    Info    = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Header  = "Magenta"
    Prompt  = "White"
}

# Global configuration
$Config = @{
    ProjectName = "ReadySearch"
    BasePort = 5173
    NgrokRegion = "us"
    MaxConnections = 10
    LogFile = "launcher.log"
    BackupDir = "backups"
    ArchiveDir = "archive"
}

# Initialize logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $Config.LogFile -Value $logEntry -Encoding UTF8
}

# Enhanced console output with colors
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Level = "INFO",
        [switch]$NoNewline
    )
    
    $prefix = switch ($Level) {
        "SUCCESS" { "✅" }
        "ERROR"   { "❌" }
        "WARNING" { "⚠️" }
        "INFO"    { "ℹ️" }
        "HEADER"  { "🚀" }
        default   { "•" }
    }
    
    $output = "$prefix $Message"
    
    if ($NoNewline) {
        Write-Host $output -ForegroundColor $Colors[$Color] -NoNewline
    } else {
        Write-Host $output -ForegroundColor $Colors[$Color]
    }
    
    Write-Log -Message $Message -Level $Level
}

# Check if a process is running on a specific port
function Test-PortInUse {
    param([int]$Port)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $connection -ne $null
    } catch {
        return $false
    }
}

# Get process using a specific port
function Get-ProcessByPort {
    param([int]$Port)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            return Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        }
    } catch {
        return $null
    }
    return $null
}

# Kill processes on specific ports
function Stop-ProcessOnPort {
    param([int]$Port)
    
    $process = Get-ProcessByPort -Port $Port
    if ($process) {
        try {
            Write-ColoredOutput "Stopping process '$($process.ProcessName)' (PID: $($process.Id)) on port $Port" -Color "Warning" -Level "WARNING"
            $process | Stop-Process -Force
            Start-Sleep -Seconds 2
            
            if (-not (Test-PortInUse -Port $Port)) {
                Write-ColoredOutput "Successfully freed port $Port" -Color "Success" -Level "SUCCESS"
                return $true
            }
        } catch {
            Write-ColoredOutput "Failed to stop process on port $Port`: $_" -Color "Error" -Level "ERROR"
        }
    }
    return $false
}

# Check and install required tools
function Test-RequiredTools {
    Write-ColoredOutput "Checking required development tools..." -Color "Info" -Level "INFO"
    
    $tools = @{
        "node" = "Node.js"
        "npm" = "NPM"
        "git" = "Git"
    }
    
    $missing = @()
    
    foreach ($tool in $tools.Keys) {
        try {
            $null = & $tool --version 2>$null
            Write-ColoredOutput "$($tools[$tool]) ✓" -Color "Success" -Level "SUCCESS"
        } catch {
            Write-ColoredOutput "$($tools[$tool]) ✗ (Missing)" -Color "Error" -Level "ERROR"
            $missing += $tools[$tool]
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-ColoredOutput "Missing tools: $($missing -join ', ')" -Color "Error" -Level "ERROR"
        return $false
    }
    
    return $true
}

# Check and setup ngrok
function Test-NgrokSetup {
    try {
        $ngrokVersion = & ngrok version 2>$null
        Write-ColoredOutput "Ngrok is available: $ngrokVersion" -Color "Success" -Level "SUCCESS"
        
        # Check if ngrok is authenticated
        $configPath = "$env:USERPROFILE\.ngrok2\ngrok.yml"
        if (-not (Test-Path $configPath)) {
            Write-ColoredOutput "Ngrok not configured. Please run 'ngrok authtoken YOUR_TOKEN'" -Color "Warning" -Level "WARNING"
            return $false
        }
        
        return $true
    } catch {
        Write-ColoredOutput "Ngrok not found. Please install from https://ngrok.com/" -Color "Error" -Level "ERROR"
        return $false
    }
}

# Get ngrok tunnel status and connections
function Get-NgrokStatus {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction SilentlyContinue
        return $response.tunnels
    } catch {
        return $null
    }
}

# Monitor ngrok connections
function Show-NgrokConnections {
    Write-ColoredOutput "Monitoring Ngrok connections..." -Color "Info" -Level "INFO"
    
    try {
        $tunnels = Get-NgrokStatus
        if ($tunnels) {
            Write-Host ""
            Write-Host "Active Ngrok Tunnels:" -ForegroundColor $Colors.Header
            Write-Host "===================" -ForegroundColor $Colors.Header
            
            foreach ($tunnel in $tunnels) {
                Write-Host "Name: $($tunnel.name)" -ForegroundColor $Colors.Info
                Write-Host "Public URL: $($tunnel.public_url)" -ForegroundColor $Colors.Success
                Write-Host "Local URL: $($tunnel.config.addr)" -ForegroundColor $Colors.Info
                Write-Host "Protocol: $($tunnel.proto)" -ForegroundColor $Colors.Info
                Write-Host "---"
            }
            
            # Get connection metrics
            try {
                $metrics = Invoke-RestMethod -Uri "http://localhost:4040/api/requests/http" -ErrorAction SilentlyContinue
                if ($metrics -and $metrics.requests) {
                    Write-Host "Recent Connections:" -ForegroundColor $Colors.Header
                    $metrics.requests | Select-Object -First 10 | ForEach-Object {
                        $timestamp = [DateTime]::Parse($_.start_ts).ToString("HH:mm:ss")
                        Write-Host "[$timestamp] $($_.remote_addr) -> $($_.host) ($($_.status))" -ForegroundColor $Colors.Prompt
                    }
                }
            } catch {
                Write-ColoredOutput "Could not retrieve connection metrics" -Color "Warning" -Level "WARNING"
            }
        } else {
            Write-ColoredOutput "No active ngrok tunnels found" -Color "Warning" -Level "WARNING"
        }
    } catch {
        Write-ColoredOutput "Could not connect to ngrok API (is ngrok running?)" -Color "Error" -Level "ERROR"
    }
}

# Stop all ngrok tunnels
function Stop-NgrokTunnels {
    Write-ColoredOutput "Stopping all ngrok tunnels..." -Color "Warning" -Level "WARNING"
    
    try {
        $tunnels = Get-NgrokStatus
        if ($tunnels) {
            foreach ($tunnel in $tunnels) {
                try {
                    Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels/$($tunnel.name)" -Method DELETE -ErrorAction SilentlyContinue
                    Write-ColoredOutput "Stopped tunnel: $($tunnel.name)" -Color "Success" -Level "SUCCESS"
                } catch {
                    Write-ColoredOutput "Failed to stop tunnel: $($tunnel.name)" -Color "Error" -Level "ERROR"
                }
            }
        }
        
        # Kill ngrok process if still running
        Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-ColoredOutput "All ngrok processes terminated" -Color "Success" -Level "SUCCESS"
        
    } catch {
        Write-ColoredOutput "Error stopping ngrok tunnels: $_" -Color "Error" -Level "ERROR"
    }
}

# Setup project structure
function Initialize-ProjectStructure {
    Write-ColoredOutput "Setting up project structure..." -Color "Info" -Level "INFO"
    
    $directories = @(
        $Config.BackupDir,
        $Config.ArchiveDir,
        "src",
        "public",
        "tests",
        "docs",
        "logs"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColoredOutput "Created directory: $dir" -Color "Success" -Level "SUCCESS"
        }
    }
    
    # Create basic package.json if it doesn't exist
    if (-not (Test-Path "package.json")) {
        $packageJson = @{
            name = "readysearch"
            version = "1.0.0"
            description = "Advanced search application"
            main = "src/index.js"
            scripts = @{
                start = "node src/index.js"
                dev = "node src/index.js --dev"
                test = "npm test"
                build = "npm run build"
            }
            dependencies = @{}
            devDependencies = @{}
        } | ConvertTo-Json -Depth 3
        
        $packageJson | Out-File -FilePath "package.json" -Encoding UTF8
        Write-ColoredOutput "Created package.json" -Color "Success" -Level "SUCCESS"
    }
}

# Build project
function Build-Project {
    Write-ColoredOutput "Building ReadySearch project..." -Color "Info" -Level "INFO"
    
    # Install dependencies
    if (Test-Path "package.json") {
        Write-ColoredOutput "Installing NPM dependencies..." -Color "Info" -Level "INFO"
        & npm install
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "Dependencies installed successfully" -Color "Success" -Level "SUCCESS"
        } else {
            Write-ColoredOutput "Failed to install dependencies" -Color "Error" -Level "ERROR"
            return $false
        }
    }
    
    # Run build script if available
    try {
        $packageContent = Get-Content "package.json" | ConvertFrom-Json
        if ($packageContent.scripts.build) {
            Write-ColoredOutput "Running build script..." -Color "Info" -Level "INFO"
            & npm run build
            if ($LASTEXITCODE -eq 0) {
                Write-ColoredOutput "Build completed successfully" -Color "Success" -Level "SUCCESS"
            } else {
                Write-ColoredOutput "Build failed" -Color "Error" -Level "ERROR"
                return $false
            }
        }
    } catch {
        Write-ColoredOutput "No build script found, skipping..." -Color "Warning" -Level "WARNING"
    }
    
    return $true
}

# Run tests
function Test-Project {
    Write-ColoredOutput "Running project tests..." -Color "Info" -Level "INFO"
    
    if (Test-Path "package.json") {
        try {
            $packageContent = Get-Content "package.json" | ConvertFrom-Json
            if ($packageContent.scripts.test) {
                & npm test
                if ($LASTEXITCODE -eq 0) {
                    Write-ColoredOutput "All tests passed" -Color "Success" -Level "SUCCESS"
                } else {
                    Write-ColoredOutput "Some tests failed" -Color "Error" -Level "ERROR"
                }
            } else {
                Write-ColoredOutput "No test script found" -Color "Warning" -Level "WARNING"
            }
        } catch {
            Write-ColoredOutput "Error reading package.json" -Color "Error" -Level "ERROR"
        }
    } else {
        Write-ColoredOutput "No package.json found" -Color "Warning" -Level "WARNING"
    }
}

# Start development server (Frontend + Backend)
function Start-DevServer {
    param([int]$Port = $Config.BasePort)
    
    Write-ColoredOutput "Starting full-stack development environment..." -Color "Header" -Level "HEADER"
    
    # Backend API Server (Port 5000)
    $ApiPort = 5000
    Write-ColoredOutput "🐍 Starting Python API Server (Backend) on port $ApiPort..." -Color "Info" -Level "INFO"
    
    # Stop any existing API server
    if (Test-PortInUse -Port $ApiPort) {
        Write-ColoredOutput "Stopping existing API server on port $ApiPort..." -Color "Warning" -Level "WARNING"
        Stop-ProcessOnPort -Port $ApiPort
        Start-Sleep -Seconds 2
    }
    
    # Start Python API server
    $ApiServerStarted = $false
    try {
        if (Test-Path "production_api_server.py") {
            Write-ColoredOutput "🚀 Launching PRODUCTION Python API server with REAL Automation..." -Color "Info" -Level "INFO"
            Start-Process "cmd" -ArgumentList "/c", "python", "production_api_server.py" -WindowStyle Hidden
            Start-Sleep -Seconds 3
            
            if (Test-PortInUse -Port $ApiPort) {
                Write-ColoredOutput "✅ Python API Server started successfully on port $ApiPort" -Color "Success" -Level "SUCCESS"
                Write-ColoredOutput "📡 API URL: http://localhost:$ApiPort" -Color "Success" -Level "SUCCESS"
                $ApiServerStarted = $true
            } else {
                Write-ColoredOutput "❌ Failed to start Python API server" -Color "Error" -Level "ERROR"
            }
        } else {
            Write-ColoredOutput "❌ production_api_server.py not found" -Color "Error" -Level "ERROR"
        }
    } catch {
        Write-ColoredOutput "❌ Error starting Python API server: $_" -Color "Error" -Level "ERROR"
    }
    
    # Frontend Development Server (Port 5173)
    Write-ColoredOutput "⚛️ Starting Frontend Development Server on port $Port..." -Color "Info" -Level "INFO"
    
    # Stop any existing process on the frontend port
    if (Test-PortInUse -Port $Port) {
        Write-ColoredOutput "Stopping existing frontend server on port $Port..." -Color "Warning" -Level "WARNING"
        Stop-ProcessOnPort -Port $Port
        Start-Sleep -Seconds 2
    }
    
    # Start the frontend development server
    $FrontendStarted = $false
    try {
        if (Test-Path "package.json") {
            $packageContent = Get-Content "package.json" | ConvertFrom-Json
            if ($packageContent.scripts.dev) {
                Write-ColoredOutput "🚀 Starting with NPM dev script..." -Color "Info" -Level "INFO"
                # For Vite, we need to set the port differently
                if ($packageContent.devDependencies.vite) {
                    Start-Process "cmd" -ArgumentList "/c", "npm", "run", "dev", "--", "--port", "$Port" -NoNewWindow
                } else {
                    $env:PORT = $Port
                    Start-Process "cmd" -ArgumentList "/c", "npm", "run", "dev" -NoNewWindow
                }
            } elseif ($packageContent.scripts.start) {
                Write-ColoredOutput "🚀 Starting with NPM start script..." -Color "Info" -Level "INFO"
                $env:PORT = $Port
                Start-Process "cmd" -ArgumentList "/c", "npm", "start" -NoNewWindow
            } else {
                Write-ColoredOutput "❌ No dev/start script found in package.json" -Color "Error" -Level "ERROR"
                return $false
            }
        } else {
            Write-ColoredOutput "❌ No package.json found" -Color "Error" -Level "ERROR"
            return $false
        }
        
        # Wait a moment and check if frontend server started
        Start-Sleep -Seconds 4
        if (Test-PortInUse -Port $Port) {
            Write-ColoredOutput "✅ Frontend server started successfully on port $Port" -Color "Success" -Level "SUCCESS"
            Write-ColoredOutput "🌐 Frontend URL: http://localhost:$Port" -Color "Success" -Level "SUCCESS"
            $FrontendStarted = $true
        } else {
            Write-ColoredOutput "❌ Failed to start frontend server" -Color "Error" -Level "ERROR"
        }
        
    } catch {
        Write-ColoredOutput "❌ Error starting frontend server: $_" -Color "Error" -Level "ERROR"
    }
    
    # Summary
    Write-Host ""
    Write-ColoredOutput "📊 Development Environment Status:" -Color "Header" -Level "HEADER"
    if ($ApiServerStarted) {
        Write-ColoredOutput "✅ Backend API Server: Running on http://localhost:$ApiPort" -Color "Success" -Level "SUCCESS"
        Write-ColoredOutput "   Available endpoints: /api/start-automation, /api/health" -Color "Info" -Level "INFO"
    } else {
        Write-ColoredOutput "❌ Backend API Server: Failed to start" -Color "Error" -Level "ERROR"
    }
    
    if ($FrontendStarted) {
        Write-ColoredOutput "✅ Frontend Server: Running on http://localhost:$Port" -Color "Success" -Level "SUCCESS"
        Write-ColoredOutput "   React app with ReadySearch automation interface" -Color "Info" -Level "INFO"
    } else {
        Write-ColoredOutput "❌ Frontend Server: Failed to start" -Color "Error" -Level "ERROR"
    }
    
    if ($ApiServerStarted -and $FrontendStarted) {
        Write-Host ""
        Write-ColoredOutput "🎉 Full-stack development environment ready!" -Color "Success" -Level "SUCCESS"
        Write-ColoredOutput "🌐 Open http://localhost:$Port to use ReadySearch automation" -Color "Success" -Level "SUCCESS"
        Write-ColoredOutput "📡 Backend API available at http://localhost:$ApiPort" -Color "Success" -Level "SUCCESS"
        return $true
    } else {
        Write-Host ""
        Write-ColoredOutput "⚠️ Partial startup - some services failed" -Color "Warning" -Level "WARNING"
        return $false
    }
}

# Start ngrok tunnel
function Start-NgrokTunnel {
    param([int]$Port = $Config.BasePort)
    
    Write-ColoredOutput "Starting ngrok tunnel for port $Port..." -Color "Info" -Level "INFO"
    
    # Stop existing tunnels first
    Stop-NgrokTunnels
    Start-Sleep -Seconds 2
    
    try {
        # Start ngrok in background
        $ngrokArgs = @("http", $Port, "--region", $Config.NgrokRegion)
        Start-Process "ngrok" -ArgumentList $ngrokArgs -WindowStyle Hidden
        
        # Wait for ngrok to start
        Write-ColoredOutput "Waiting for ngrok to initialize..." -Color "Info" -Level "INFO"
        Start-Sleep -Seconds 5
        
        # Get tunnel information
        $attempts = 0
        do {
            Start-Sleep -Seconds 2
            $tunnels = Get-NgrokStatus
            $attempts++
        } while (-not $tunnels -and $attempts -lt 10)
        
        if ($tunnels) {
            foreach ($tunnel in $tunnels) {
                Write-ColoredOutput "Ngrok tunnel active!" -Color "Success" -Level "SUCCESS"
                Write-ColoredOutput "Public URL: $($tunnel.public_url)" -Color "Success" -Level "SUCCESS"
                Write-ColoredOutput "Local URL: $($tunnel.config.addr)" -Color "Info" -Level "INFO"
                Write-ColoredOutput "Web Interface: http://localhost:4040" -Color "Info" -Level "INFO"
            }
            return $true
        } else {
            Write-ColoredOutput "Failed to establish ngrok tunnel" -Color "Error" -Level "ERROR"
            return $false
        }
        
    } catch {
        Write-ColoredOutput "Error starting ngrok tunnel: $_" -Color "Error" -Level "ERROR"
        return $false
    }
}

# Show main menu
function Show-MainMenu {
    Clear-Host
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $Colors.Header
    Write-Host "    READYSEARCH ADVANCED LAUNCHER" -ForegroundColor $Colors.Header
    Write-Host "========================================" -ForegroundColor $Colors.Header
    Write-Host ""
    Write-Host "🎨 Enhanced Interfaces:" -ForegroundColor $Colors.Header
    Write-Host "  1. 💻 Enhanced CLI (Beautiful Terminal Interface)" -ForegroundColor $Colors.Prompt
    Write-Host "  2. 🖼️  Advanced GUI (Modern Desktop Application)" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "Development Options:" -ForegroundColor $Colors.Info
    Write-Host "  3. 🔧 Initialize Project Structure" -ForegroundColor $Colors.Prompt
    Write-Host "  4. 🏗️  Build Project" -ForegroundColor $Colors.Prompt
    Write-Host "  5. 🧪 Run Tests" -ForegroundColor $Colors.Prompt
    Write-Host "  6. 🚀 Start Full-Stack Dev Environment (Frontend + Backend)" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "ReadySearch Automation:" -ForegroundColor $Colors.Info
    Write-Host "  7. ⚡ Production CLI (Semicolon-Separated Names)" -ForegroundColor $Colors.Prompt
    Write-Host "  8. 🎯 Single Name Test (Interactive)" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "Deployment & Tunneling:" -ForegroundColor $Colors.Info
    Write-Host "  9. 🌐 Start Ngrok Tunnel" -ForegroundColor $Colors.Prompt
    Write-Host " 10. 📊 Show Ngrok Connections" -ForegroundColor $Colors.Prompt
    Write-Host " 11. 🛑 Stop All Ngrok Tunnels" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "Combined Actions:" -ForegroundColor $Colors.Info
    Write-Host " 12. 🚀🌐 Start Full-Stack + Ngrok Tunnel" -ForegroundColor $Colors.Prompt
    Write-Host " 13. 🔄 Complete Deploy (Build + Full-Stack + Tunnel)" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "System:" -ForegroundColor $Colors.Info
    Write-Host " 14. 🔍 Check System Status" -ForegroundColor $Colors.Prompt
    Write-Host " 15. 📋 Show Process Monitor" -ForegroundColor $Colors.Prompt
    Write-Host "  0. ❌ Exit" -ForegroundColor $Colors.Error
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $Colors.Header
}

# Process monitor
function Show-ProcessMonitor {
    Write-ColoredOutput "Development Process Monitor" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check ports
    $ports = @($Config.BasePort, 3000, 5000, 5173, 5174, 4040, 8080)
    Write-Host "Port Status:" -ForegroundColor $Colors.Info
    foreach ($port in $ports) {
        $inUse = Test-PortInUse -Port $port
        $status = if ($inUse) { "ACTIVE" } else { "FREE" }
        $color = if ($inUse) { $Colors.Success } else { $Colors.Warning }
        
        if ($inUse) {
            $process = Get-ProcessByPort -Port $port
            Write-Host "  Port $port`: $status ($($process.ProcessName) - PID: $($process.Id))" -ForegroundColor $color
        } else {
            Write-Host "  Port $port`: $status" -ForegroundColor $color
        }
    }
    
    Write-Host ""
    Write-Host "Development Processes:" -ForegroundColor $Colors.Info
    $devProcesses = @("node", "npm", "python", "ngrok", "code")
    foreach ($processName in $devProcesses) {
        $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
        if ($processes) {
            foreach ($proc in $processes) {
                Write-Host "  $($proc.ProcessName) (PID: $($proc.Id)) - CPU: $($proc.CPU)" -ForegroundColor $Colors.Success
            }
        }
    }
}

# Start Production CLI with semicolon-separated names
function Start-ProductionCLI {
    Write-ColoredOutput "🚀 ReadySearch Production CLI" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check if production_cli.py exists
    if (-not (Test-Path "production_cli.py")) {
        Write-ColoredOutput "❌ production_cli.py not found!" -Color "Error" -Level "ERROR"
        return $false
    }
    
    Write-Host "💡 Examples:" -ForegroundColor $Colors.Info
    Write-Host "   • Single name: John Smith" -ForegroundColor $Colors.Prompt
    Write-Host "   • With birth year: John Smith,1990" -ForegroundColor $Colors.Prompt
    Write-Host "   • Multiple names: John Smith;Jane Doe,1985;Bob Jones" -ForegroundColor $Colors.Prompt
    Write-Host ""
    
    # Get names from user
    do {
        try {
            $names = Read-Host "🔤 Enter names (semicolon-separated, or 'demo' for test data)"
            
            # Handle null input (can happen in command-line mode)
            if ($null -eq $names) {
                Write-ColoredOutput "🧪 No input detected, using demo data..." -Color "Info" -Level "INFO"
                $names = "Andro Cutuk,1975;Anthony Bek,1993;Ghafoor Jaggi Nadery,1978"
                break
            } elseif ($names -eq "demo") {
                $names = "Andro Cutuk,1975;Anthony Bek,1993;Ghafoor Jaggi Nadery,1978"
                Write-ColoredOutput "🧪 Using demo data: $names" -Color "Info" -Level "INFO"
                break
            } elseif ($names -and $names.Trim()) {
                break
            } else {
                Write-ColoredOutput "⚠️ Please enter at least one name" -Color "Warning" -Level "WARNING"
            }
        } catch {
            # If Read-Host fails (e.g., in non-interactive mode), use demo data
            Write-ColoredOutput "🧪 Using demo data (non-interactive mode)..." -Color "Info" -Level "INFO"
            $names = "Andro Cutuk,1975;Anthony Bek,1993;Ghafoor Jaggi Nadery,1978"
            break
        }
    } while ($true)
    
    try {
        Write-ColoredOutput "⚡ Starting production CLI automation..." -Color "Info" -Level "INFO"
        Write-Host ""
        
        # Execute the CLI with the names
        $output = & python "production_cli.py" $names 2>&1
        
        # Display the output with proper formatting
        $output | ForEach-Object {
            $line = $_.ToString()
            if ($line -match "^✅|🎉|📊") {
                Write-Host $line -ForegroundColor $Colors.Success
            } elseif ($line -match "^❌|⚠️") {
                Write-Host $line -ForegroundColor $Colors.Error
            } elseif ($line -match "^🔍|📋|⚡|🚀|🌐|⌨️|📅") {
                Write-Host $line -ForegroundColor $Colors.Info
            } elseif ($line -match "^=|🎯") {
                Write-Host $line -ForegroundColor $Colors.Header
            } else {
                Write-Host $line -ForegroundColor $Colors.Prompt
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColoredOutput "🎉 Production CLI completed successfully!" -Color "Success" -Level "SUCCESS"
        } else {
            Write-ColoredOutput "❌ CLI execution failed with exit code: $LASTEXITCODE" -Color "Error" -Level "ERROR"
        }
        
    } catch {
        Write-ColoredOutput "❌ Error running production CLI: $_" -Color "Error" -Level "ERROR"
        return $false
    }
    
    return $true
}

# Start Enhanced CLI
function Start-EnhancedCLI {
    Write-ColoredOutput "💻 ReadySearch Enhanced CLI" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check if enhanced_cli.py exists
    if (-not (Test-Path "enhanced_cli.py")) {
        Write-ColoredOutput "❌ enhanced_cli.py not found!" -Color "Error" -Level "ERROR"
        return $false
    }
    
    Write-Host "✨ Features:" -ForegroundColor $Colors.Info
    Write-Host "   • Beautiful terminal interface with colors and formatting" -ForegroundColor $Colors.Prompt
    Write-Host "   • Structured results display with tables" -ForegroundColor $Colors.Prompt
    Write-Host "   • Export functionality (JSON, CSV, TXT)" -ForegroundColor $Colors.Prompt
    Write-Host "   • Continuous searching without restart" -ForegroundColor $Colors.Prompt
    Write-Host "   • Session statistics and progress tracking" -ForegroundColor $Colors.Prompt
    Write-Host ""
    
    try {
        Write-ColoredOutput "🚀 Starting Enhanced CLI..." -Color "Info" -Level "INFO"
        Write-Host ""
        
        # Execute the Enhanced CLI
        & python "enhanced_cli.py"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColoredOutput "🎉 Enhanced CLI session completed!" -Color "Success" -Level "SUCCESS"
        } else {
            Write-ColoredOutput "❌ Enhanced CLI failed with exit code: $LASTEXITCODE" -Color "Error" -Level "ERROR"
        }
        
    } catch {
        Write-ColoredOutput "❌ Error running Enhanced CLI: $_" -Color "Error" -Level "ERROR"
        return $false
    }
    
    return $true
}

# Start Advanced GUI
function Start-AdvancedGUI {
    Write-ColoredOutput "🖼️ ReadySearch Advanced GUI" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check if readysearch_gui.py exists
    if (-not (Test-Path "readysearch_gui.py")) {
        Write-ColoredOutput "❌ readysearch_gui.py not found!" -Color "Error" -Level "ERROR"
        return $false
    }
    
    Write-Host "✨ Features:" -ForegroundColor $Colors.Info
    Write-Host "   • Modern desktop interface with professional styling" -ForegroundColor $Colors.Prompt
    Write-Host "   • Real-time search progress with visual feedback" -ForegroundColor $Colors.Prompt
    Write-Host "   • Tabbed results view (Summary + Detailed)" -ForegroundColor $Colors.Prompt
    Write-Host "   • Interactive export options with file browser" -ForegroundColor $Colors.Prompt
    Write-Host "   • Batch search with file loading capability" -ForegroundColor $Colors.Prompt
    Write-Host "   • Session management and statistics" -ForegroundColor $Colors.Prompt
    Write-Host ""
    
    try {
        Write-ColoredOutput "🚀 Starting Advanced GUI..." -Color "Info" -Level "INFO"
        Write-Host ""
        
        # Execute the GUI application
        & python "readysearch_gui.py"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColoredOutput "🎉 GUI session completed!" -Color "Success" -Level "SUCCESS"
        } else {
            Write-ColoredOutput "❌ GUI failed with exit code: $LASTEXITCODE" -Color "Error" -Level "ERROR"
        }
        
    } catch {
        Write-ColoredOutput "❌ Error running Advanced GUI: $_" -Color "Error" -Level "ERROR"
        return $false
    }
    
    return $true
}

# Start single name interactive test
function Start-SingleNameTest {
    Write-ColoredOutput "🎯 ReadySearch Single Name Test" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check if production_launcher.py exists
    if (-not (Test-Path "production_launcher.py")) {
        Write-ColoredOutput "❌ production_launcher.py not found!" -Color "Error" -Level "ERROR"
        return $false
    }
    
    try {
        Write-ColoredOutput "🚀 Starting interactive single name test..." -Color "Info" -Level "INFO"
        Write-Host ""
        
        # Execute the single name test (it has its own interactive prompt)
        & python "production_launcher.py"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColoredOutput "🎉 Single name test completed!" -Color "Success" -Level "SUCCESS"
        } else {
            Write-ColoredOutput "❌ Test failed with exit code: $LASTEXITCODE" -Color "Error" -Level "ERROR"
        }
        
    } catch {
        Write-ColoredOutput "❌ Error running single name test: $_" -Color "Error" -Level "ERROR"
        return $false
    }
    
    return $true
}

# System status check
function Show-SystemStatus {
    Write-ColoredOutput "System Status Check" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check tools
    $toolsOk = Test-RequiredTools
    
    # Check ngrok
    Write-Host ""
    $ngrokOk = Test-NgrokSetup
    
    # Check project structure
    Write-Host ""
    Write-ColoredOutput "Project Structure:" -Color "Info" -Level "INFO"
    $requiredFiles = @("package.json", "src", "public")
    foreach ($file in $requiredFiles) {
        $exists = Test-Path $file
        $status = if ($exists) { "✓" } else { "✗" }
        $color = if ($exists) { $Colors.Success } else { $Colors.Error }
        Write-Host "  $file $status" -ForegroundColor $color
    }
    
    # Overall status
    Write-Host ""
    $overallStatus = $toolsOk -and $ngrokOk
    if ($overallStatus) {
        Write-ColoredOutput "System is ready for development!" -Color "Success" -Level "SUCCESS"
    } else {
        Write-ColoredOutput "System needs configuration before development" -Color "Error" -Level "ERROR"
    }
}

# Main execution logic
function Main {
    # Initialize logging
    Write-Log -Message "ReadySearch Advanced Launcher started" -Level "INFO"
    
    # Create basic directories
    @($Config.BackupDir, $Config.ArchiveDir, "logs") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }
    
    # Handle command line parameters
    if ($Action) {
        switch ($Action.ToLower()) {
            "enhanced-cli" { Start-EnhancedCLI; Read-Host "Press Enter to exit"; exit }
            "gui" { Start-AdvancedGUI; Read-Host "Press Enter to exit"; exit }
            "build" { Build-Project; exit }
            "test" { Test-Project; exit }
            "server" { Start-DevServer; Read-Host "Press Enter to exit"; exit }
            "cli" { Start-ProductionCLI; Read-Host "Press Enter to exit"; exit }
            "single" { Start-SingleNameTest; Read-Host "Press Enter to exit"; exit }
            "ngrok" { Start-NgrokTunnel; Read-Host "Press Enter to exit"; exit }
            "status" { Show-SystemStatus; Read-Host "Press Enter to exit"; exit }
            default { Write-ColoredOutput "Unknown action: $Action" -Color "Error" -Level "ERROR"; exit 1 }
        }
    }
    
    # Main interactive loop
    do {
        Show-MainMenu
        $choice = Read-Host "Select an option"
        
        switch ($choice) {
            "1" {
                Start-EnhancedCLI
                Read-Host "Press Enter to continue"
            }
            "2" {
                Start-AdvancedGUI
                Read-Host "Press Enter to continue"
            }
            "3" {
                Initialize-ProjectStructure
                Read-Host "Press Enter to continue"
            }
            "4" {
                Build-Project
                Read-Host "Press Enter to continue"
            }
            "5" {
                Test-Project
                Read-Host "Press Enter to continue"
            }
            "6" {
                Start-DevServer
                Read-Host "Press Enter to continue"
            }
            "7" {
                Start-ProductionCLI
                Read-Host "Press Enter to continue"
            }
            "8" {
                Start-SingleNameTest
                Read-Host "Press Enter to continue"
            }
            "9" {
                Start-NgrokTunnel
                Read-Host "Press Enter to continue"
            }
            "10" {
                Show-NgrokConnections
                Read-Host "Press Enter to continue"
            }
            "11" {
                Stop-NgrokTunnels
                Read-Host "Press Enter to continue"
            }
            "12" {
                if (Start-DevServer) {
                    Start-Sleep -Seconds 3
                    Start-NgrokTunnel
                }
                Read-Host "Press Enter to continue"
            }
            "13" {
                if (Build-Project) {
                    if (Start-DevServer) {
                        Start-Sleep -Seconds 3
                        Start-NgrokTunnel
                        Show-NgrokConnections
                    }
                }
                Read-Host "Press Enter to continue"
            }
            "14" {
                Show-SystemStatus
                Read-Host "Press Enter to continue"
            }
            "15" {
                Show-ProcessMonitor
                Read-Host "Press Enter to continue"
            }
            "0" {
                Write-ColoredOutput "Shutting down launcher..." -Color "Warning" -Level "WARNING"
                break
            }
            default {
                Write-ColoredOutput "Invalid option. Please try again." -Color "Error" -Level "ERROR"
                Start-Sleep -Seconds 2
            }
        }
    } while ($true)
    
    Write-Log -Message "ReadySearch Advanced Launcher ended" -Level "INFO"
}

# Start the launcher
Main
