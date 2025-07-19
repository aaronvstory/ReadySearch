#!/usr/bin/env python3
"""
Quick test to verify browser visibility and automation functionality
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import ReadySearchAutomation
from config import Config
from readysearch_automation.input_loader import SearchRecord

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_visible_browser():
    """Test automation with visible browser"""
    
    logger.info("🔍 Starting browser visibility test...")
    
    try:
        # Configuration with visible browser
        config = Config.get_config()
        config.update({
            'headless': False,  # VISIBLE BROWSER
            'delay': 1.5,
            'log_level': 'INFO',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'browser_test.log',
            'output_file': 'browser_test_results'
        })
        
        logger.info("📋 Configuration with VISIBLE BROWSER:")
        logger.info(f"   - Headless: {config['headless']}")
        logger.info(f"   - Browser should be: {'VISIBLE' if not config['headless'] else 'HIDDEN'}")
        
        # Create automation instance
        logger.info("🚀 Creating ReadySearchAutomation with visible browser...")
        automation = ReadySearchAutomation(config)
        logger.info("✅ Automation instance created")
        
        # Create test search record
        search_record = SearchRecord(name="Andro Cutuk", birth_year=1975)
        logger.info(f"🎯 Testing: {search_record.name}, born {search_record.birth_year}")
        
        # Run automation
        logger.info("🔧 Starting automation... BROWSER WINDOW SHOULD APPEAR NOW!")
        success = await automation.run_automation([search_record])
        logger.info(f"📊 Automation result: success={success}")
        
        # Check results
        if automation.reporter.has_results():
            results = automation.reporter.get_results()
            logger.info(f"📄 Found {len(results)} results:")
            for i, result in enumerate(results):
                logger.info(f"   Result {i+1}: {result}")
        else:
            logger.warning("⚠️ No results found")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in browser test: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🌟 BROWSER VISIBILITY TEST")
    print("📋 This test should open a visible browser window")
    print("👀 Watch for Chrome/Edge browser window to appear")
    print("")
    
    result = asyncio.run(test_visible_browser())
    print(f"\n🎯 Final result: {'SUCCESS' if result else 'FAILED'}")
    
    if result:
        print("✅ Browser should have been visible during automation")
    else:
        print("❌ Test failed - check logs for details")