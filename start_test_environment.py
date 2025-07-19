#!/usr/bin/env python3
"""
Quick test environment starter for ReadySearch.
Starts the enhanced API server and provides instructions for frontend.
"""

import subprocess
import sys
import time
import requests
import os

def start_api_server():
    """Start the enhanced API server."""
    print("🚀 Starting Enhanced ReadySearch API Server...")
    
    try:
        # Start the enhanced API server
        api_process = subprocess.Popen([
            sys.executable, "enhanced_api_server.py"
        ], cwd=os.getcwd())
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is running
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Enhanced API Server started successfully!")
                print(f"🎯 Status: {data['status']}")
                print(f"📡 URL: http://localhost:5000")
                print(f"🔧 Features: {', '.join(data['features'])}")
                return api_process
            else:
                print(f"❌ API Server health check failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ API Server not responding: {str(e)}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {str(e)}")
        return None

def main():
    print("🧪 READYSEARCH TEST ENVIRONMENT STARTER")
    print("=" * 60)
    print("This script starts the enhanced API server for testing.")
    print()
    
    # Start API server
    api_process = start_api_server()
    
    if not api_process:
        print("❌ Failed to start API server. Cannot continue.")
        return
    
    print()
    print("📋 NEXT STEPS:")
    print("1. 🌐 Start Frontend: npm run dev (in another terminal)")
    print("2. 🧪 Run Integration Test: python test_complete_integration.py")
    print("3. 🌍 Open Browser: http://localhost:5173")
    print()
    print("🎯 TESTING FRIEND'S REQUIREMENTS:")
    print("   - Use sample names: John Smith,1990 or Mike Johnson,1985")
    print("   - Check for PARTIAL MATCH on middle name additions")
    print("   - Check for PARTIAL MATCH on name variations")
    print("   - Verify detailed match reasoning is displayed")
    print()
    print("⚡ API Server is running. Press Ctrl+C to stop.")
    
    try:
        # Keep the API server running
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping API server...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
        print("✅ API server stopped.")

if __name__ == "__main__":
    main()