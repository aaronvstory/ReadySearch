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

# Start development server
function Start-DevServer {
    param([int]$Port = $Config.BasePort)
    
    Write-ColoredOutput "Starting development server on port $Port..." -Color "Info" -Level "INFO"
    
    # Stop any existing process on the port
    if (Test-PortInUse -Port $Port) {
        Stop-ProcessOnPort -Port $Port
    }
    
    # Start the development server
    try {
        if (Test-Path "package.json") {
            $packageContent = Get-Content "package.json" | ConvertFrom-Json
            if ($packageContent.scripts.dev) {
                Write-ColoredOutput "Starting with NPM dev script..." -Color "Info" -Level "INFO"
                # For Vite, we need to set the port differently
                if ($packageContent.devDependencies.vite) {
                    Start-Process "cmd" -ArgumentList "/c", "npm", "run", "dev", "--", "--port", "$Port" -NoNewWindow
                } else {
                    $env:PORT = $Port
                    Start-Process "cmd" -ArgumentList "/c", "npm", "run", "dev" -NoNewWindow
                }
            } elseif ($packageContent.scripts.start) {
                Write-ColoredOutput "Starting with NPM start script..." -Color "Info" -Level "INFO"
                $env:PORT = $Port
                Start-Process "cmd" -ArgumentList "/c", "npm", "start" -NoNewWindow
            } else {
                Write-ColoredOutput "No dev/start script found in package.json" -Color "Error" -Level "ERROR"
                return $false
            }
        } else {
            Write-ColoredOutput "No package.json found" -Color "Error" -Level "ERROR"
            return $false
        }
        
        # Wait a moment and check if server started
        Start-Sleep -Seconds 3
        if (Test-PortInUse -Port $Port) {
            Write-ColoredOutput "Development server started successfully on port $Port" -Color "Success" -Level "SUCCESS"
            Write-ColoredOutput "Local URL: http://localhost:$Port" -Color "Success" -Level "SUCCESS"
            return $true
        } else {
            Write-ColoredOutput "Failed to start development server" -Color "Error" -Level "ERROR"
            return $false
        }
        
    } catch {
        Write-ColoredOutput "Error starting development server: $_" -Color "Error" -Level "ERROR"
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
    Write-Host "Development Options:" -ForegroundColor $Colors.Info
    Write-Host "  1. 🔧 Initialize Project Structure" -ForegroundColor $Colors.Prompt
    Write-Host "  2. 🏗️  Build Project" -ForegroundColor $Colors.Prompt
    Write-Host "  3. 🧪 Run Tests" -ForegroundColor $Colors.Prompt
    Write-Host "  4. 🚀 Start Development Server" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "Deployment & Tunneling:" -ForegroundColor $Colors.Info
    Write-Host "  5. 🌐 Start Ngrok Tunnel" -ForegroundColor $Colors.Prompt
    Write-Host "  6. 📊 Show Ngrok Connections" -ForegroundColor $Colors.Prompt
    Write-Host "  7. 🛑 Stop All Ngrok Tunnels" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "Combined Actions:" -ForegroundColor $Colors.Info
    Write-Host "  8. 🚀🌐 Start Dev Server + Ngrok" -ForegroundColor $Colors.Prompt
    Write-Host "  9. 🔄 Full Deploy (Build + Server + Tunnel)" -ForegroundColor $Colors.Prompt
    Write-Host ""
    Write-Host "System:" -ForegroundColor $Colors.Info
    Write-Host " 10. 🔍 Check System Status" -ForegroundColor $Colors.Prompt
    Write-Host " 11. 📋 Show Process Monitor" -ForegroundColor $Colors.Prompt
    Write-Host "  0. ❌ Exit" -ForegroundColor $Colors.Error
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $Colors.Header
}

# Process monitor
function Show-ProcessMonitor {
    Write-ColoredOutput "Development Process Monitor" -Color "Header" -Level "HEADER"
    Write-Host ""
    
    # Check ports
    $ports = @($Config.BasePort, 3000, 5173, 5174, 4040, 8080)
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
    $devProcesses = @("node", "npm", "ngrok", "code")
    foreach ($processName in $devProcesses) {
        $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
        if ($processes) {
            foreach ($proc in $processes) {
                Write-Host "  $($proc.ProcessName) (PID: $($proc.Id)) - CPU: $($proc.CPU)" -ForegroundColor $Colors.Success
            }
        }
    }
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
            "build" { Build-Project; exit }
            "test" { Test-Project; exit }
            "server" { Start-DevServer; Read-Host "Press Enter to exit"; exit }
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
                Initialize-ProjectStructure
                Read-Host "Press Enter to continue"
            }
            "2" {
                Build-Project
                Read-Host "Press Enter to continue"
            }
            "3" {
                Test-Project
                Read-Host "Press Enter to continue"
            }
            "4" {
                Start-DevServer
                Read-Host "Press Enter to continue"
            }
            "5" {
                Start-NgrokTunnel
                Read-Host "Press Enter to continue"
            }
            "6" {
                Show-NgrokConnections
                Read-Host "Press Enter to continue"
            }
            "7" {
                Stop-NgrokTunnels
                Read-Host "Press Enter to continue"
            }
            "8" {
                if (Start-DevServer) {
                    Start-Sleep -Seconds 3
                    Start-NgrokTunnel
                }
                Read-Host "Press Enter to continue"
            }
            "9" {
                if (Build-Project) {
                    if (Start-DevServer) {
                        Start-Sleep -Seconds 3
                        Start-NgrokTunnel
                        Show-NgrokConnections
                    }
                }
                Read-Host "Press Enter to continue"
            }
            "10" {
                Show-SystemStatus
                Read-Host "Press Enter to continue"
            }
            "11" {
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
