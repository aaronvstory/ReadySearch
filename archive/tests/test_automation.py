"""
Test script for ReadySearch automation with comprehensive testing.
Tests the specific case: "Ghafoor Nadery" name search with popup handling.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from readysearch_automation import BrowserController, ResultParser, NameMatcher
from playwright.async_api import Browser


async def test_name_search(name: str, config: dict) -> dict:
    """Test search for a specific name."""
    print(f"\n🔍 Testing search for: {name}")
    
    browser_controller = BrowserController(config)
    
    try:
        # Start browser
        print("📱 Starting browser...")
        await browser_controller.start_browser()
        
        # Navigate to search page
        print("🌐 Navigating to ReadySearch...")
        success = await browser_controller.navigate_to_search_page()
        if not success:
            return {"status": "error", "error": "Failed to navigate to search page"}
        
        # Take initial screenshot
        await browser_controller.take_screenshot("screenshots/1_initial_page.png")
        print("📸 Screenshot saved: screenshots/1_initial_page.png")
        
        # Search for the name
        print(f"🔎 Searching for: {name}")
        search_result = await browser_controller.search_name(name)
        
        # Take screenshot after search
        await browser_controller.take_screenshot("screenshots/2_after_search.png")
        print("📸 Screenshot saved: screenshots/2_after_search.png")
        
        # Wait a bit for any delayed popups
        await asyncio.sleep(2)
        
        # Parse results
        print("📊 Parsing search results...")
        result_parser = ResultParser(browser_controller.page)
        extracted_results = await result_parser.extract_search_results()
        
        # Take final screenshot
        await browser_controller.take_screenshot("screenshots/3_final_results.png")
        print("📸 Screenshot saved: screenshots/3_final_results.png")
        
        # Analyze matches
        name_matcher = NameMatcher(strict_mode=True)
        match_found, matches = name_matcher.find_exact_matches(name, extracted_results)
        
        # Print results
        print(f"\n📋 Results for '{name}':")
        print(f"   Total results found: {len(extracted_results)}")
        print(f"   Exact matches found: {len(matches)}")
        
        if extracted_results:
            print("\n📑 All extracted results:")
            for i, result in enumerate(extracted_results[:10], 1):  # Show first 10
                print(f"   {i}. {result.name} ({result.location})")
        
        if matches:
            print("\n✅ Exact matches:")
            for i, match in enumerate(matches, 1):
                print(f"   {i}. {match.name} (confidence: {match.confidence_score:.2f})")
        else:
            print("\n❌ No exact matches found")
        
        return {
            "status": "success",
            "name": name,
            "total_results": len(extracted_results),
            "exact_matches": len(matches),
            "match_found": match_found,
            "all_results": [{"name": r.name, "location": r.location} for r in extracted_results[:5]],
            "exact_match_details": [{"name": m.name, "confidence": m.confidence_score} for m in matches]
        }
        
    except Exception as e:
        error_msg = f"Error during search: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Take error screenshot
        try:
            await browser_controller.take_screenshot("screenshots/error_screenshot.png")
            print("📸 Error screenshot saved: screenshots/error_screenshot.png")
        except:
            pass
            
        return {"status": "error", "error": error_msg}
        
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        await browser_controller.cleanup()


async def test_popup_handling(config: dict):
    """Test popup handling specifically."""
    print("\n🪟 Testing popup handling...")
    
    browser_controller = BrowserController(config)
    
    try:
        await browser_controller.start_browser()
        await browser_controller.navigate_to_search_page()
        
        # Wait for any popups to appear
        await asyncio.sleep(3)
        
        # Test popup handler directly
        popup_handler = browser_controller.popup_handler
        
        # Check for common popup patterns
        popup_found = await popup_handler.handle_modal_popups()
        if popup_found:
            print("✅ Modal popup detected and handled")
        
        readysearch_popup = await popup_handler.handle_readysearch_popups()
        if readysearch_popup:
            print("✅ ReadySearch-specific popup detected and handled")
        
        if not popup_found and not readysearch_popup:
            print("ℹ️  No popups detected (this is normal)")
            
        await browser_controller.take_screenshot("screenshots/popup_test.png")
        print("📸 Popup test screenshot saved: screenshots/popup_test.png")
        
    except Exception as e:
        print(f"❌ Popup test error: {str(e)}")
        
    finally:
        await browser_controller.cleanup()


async def main():
    """Main test function."""
    print("🚀 ReadySearch Automation Test Suite")
    print("="*50)
    
    # Create screenshots directory
    Path("screenshots").mkdir(exist_ok=True)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_automation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get configuration
    config = Config.get_config()
    
    # Test with headless=False for visual debugging
    config['headless'] = False  # Set to True for production
    config['delay'] = 1.0  # Faster for testing
    
    print(f"🔧 Configuration:")
    print(f"   Base URL: {config['base_url']}")
    print(f"   Headless mode: {config['headless']}")
    print(f"   Delay between searches: {config['delay']}s")
    
    # Test 1: Popup handling
    await test_popup_handling(config)
    
    # Test 2: Specific name - "Ghafoor Nadery"
    test_names = [
        "Ghafoor Nadery",
        "John Smith",  # Common name for comparison
        "Jane Doe"     # Another common name
    ]
    
    results = []
    for name in test_names:
        result = await test_name_search(name, config)
        results.append(result)
        
        # Wait between searches
        if name != test_names[-1]:
            print(f"⏳ Waiting {config['delay']}s before next search...")
            await asyncio.sleep(config['delay'])
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['name']}: {result['total_results']} results, {result['exact_matches']} exact matches")
        else:
            print(f"❌ {result.get('name', 'Unknown')}: {result.get('error', 'Unknown error')}")
    
    print("\n🎯 Specific Test Case: 'Ghafoor Nadery'")
    ghafoor_result = next((r for r in results if r.get('name') == 'Ghafoor Nadery'), None)
    
    if ghafoor_result:
        if ghafoor_result['status'] == 'success':
            print(f"   ✅ Search completed successfully")
            print(f"   📊 Total results: {ghafoor_result['total_results']}")
            print(f"   🎯 Exact matches: {ghafoor_result['exact_matches']}")
            
            if ghafoor_result['match_found']:
                print(f"   ✅ MATCH FOUND for 'Ghafoor Nadery'!")
                for match in ghafoor_result['exact_match_details']:
                    print(f"      - {match['name']} (confidence: {match['confidence']:.2f})")
            else:
                print(f"   ❌ No exact match found for 'Ghafoor Nadery'")
                if ghafoor_result['all_results']:
                    print(f"   📋 Similar results found:")
                    for result in ghafoor_result['all_results']:
                        print(f"      - {result['name']} ({result['location']})")
        else:
            print(f"   ❌ Search failed: {ghafoor_result.get('error', 'Unknown error')}")
    
    print("\n📸 Check the 'screenshots/' folder for visual verification")
    print("📝 Check 'test_automation.log' for detailed logs")
    print("\n✨ Test completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
