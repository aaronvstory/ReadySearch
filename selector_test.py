#!/usr/bin/env python3
"""
Direct selector test to verify our selectors work
"""

import asyncio
from playwright.async_api import async_playwright

async def test_selectors():
    """Test our verified selectors directly"""
    
    print("🔍 DIRECT SELECTOR TEST")
    print("🎯 Testing verified selectors on ReadySearch")
    print("")
    
    async with async_playwright() as p:
        try:
            print("🚀 Launching browser...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("🌐 Navigating to ReadySearch...")
            await page.goto("https://readysearch.com.au/products?person", wait_until="networkidle")
            print("✅ Page loaded")
            
            # Test our verified selectors
            print("\n🎯 TESTING VERIFIED SELECTORS:")
            
            selectors_to_test = {
                'name_input': 'input[name="search"]',
                'birth_year_start': 'select[name="yobs"]', 
                'birth_year_end': 'select[name="yobe"]',
                'search_button': '.sch_but'
            }
            
            all_working = True
            
            for name, selector in selectors_to_test.items():
                try:
                    print(f"   Testing {name}: {selector}")
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        is_visible = await element.is_visible()
                        print(f"   ✅ FOUND and {'VISIBLE' if is_visible else 'HIDDEN'}: {selector}")
                        
                        if name == 'name_input' and is_visible:
                            # Test interaction
                            await element.click()
                            await element.fill("TEST NAME")
                            value = await element.input_value()
                            print(f"      ✅ Can interact - entered: '{value}'")
                            await element.clear()
                        
                    else:
                        print(f"   ❌ NOT FOUND: {selector}")
                        all_working = False
                        
                except Exception as e:
                    print(f"   ❌ ERROR with {selector}: {e}")
                    all_working = False
            
            print(f"\n📊 SELECTOR TEST RESULT: {'✅ ALL WORKING' if all_working else '❌ SOME FAILED'}")
            
            # Test the config loading
            print("\n🔧 TESTING CONFIG LOADING:")
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent))
            
            from config import Config
            config = Config.get_config()
            selectors = config.get('selectors', {})
            
            print(f"   Config name_input: '{selectors.get('name_input', 'NOT FOUND')}'")
            print(f"   Config birth_year_start: '{selectors.get('birth_year_start', 'NOT FOUND')}'")
            print(f"   Config birth_year_end: '{selectors.get('birth_year_end', 'NOT FOUND')}'")
            print(f"   Config search_button: '{selectors.get('search_button', 'NOT FOUND')}'")
            
            await asyncio.sleep(3)
            await browser.close()
            
            return all_working
            
        except Exception as e:
            print(f"❌ Error in selector test: {e}")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_selectors())
    print(f"\n🎯 Final result: {'SUCCESS' if result else 'FAILED'}")