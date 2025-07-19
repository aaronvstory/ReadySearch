#!/usr/bin/env python3
"""
EMERGENCY DIAGNOSTIC - Fast test to identify automation bottlenecks
"""

import asyncio
import sys
import logging
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import ReadySearchAutomation
from config import Config
from readysearch_automation.input_loader import SearchRecord

# Set up DETAILED logging to capture everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emergency_diagnostic.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def emergency_test():
    """Emergency test with aggressive timeouts for speed"""
    
    logger.info("🚨 EMERGENCY DIAGNOSTIC TEST STARTING")
    logger.info("🎯 Goal: Identify why automation takes 5+ minutes and returns No Match")
    
    try:
        # AGGRESSIVE configuration for SPEED
        config = Config.get_config()
        config.update({
            'headless': True,  # HEADLESS for speed
            'delay': 0.5,  # Minimal delay
            'page_timeout': 15000,  # 15s max per action (reduced from 30s)
            'element_timeout': 3000,  # 3s max per element (reduced from 5s)
            'max_retries': 1,  # Only 1 retry (reduced from 2)
            'log_level': 'DEBUG',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'emergency_diagnostic.log',
            'output_file': 'emergency_results'
        })
        
        logger.info("📋 AGGRESSIVE SPEED CONFIGURATION:")
        logger.info(f"   - Headless: {config['headless']} (for speed)")
        logger.info(f"   - Page timeout: {config['page_timeout']}ms (reduced)")
        logger.info(f"   - Element timeout: {config['element_timeout']}ms (reduced)")
        logger.info(f"   - Max retries: {config['max_retries']} (reduced)")
        logger.info(f"   - Delay: {config['delay']}s (minimal)")
        
        # Create automation instance
        logger.info("🚀 Creating SPEED-OPTIMIZED automation instance...")
        start_create = time.time()
        automation = ReadySearchAutomation(config)
        create_time = time.time() - start_create
        logger.info(f"✅ Automation created in {create_time:.2f}s")
        
        # Test search record
        search_record = SearchRecord(name="Andro Cutuk", birth_year=1975)
        logger.info(f"🎯 Testing: {search_record.name}, born {search_record.birth_year}")
        
        # Run automation with detailed timing
        logger.info("🔧 STARTING AUTOMATION - MONITORING ALL PHASES...")
        overall_start = time.time()
        
        success = await automation.run_automation([search_record])
        
        overall_end = time.time()
        total_time = overall_end - overall_start
        
        logger.info(f"📊 AUTOMATION COMPLETED:")
        logger.info(f"   - Success: {success}")
        logger.info(f"   - Total time: {total_time:.2f}s ({total_time:.0f}ms)")
        logger.info(f"   - Target time: <30s")
        logger.info(f"   - Performance: {'ACCEPTABLE' if total_time < 30 else 'UNACCEPTABLE'}")
        
        # Detailed results analysis
        reporter_results = automation.reporter.get_results()
        logger.info(f"📋 RESULTS ANALYSIS:")
        logger.info(f"   - Reporter has {len(reporter_results)} results")
        
        if reporter_results:
            for i, result in enumerate(reporter_results):
                logger.info(f"   - Result {i+1}: {result}")
        else:
            logger.warning("⚠️ NO RESULTS FOUND - THIS IS THE PROBLEM!")
            
        # Detailed diagnostics
        logger.info("🔍 DIAGNOSTIC SUMMARY:")
        if total_time > 30:
            logger.error(f"❌ PERFORMANCE FAILURE: {total_time:.2f}s > 30s target")
        if not success:
            logger.error("❌ AUTOMATION FAILURE: success=False")
        if not reporter_results:
            logger.error("❌ RESULTS FAILURE: No results extracted")
            
        return {
            'success': success,
            'total_time': total_time,
            'results_count': len(reporter_results),
            'results': reporter_results
        }
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'total_time': 0,
            'results_count': 0
        }

if __name__ == "__main__":
    print("🚨 EMERGENCY DIAGNOSTIC TEST")
    print("🎯 Aggressive speed optimization + detailed logging")
    print("📊 Target: <30s with real results")
    print("")
    
    result = asyncio.run(emergency_test())
    
    print(f"\n🎯 DIAGNOSTIC RESULTS:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Time: {result.get('total_time', 0):.2f}s")
    print(f"   Results: {result.get('results_count', 0)}")
    
    if result.get('total_time', 0) > 30:
        print("❌ PERFORMANCE CRITICAL: Exceeds 30s target")
    if not result.get('success', False):
        print("❌ AUTOMATION CRITICAL: Failed to complete")
    if result.get('results_count', 0) == 0:
        print("❌ RESULTS CRITICAL: No matches extracted")
        
    print("\n📊 See emergency_diagnostic.log for detailed analysis")