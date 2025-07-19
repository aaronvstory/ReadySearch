"""
Enhanced browser initialization debugging with comprehensive cleanup and diagnostics.
This script addresses the "Failed to fetch" error by implementing thorough cleanup and enhanced logging.
"""

import asyncio
import logging
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_browser_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBrowserDebugger:
    """Enhanced browser debugging with comprehensive cleanup and diagnostics."""
    
    def __init__(self):
        self.browser_controller = None
        self.config = None
        
    async def comprehensive_cleanup(self):
        """Perform comprehensive cleanup of browser processes and sessions."""
        logger.info("🧹 Starting comprehensive cleanup...")
        
        # 1. Force cleanup session manager
        try:
            logger.info("📋 Cleaning up session manager...")
            from readysearch_automation import session_manager
            await session_manager.force_cleanup()
            logger.info("   ✅ Session manager cleaned up")
        except Exception as e:
            logger.warning(f"   ⚠️ Session manager cleanup failed: {str(e)}")
        
        # 2. Kill existing Chrome processes
        logger.info("🔧 Killing existing Chrome processes...")
        try:
            # Windows process killing
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe", "/T"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("   ✅ Chrome processes killed")
            else:
                logger.info("   ℹ️ No Chrome processes to kill")
        except Exception as e:
            logger.warning(f"   ⚠️ Chrome process cleanup failed: {str(e)}")
        
        # 3. Kill existing Python processes (except current)
        logger.info("🐍 Checking for conflicting Python processes...")
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                current_pid = os.getpid()
                python_processes = []
                
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split('","')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            if pid.isdigit() and int(pid) != current_pid:
                                python_processes.append(pid)
                
                if python_processes:
                    logger.info(f"   Found {len(python_processes)} other Python processes")
                    for pid in python_processes:
                        logger.info(f"   Python process PID: {pid}")
                else:
                    logger.info("   ✅ No conflicting Python processes found")
        except Exception as e:
            logger.warning(f"   ⚠️ Python process check failed: {str(e)}")
        
        # 4. Clean up temporary files
        logger.info("🗂️ Cleaning up temporary files...")
        try:
            temp_patterns = [
                "debug_*.png",
                "manual_test_*.png",
                "*.tmp",
                "playwright_*"
            ]
            
            cleaned_files = 0
            for pattern in temp_patterns:
                for file_path in Path(".").glob(pattern):
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                    except Exception as e:
                        logger.debug(f"   Could not delete {file_path}: {str(e)}")
            
            logger.info(f"   ✅ Cleaned up {cleaned_files} temporary files")
        except Exception as e:
            logger.warning(f"   ⚠️ Temporary file cleanup failed: {str(e)}")
        
        # 5. Wait for processes to fully terminate
        logger.info("⏳ Waiting for processes to fully terminate...")
        await asyncio.sleep(3)
        
        logger.info("✅ Comprehensive cleanup completed")
    
    async def enhanced_browser_startup(self):
        """Enhanced browser startup with comprehensive logging and error recovery."""
        logger.info("🚀 Starting enhanced browser initialization...")
        
        try:
            # Step 1: Load configuration
            logger.info("⚙️ Step 1: Loading configuration...")
            from config import Config
            self.config = Config.get_config()
            logger.info("   ✅ Configuration loaded successfully")
            logger.info(f"   📊 Config: headless={self.config['headless']}, timeout={self.config['page_timeout']}ms")
            
            # Step 2: Import browser controller
            logger.info("📦 Step 2: Importing browser controller...")
            from readysearch_automation.browser_controller import BrowserController
            logger.info("   ✅ Browser controller imported")
            
            # Step 3: Create browser controller instance
            logger.info("🏗️ Step 3: Creating browser controller instance...")
            self.browser_controller = BrowserController(self.config)
            logger.info("   ✅ Browser controller instance created")
            
            # Step 4: Initialize Playwright with enhanced logging
            logger.info("🎭 Step 4: Initializing Playwright...")
            from playwright.async_api import async_playwright
            
            # Test Playwright initialization separately
            playwright = await async_playwright().start()
            logger.info("   ✅ Playwright started successfully")
            
            # Test browser availability
            logger.info("🌐 Step 5: Testing browser availability...")
            browser = await playwright.chromium.launch(
                headless=self.config['headless'],
                args=self.config['browser_args']
            )
            logger.info("   ✅ Browser launched successfully")
            
            # Test context creation
            logger.info("📄 Step 6: Testing context creation...")
            context = await browser.new_context(
                user_agent=self.config['user_agent'],
                viewport={'width': 1920, 'height': 1080},
                locale='en-AU',
                timezone_id='Australia/Sydney'
            )
            logger.info("   ✅ Browser context created successfully")
            
            # Test page creation
            logger.info("📃 Step 7: Testing page creation...")
            page = await context.new_page()
            logger.info("   ✅ Page created successfully")
            
            # Test basic navigation
            logger.info("🔗 Step 8: Testing basic navigation...")
            try:
                response = await page.goto("https://www.google.com", timeout=10000)
                logger.info(f"   ✅ Navigation successful, status: {response.status}")
            except Exception as e:
                logger.error(f"   ❌ Navigation failed: {str(e)}")
                raise
            
            # Clean up test browser
            logger.info("🧹 Step 9: Cleaning up test browser...")
            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()
            logger.info("   ✅ Test browser cleaned up")
            
            # Step 10: Now test the actual browser controller
            logger.info("🎯 Step 10: Testing actual browser controller...")
            await self.browser_controller.start_browser()
            logger.info("   ✅ Browser controller started successfully")
            
            # Step 11: Test navigation to ReadySearch
            logger.info("🔗 Step 11: Testing ReadySearch navigation...")
            navigation_success = await self.browser_controller.navigate_to_search_page()
            if navigation_success:
                logger.info("   ✅ ReadySearch navigation successful")
            else:
                logger.error("   ❌ ReadySearch navigation failed")
                raise Exception("ReadySearch navigation failed")
            
            # Step 12: Test basic page interaction
            logger.info("🔍 Step 12: Testing page interaction...")
            try:
                # Take a screenshot to verify page loaded
                await self.browser_controller.take_screenshot("enhanced_debug_page_loaded.png")
                logger.info("   ✅ Screenshot taken successfully")
                
                # Test finding search input
                search_input = await self.browser_controller._find_search_input()
                if search_input:
                    logger.info("   ✅ Search input found")
                else:
                    logger.warning("   ⚠️ Search input not found")
                
            except Exception as e:
                logger.error(f"   ❌ Page interaction test failed: {str(e)}")
                raise
            
            logger.info("🎉 Enhanced browser initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced browser initialization failed: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            import traceback
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            return False
        
        finally:
            # Always cleanup
            if self.browser_controller:
                try:
                    await self.browser_controller.cleanup()
                    logger.info("🧹 Browser controller cleaned up")
                except Exception as e:
                    logger.error(f"❌ Browser controller cleanup failed: {str(e)}")
    
    async def test_main_automation_startup(self):
        """Test the main automation startup process with enhanced debugging."""
        logger.info("🚀 Testing main automation startup process...")
        
        try:
            # Step 1: Import all required modules
            logger.info("📦 Step 1: Importing modules...")
            from readysearch_automation import InputLoader, SearchRecord
            from config import Config
            logger.info("   ✅ Modules imported successfully")
            
            # Step 2: Load configuration
            logger.info("⚙️ Step 2: Loading configuration...")
            config = Config.get_config()
            logger.info("   ✅ Configuration loaded")
            
            # Step 3: Test input loading
            logger.info("📄 Step 3: Testing input loading...")
            input_loader = InputLoader(config['input_file'])
            
            # Check if input file exists
            input_file_path = Path(config['input_file'])
            if not input_file_path.exists():
                logger.error(f"   ❌ Input file not found: {config['input_file']}")
                return False
            
            # Load search records
            search_records = input_loader.load_names()
            logger.info(f"   ✅ Loaded {len(search_records)} search records")
            
            # Step 4: Test automation class creation
            logger.info("🏗️ Step 4: Creating automation instance...")
            from main import ReadySearchAutomation
            automation = ReadySearchAutomation(config)
            logger.info("   ✅ Automation instance created")
            
            # Step 5: Test session management
            logger.info("📋 Step 5: Testing session management...")
            from readysearch_automation import session_manager
            session_id = f"test_{int(time.time())}"
            
            session_started = await session_manager.start_session(session_id)
            if session_started:
                logger.info("   ✅ Test session started successfully")
                await session_manager.end_session(session_id)
                logger.info("   ✅ Test session ended successfully")
            else:
                logger.error("   ❌ Test session failed to start")
                return False
            
            # Step 6: Test connectivity
            logger.info("🌐 Step 6: Testing connectivity...")
            connectivity_ok = await automation._test_connectivity()
            if connectivity_ok:
                logger.info("   ✅ Connectivity test passed")
            else:
                logger.error("   ❌ Connectivity test failed")
                return False
            
            logger.info("🎉 Main automation startup test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Main automation startup test failed: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            import traceback
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            return False
    
    async def run_comprehensive_debug(self):
        """Run comprehensive debugging session."""
        logger.info("🔍 Starting comprehensive browser debugging session...")
        
        try:
            # Phase 1: Comprehensive cleanup
            await self.comprehensive_cleanup()
            
            # Phase 2: Enhanced browser startup
            browser_success = await self.enhanced_browser_startup()
            if not browser_success:
                logger.error("❌ Enhanced browser startup failed")
                return False
            
            # Phase 3: Test main automation startup
            automation_success = await self.test_main_automation_startup()
            if not automation_success:
                logger.error("❌ Main automation startup test failed")
                return False
            
            logger.info("🎉 Comprehensive debugging completed successfully!")
            logger.info("✅ All tests passed - the automation should now work correctly")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Comprehensive debugging failed: {str(e)}")
            return False

async def main():
    """Main debugging function."""
    logger.info("🚀 Starting Enhanced Browser Debugging...")
    
    debugger = EnhancedBrowserDebugger()
    success = await debugger.run_comprehensive_debug()
    
    if success:
        logger.info("✅ Enhanced browser debugging completed successfully!")
        logger.info("🎯 The automation should now work correctly. Try running main.py again.")
    else:
        logger.error("❌ Enhanced browser debugging failed!")
        logger.error("🔍 Check the logs above for specific error details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())