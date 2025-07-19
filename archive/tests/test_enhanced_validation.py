#!/usr/bin/env python3
"""
Test script to verify enhanced ReadySearch validation
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from main import ReadySearchAutomation

async def test_single_search():
    """Test a single name search with detailed logging."""
    
    # Set up logging to see detailed output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("🔍 Testing Enhanced ReadySearch Validation")
    print("=" * 50)
    
    try:
        # Get configuration
        config = Config.get_config()
        
        # Override headless setting for testing
        config['headless'] = False  # Show browser for debugging
        
        # Create automation instance
        automation = ReadySearchAutomation(config)
        
        # Test name (use the name that was showing false positive)
        test_name = "Ghafoor Nadery"
        
        print(f"\n📋 Testing search for: '{test_name}'")
        print(f"Expected: Should properly validate if this is a real match or not")
        print()
        
        # Start browser
        print("🌐 Starting browser...")
        await automation.browser_controller.start_browser()
        
        # Navigate to search page
        print("🔗 Navigating to ReadySearch...")
        navigation_success = await automation.browser_controller.navigate_to_search_page()
        
        if not navigation_success:
            print("❌ Failed to navigate to search page")
            return
        
        print("✅ Successfully navigated to ReadySearch")
        
        # Perform enhanced search
        print(f"\n🔍 Searching for '{test_name}' with enhanced validation...")
        search_result = await automation._search_single_name_enhanced(test_name)
        
        # Display detailed results
        print("\n📊 SEARCH RESULTS:")
        print("=" * 30)
        
        status = search_result.get('status', 'Unknown')
        print(f"Status: {status}")
        
        statistics = search_result.get('statistics')
        if statistics:
            print(f"Total Results Found: {statistics.total_results_found}")
            print(f"Exact Matches: {statistics.exact_matches}")
            print(f"Partial Matches: {statistics.partial_matches}")
            print(f"No Matches: {statistics.no_matches}")
            print(f"Search Time: {statistics.search_time:.2f}s")
            
            if statistics.error_occurred:
                print(f"Error: {statistics.error_message}")
        
        exact_matches = search_result.get('exact_matches', [])
        if exact_matches:
            print(f"\n✅ EXACT MATCHES ({len(exact_matches)}):")
            for i, match in enumerate(exact_matches, 1):
                print(f"  {i}. {match.name}")
                print(f"     Confidence: {match.confidence_score:.2f}")
                print(f"     Match Type: {match.match_type}")
                if match.location:
                    print(f"     Location: {match.location}")
                if match.additional_info:
                    print(f"     Additional Info: {match.additional_info}")
                print()
        
        all_results = search_result.get('all_results', [])
        if all_results and not exact_matches:
            print(f"\n📋 ALL RESULTS FOUND ({len(all_results)}) - No Exact Matches:")
            for i, result in enumerate(all_results[:5], 1):  # Show first 5
                print(f"  {i}. {result.name}")
                print(f"     Match Type: {result.match_type}")
                print(f"     Confidence: {result.confidence_score:.2f}")
                if result.location:
                    print(f"     Location: {result.location}")
                print()
            
            if len(all_results) > 5:
                print(f"     ... and {len(all_results) - 5} more results")
        
        if search_result.get('error'):
            print(f"\n❌ ERROR: {search_result['error']}")
        
        print("\n" + "=" * 50)
        
        if status == 'Match':
            print("✅ CONCLUSION: This is a confirmed match with proper validation")
        elif status == 'No Match':
            print("❌ CONCLUSION: No exact matches found (correct validation)")
        else:
            print("⚠️  CONCLUSION: Search encountered an error")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            await automation.browser_controller.cleanup()
            print("\n🧹 Browser cleanup completed")
        except:
            pass

async def main():
    """Main test function."""
    await test_single_search()

if __name__ == "__main__":
    asyncio.run(main())
