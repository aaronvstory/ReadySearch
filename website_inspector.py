#!/usr/bin/env python3
"""
Website Inspector - Check ReadySearch page structure and find correct selectors
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

async def inspect_readysearch_website():
    """Inspect ReadySearch website to find correct selectors"""
    
    print("🔍 READYSEARCH WEBSITE INSPECTOR")
    print("🎯 Finding correct selectors for automation")
    print("")
    
    async with async_playwright() as p:
        try:
            print("🚀 Launching browser...")
            browser = await p.chromium.launch(headless=False)  # Visible browser for inspection
            context = await browser.new_context()
            page = await context.new_page()
            
            print("🌐 Navigating to ReadySearch...")
            await page.goto("https://readysearch.com.au/products?person", wait_until="networkidle")
            
            print("✅ Page loaded, taking screenshot...")
            await page.screenshot(path="readysearch_inspection.png")
            
            print("🔍 Inspecting page structure...")
            
            # Find all input elements
            print("\n📋 ALL INPUT ELEMENTS:")
            inputs = await page.query_selector_all("input")
            for i, input_elem in enumerate(inputs):
                input_type = await input_elem.get_attribute("type") or "text"
                input_name = await input_elem.get_attribute("name") or ""
                input_id = await input_elem.get_attribute("id") or ""
                input_class = await input_elem.get_attribute("class") or ""
                input_placeholder = await input_elem.get_attribute("placeholder") or ""
                
                print(f"   Input {i+1}: type='{input_type}' name='{input_name}' id='{input_id}' class='{input_class}' placeholder='{input_placeholder}'")
            
            # Find all select elements  
            print("\n📋 ALL SELECT ELEMENTS:")
            selects = await page.query_selector_all("select")
            for i, select_elem in enumerate(selects):
                select_name = await select_elem.get_attribute("name") or ""
                select_id = await select_elem.get_attribute("id") or ""
                select_class = await select_elem.get_attribute("class") or ""
                
                # Get options
                options = await select_elem.query_selector_all("option")
                option_count = len(options)
                first_few_options = []
                for j, option in enumerate(options[:5]):
                    option_value = await option.get_attribute("value") or ""
                    option_text = await option.inner_text()
                    first_few_options.append(f"{option_value}:{option_text}")
                
                print(f"   Select {i+1}: name='{select_name}' id='{select_id}' class='{select_class}' options={option_count}")
                print(f"      First options: {first_few_options}")
            
            # Find all buttons
            print("\n📋 ALL BUTTON ELEMENTS:")
            buttons = await page.query_selector_all("button, input[type='submit'], .sch_but")
            for i, button_elem in enumerate(buttons):
                button_type = await button_elem.get_attribute("type") or ""
                button_class = await button_elem.get_attribute("class") or ""
                button_id = await button_elem.get_attribute("id") or ""
                button_text = await button_elem.inner_text()
                
                print(f"   Button {i+1}: type='{button_type}' class='{button_class}' id='{button_id}' text='{button_text.strip()}'")
            
            # Test if we can find a name input field
            print("\n🎯 TESTING SELECTORS:")
            
            # Test various selectors
            test_selectors = [
                "input[type='text']",
                "input[name='name']", 
                "input[placeholder*='name']",
                "#name",
                ".name-input",
                "input[name*='search']",
                "input.search",
                "input"
            ]
            
            for selector in test_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        print(f"   ✅ FOUND: {selector} (visible: {is_visible})")
                        
                        # Try to interact with it
                        if is_visible:
                            try:
                                await element.click()
                                await element.fill("TEST")
                                print(f"      ✅ Can interact with {selector}")
                                await element.clear()
                            except Exception as e:
                                print(f"      ⚠️ Cannot interact with {selector}: {e}")
                    else:
                        print(f"   ❌ NOT FOUND: {selector}")
                except Exception as e:
                    print(f"   ❌ ERROR with {selector}: {e}")
            
            # Test year selectors
            print("\n🎯 TESTING YEAR SELECTORS:")
            year_selectors = [
                "select[name='yobs']",
                "select[name='yobe']", 
                "select[name*='year']",
                "select[name*='birth']",
                "select"
            ]
            
            for selector in year_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        print(f"   ✅ FOUND: {selector} (visible: {is_visible})")
                    else:
                        print(f"   ❌ NOT FOUND: {selector}")
                except Exception as e:
                    print(f"   ❌ ERROR with {selector}: {e}")
            
            print("\n📸 Screenshot saved as: readysearch_inspection.png")
            print("🎯 Use this information to update selectors in config.py")
            
            # Wait a bit so user can see the page
            print("\n⏳ Keeping browser open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ Error inspecting website: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(inspect_readysearch_website())