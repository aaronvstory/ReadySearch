#!/usr/bin/env python3
"""
Test script to directly debug the ReadySearchAutomation issue
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_automation():
    """Test the ReadySearchAutomation directly"""
    
    logger.info("🔍 Starting ReadySearchAutomation test...")
    
    try:
        # Test configuration - use Config.get_config() to ensure all required keys
        config = Config.get_config()
        config.update({
            'log_level': 'DEBUG',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'test_readysearch_automation.log',
            'output_file': 'test_readysearch_results'
        })
        
        logger.info("📋 Configuration loaded successfully")
        logger.info(f"   - Headless: {config['headless']}")
        logger.info(f"   - Page timeout: {config['page_timeout']}")
        logger.info(f"   - Element timeout: {config['element_timeout']}")
        
        # Create automation instance
        logger.info("🚀 Creating ReadySearchAutomation instance...")
        automation = ReadySearchAutomation(config)
        logger.info("✅ ReadySearchAutomation instance created")
        
        # Create test search record
        search_record = SearchRecord(name="Andro Cutuk", birth_year=1975)
        logger.info(f"🎯 Created search record: {search_record.name}, {search_record.birth_year}")
        
        # Run automation
        logger.info("🔧 Running automation...")
        success = await automation.run_automation([search_record])
        logger.info(f"📊 Automation result: success={success}")
        
        # Check reporter
        logger.info(f"📋 Reporter results count: {len(automation.reporter.get_results())}")
        
        if automation.reporter.has_results():
            results = automation.reporter.get_results()
            logger.info(f"📄 Results: {results}")
        else:
            logger.warning("⚠️ No results found in reporter")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in automation test: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_automation())
    print(f"\n🎯 Final result: {'SUCCESS' if result else 'FAILED'}")