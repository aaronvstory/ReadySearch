"""
Comprehensive startup debugging script to identify "Failed to fetch" error
"""

import asyncio
import logging
import sys
import os
import subprocess
import socket
import platform
import time
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug_startup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def comprehensive_system_check():
    """Comprehensive system and environment check"""
    logger.info("🔍 Starting comprehensive system analysis...")
    
    # 1. System Information
    logger.info("📊 System Information:")
    logger.info(f"   Platform: {platform.platform()}")
    logger.info(f"   Python Version: {platform.python_version()}")
    logger.info(f"   Architecture: {platform.architecture()}")
    logger.info(f"   Processor: {platform.processor()}")
    logger.info(f"   Machine: {platform.machine()}")
    
    # 2. Network Check
    logger.info("🌐 Network Connectivity Check:")
    try:
        # Test basic connectivity
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        logger.info("   ✅ DNS connectivity: OK")
        
        # Test HTTP connectivity
        socket.create_connection(("www.google.com", 80), timeout=5)
        logger.info("   ✅ HTTP connectivity: OK")
        
        # Test HTTPS connectivity
        socket.create_connection(("www.google.com", 443), timeout=5)
        logger.info("   ✅ HTTPS connectivity: OK")
        
    except Exception as e:
        logger.error(f"   ❌ Network connectivity failed: {str(e)}")
        return False
    
    # 3. Process Check
    logger.info("🔧 Process Analysis:")
    try:
        # Check for existing Chrome processes
        result = subprocess.run(
            ["tasklist", "/fi", "imagename eq chrome.exe"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "chrome.exe" in result.stdout:
            logger.info("   ⚠️ Existing Chrome processes found")
            logger.info(f"   Chrome processes: {result.stdout.count('chrome.exe')}")
        else:
            logger.info("   ✅ No existing Chrome processes")
            
        # Check for existing Python processes
        result = subprocess.run(
            ["tasklist", "/fi", "imagename eq python.exe"],
            capture_output=True,
            text=True,
            timeout=10
        )
        python_count = result.stdout.count('python.exe')
        logger.info(f"   Python processes: {python_count}")
        
    except Exception as e:
        logger.warning(f"   ⚠️ Process check failed: {str(e)}")
    
    # 4. Dependency Check
    logger.info("📦 Dependency Analysis:")
    dependencies = [
        "playwright", "asyncio", "pandas", "logging", "pathlib", "dataclasses"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"   ✅ {dep}: Available")
        except ImportError as e:
            logger.error(f"   ❌ {dep}: Missing - {str(e)}")
            return False
    
    # 5. Playwright Check
    logger.info("🎭 Playwright Analysis:")
    try:
        from playwright.async_api import async_playwright
        
        # Test Playwright initialization
        playwright = await async_playwright().start()
        logger.info("   ✅ Playwright started successfully")
        
        # Test browser availability
        try:
            browser = await playwright.chromium.launch(headless=True)
            logger.info("   ✅ Chromium browser available")
            await browser.close()
        except Exception as e:
            logger.error(f"   ❌ Chromium launch failed: {str(e)}")
            return False
            
        await playwright.stop()
        logger.info("   ✅ Playwright stopped successfully")
        
    except Exception as e:
        logger.error(f"   ❌ Playwright test failed: {str(e)}")
        return False
    
    # 6. File System Check
    logger.info("📁 File System Analysis:")
    current_dir = Path.cwd()
    logger.info(f"   Current directory: {current_dir}")
    
    required_files = [
        "main.py", "config.py", "anthony_bek_test.json",
        "readysearch_automation/__init__.py",
        "readysearch_automation/browser_controller.py"
    ]
    
    for file_path in required_files:
        file_full_path = current_dir / file_path
        if file_full_path.exists():
            logger.info(f"   ✅ {file_path}: Found")
        else:
            logger.error(f"   ❌ {file_path}: Missing")
            return False
    
    # 7. Memory and Resource Check
    logger.info("💾 Resource Analysis:")
    try:
        import psutil
        memory = psutil.virtual_memory()
        logger.info(f"   Available memory: {memory.available / (1024**3):.1f} GB")
        logger.info(f"   Memory usage: {memory.percent}%")
        
        disk = psutil.disk_usage('/')
        logger.info(f"   Available disk: {disk.free / (1024**3):.1f} GB")
        
    except ImportError:
        logger.warning("   ⚠️ psutil not available for detailed resource check")
    
    logger.info("✅ Comprehensive system analysis completed")
    return True

async def test_minimal_automation():
    """Test minimal automation to identify failure point"""
    logger.info("🧪 Testing minimal automation...")
    
    try:
        # Step 1: Import modules
        logger.info("📦 Step 1: Importing modules...")
        from readysearch_automation import InputLoader, SearchRecord
        logger.info("   ✅ InputLoader imported")
        
        from readysearch_automation.browser_controller import BrowserController
        logger.info("   ✅ BrowserController imported")
        
        # Step 2: Load configuration
        logger.info("⚙️ Step 2: Loading configuration...")
        from config import Config
        config = Config.get_config()
        logger.info("   ✅ Configuration loaded")
        
        # Step 3: Create browser controller
        logger.info("🌐 Step 3: Creating browser controller...")
        browser_controller = BrowserController(config)
        logger.info("   ✅ Browser controller created")
        
        # Step 4: Start browser
        logger.info("🚀 Step 4: Starting browser...")
        await browser_controller.start_browser()
        logger.info("   ✅ Browser started")
        
        # Step 5: Navigate to page
        logger.info("🔗 Step 5: Navigating to ReadySearch...")
        success = await browser_controller.navigate_to_search_page()
        if success:
            logger.info("   ✅ Navigation successful")
        else:
            logger.error("   ❌ Navigation failed")
            return False
        
        # Step 6: Cleanup
        logger.info("🧹 Step 6: Cleaning up...")
        await browser_controller.cleanup()
        logger.info("   ✅ Cleanup completed")
        
        logger.info("✅ Minimal automation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Minimal automation test failed: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        import traceback
        logger.error(f"   Full traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main debugging function"""
    logger.info("🔍 Starting comprehensive debugging session...")
    
    # Run system check
    system_ok = await comprehensive_system_check()
    if not system_ok:
        logger.error("❌ System check failed - cannot proceed")
        return
    
    # Test minimal automation
    automation_ok = await test_minimal_automation()
    if not automation_ok:
        logger.error("❌ Minimal automation test failed")
        return
    
    logger.info("🎉 All debugging tests passed!")

if __name__ == "__main__":
    asyncio.run(main())