#!/usr/bin/env python3
"""
Direct test of ReadySearch automation for Ghafoor Nadery
"""
import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from readysearch_automation.browser_controller import BrowserController
from readysearch_automation.result_parser import ResultParser
from readysearch_automation.name_matcher import NameMatcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_ghafoor_nadery_search():
    """Test searching for Ghafoor Nadery specifically."""
    print("🔍 Testing ReadySearch automation for: Ghafoor Nadery")
    
    # Set up config
    config = {
        'headless': False,  # Set to True for production
        'delay': 2.5,
        'timeout': 30000,
        'retries': 3
    }
    
    browser_controller = BrowserController(config)
    result_parser = ResultParser()
    name_matcher = NameMatcher()
    
    try:
        # Start browser
        print("📱 Starting browser...")
        await browser_controller.start_browser()
        
        # Navigate to ReadySearch
        print("🌐 Navigating to ReadySearch...")
        success = await browser_controller.navigate_to_search_page()
        if not success:
            print("❌ Failed to navigate to search page")
            return
            
        # Perform search
        print("🔎 Searching for: Ghafoor Nadery")
        search_success = await browser_controller.search_name("Ghafoor Nadery")
        if not search_success:
            print("❌ Search failed")
            return
            
        print("📊 Parsing search results...")
        
        # Get page content
        page_content = await browser_controller.get_page_content()
        
        # Parse results  
        all_results = result_parser.parse_search_results(page_content)
        print(f"📋 Total results found: {len(all_results)}")
        
        # Check for exact matches
        exact_matches = name_matcher.find_exact_matches("Ghafoor Nadery", all_results)
        print(f"🎯 Exact matches found: {len(exact_matches)}")
        
        if exact_matches:
            print("✅ MATCH FOUND!")
            for match in exact_matches:
                print(f"   - {match}")
        else:
            print("❌ No exact matches found")
            
        # Show first 10 results for verification
        if all_results:
            print("\n📑 First 10 results:")
            for i, result in enumerate(all_results[:10], 1):
                print(f"   {i}. {result}")
        
        return {
            'total_results': len(all_results),
            'exact_matches': len(exact_matches),
            'found': len(exact_matches) > 0,
            'all_results': all_results[:20]  # First 20 for verification
        }
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return {'error': str(e)}
        
    finally:
        print("🧹 Cleaning up...")
        await browser_controller.cleanup()

if __name__ == "__main__":
    result = asyncio.run(test_ghafoor_nadery_search())
    print(f"\n📊 Final Result: {result}")
