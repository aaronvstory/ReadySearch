#!/usr/bin/env python3
"""
GUI Testing with Playwright - Beauty and Functionality Test
"""

import asyncio
import time
from playwright.async_api import async_playwright
from pathlib import Path

async def test_gui_beauty_and_functionality():
    """Test the GUI for beauty and functionality using Playwright"""
    
    print("🎨 GUI BEAUTY & FUNCTIONALITY TEST")
    print("=" * 50)
    
    async with async_playwright() as p:
        try:
            # Launch browser
            print("🚀 Launching browser for GUI testing...")
            browser = await p.chromium.launch(headless=False)  # Visible for inspection
            context = await browser.new_context(viewport={'width': 1200, 'height': 800})
            page = await context.new_page()
            
            # Navigate to GUI
            print("🌐 Navigating to ReadySearch GUI...")
            await page.goto("http://localhost:5173", wait_until="networkidle")
            await page.wait_for_timeout(3000)  # Wait for React to load
            
            # Take initial screenshot
            print("📸 Taking initial screenshot...")
            await page.screenshot(path="gui_test_initial.png", full_page=True)
            
            # Check page title
            title = await page.title()
            print(f"📄 Page Title: {title}")
            
            # Look for key UI elements
            print("\n🔍 CHECKING GUI ELEMENTS:")
            
            # Check for the main container
            main_container = await page.query_selector("div#root")
            if main_container:
                print("   ✅ Main React container found")
            else:
                print("   ❌ Main React container not found")
            
            # Check for ReadySearch branding/title
            headings = await page.query_selector_all("h1, h2, h3, .title, .header")
            if headings:
                print(f"   ✅ Found {len(headings)} heading elements")
                for i, heading in enumerate(headings[:3]):  # Check first 3
                    text = await heading.inner_text()
                    print(f"      {i+1}. {text}")
            else:
                print("   ⚠️ No heading elements found")
            
            # Check for input fields
            inputs = await page.query_selector_all("input, textarea")
            if inputs:
                print(f"   ✅ Found {len(inputs)} input fields")
                for i, input_elem in enumerate(inputs[:3]):  # Check first 3
                    placeholder = await input_elem.get_attribute("placeholder")
                    input_type = await input_elem.get_attribute("type")
                    print(f"      {i+1}. Type: {input_type}, Placeholder: {placeholder}")
            else:
                print("   ❌ No input fields found")
            
            # Check for buttons
            buttons = await page.query_selector_all("button")
            if buttons:
                print(f"   ✅ Found {len(buttons)} buttons")
                for i, button in enumerate(buttons[:3]):  # Check first 3
                    text = await button.inner_text()
                    print(f"      {i+1}. {text}")
            else:
                print("   ❌ No buttons found")
            
            # Check for loading/progress indicators
            progress_elements = await page.query_selector_all(".progress, .loading, .spinner")
            if progress_elements:
                print(f"   ✅ Found {len(progress_elements)} progress/loading elements")
            
            # Check for results area
            results_areas = await page.query_selector_all(".results, .output, .data, table")
            if results_areas:
                print(f"   ✅ Found {len(results_areas)} results/data display areas")
            
            print("\n🎨 VISUAL DESIGN ASSESSMENT:")
            
            # Check for CSS framework usage (Tailwind indicators)
            body = await page.query_selector("body")
            body_classes = await body.get_attribute("class") if body else ""
            body_classes = body_classes or ""  # Ensure it's not None
            if "dark" in body_classes or "light" in body_classes:
                print("   ✅ Theme system detected (dark/light mode)")
            
            # Check for modern design elements
            modern_elements = await page.query_selector_all(".card, .shadow, .rounded, .border, .bg-")
            if modern_elements:
                print(f"   ✅ Found {len(modern_elements)} modern design elements")
            
            # Check for responsive design indicators
            responsive_elements = await page.query_selector_all("[class*='responsive'], [class*='sm:'], [class*='md:'], [class*='lg:']")
            if responsive_elements:
                print(f"   ✅ Responsive design elements detected ({len(responsive_elements)} elements)")
            
            print("\n🧪 FUNCTIONALITY TEST:")
            
            # Try to interact with the first input field
            first_input = await page.query_selector("input")
            if first_input:
                print("   📝 Testing input interaction...")
                await first_input.click()
                await first_input.fill("Test Name Input")
                
                # Check if input has value
                value = await first_input.input_value()
                if value == "Test Name Input":
                    print("   ✅ Input field works correctly")
                else:
                    print("   ❌ Input field not working properly")
                
                await first_input.clear()
            
            # Try to click the first button
            first_button = await page.query_selector("button")
            if first_button:
                button_text = await first_button.inner_text()
                print(f"   🔘 Testing button interaction: '{button_text}'")
                
                # Check if button is enabled
                is_disabled = await first_button.is_disabled()
                if not is_disabled:
                    print("   ✅ Button is clickable")
                    # We won't actually click to avoid triggering automation
                else:
                    print("   ⚠️ Button is disabled")
            
            # Test dark/light mode toggle if present
            theme_toggle = await page.query_selector("button[class*='theme'], button[class*='dark'], button[class*='mode'], .theme-toggle")
            if theme_toggle:
                print("   🌙 Theme toggle detected - testing...")
                await theme_toggle.click()
                await page.wait_for_timeout(1000)
                
                # Check if theme changed
                body_classes_after = await body.get_attribute("class") if body else ""
                body_classes_after = body_classes_after or ""  # Ensure it's not None
                if body_classes_after != body_classes:
                    print("   ✅ Theme toggle works correctly")
                else:
                    print("   ⚠️ Theme toggle might not be working")
            
            # Take final screenshot
            print("\n📸 Taking final screenshot...")
            await page.screenshot(path="gui_test_final.png", full_page=True)
            
            # Performance check
            print("\n⚡ PERFORMANCE CHECK:")
            
            # Measure page load time
            start_time = time.time()
            await page.reload(wait_until="networkidle")
            load_time = time.time() - start_time
            print(f"   ⏱️ Page reload time: {load_time:.2f}s")
            
            if load_time <= 3:
                print("   ✅ Good performance (≤3s)")
            elif load_time <= 5:
                print("   ⚠️ Acceptable performance (≤5s)")
            else:
                print("   ❌ Slow performance (>5s)")
            
            # Check for console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            await page.wait_for_timeout(2000)
            
            if console_errors:
                print(f"   ⚠️ Found {len(console_errors)} console errors:")
                for error in console_errors[:3]:  # Show first 3
                    print(f"      • {error}")
            else:
                print("   ✅ No console errors detected")
            
            print("\n🏆 GUI TEST SUMMARY:")
            
            # Overall assessment
            issues = 0
            if not main_container:
                issues += 1
            if not inputs:
                issues += 1
            if not buttons:
                issues += 1
            if load_time > 5:
                issues += 1
            if console_errors:
                issues += 1
            
            if issues == 0:
                print("   🎉 EXCELLENT - GUI is beautiful and fully functional!")
            elif issues <= 2:
                print("   ✅ GOOD - GUI is functional with minor areas for improvement")
            else:
                print("   ⚠️ NEEDS WORK - GUI has several issues that should be addressed")
            
            print(f"\n📊 Issues found: {issues}/5")
            print(f"📸 Screenshots saved: gui_test_initial.png, gui_test_final.png")
            
            # Keep browser open for manual inspection
            print("\n👀 Browser will stay open for 30 seconds for manual inspection...")
            await page.wait_for_timeout(30000)
            
            await browser.close()
            
            return {
                'title': title,
                'elements_found': {
                    'inputs': len(inputs) if inputs else 0,
                    'buttons': len(buttons) if buttons else 0,
                    'headings': len(headings) if headings else 0
                },
                'load_time': load_time,
                'console_errors': len(console_errors),
                'issues': issues,
                'overall_rating': 'excellent' if issues == 0 else 'good' if issues <= 2 else 'needs_work'
            }
            
        except Exception as e:
            print(f"❌ Error during GUI testing: {str(e)}")
            try:
                await browser.close()
            except:
                pass
            return None

if __name__ == "__main__":
    print("🎨 ReadySearch GUI Beauty & Functionality Test")
    print("🎯 This will test the GUI appearance and basic functionality")
    print("")
    
    result = asyncio.run(test_gui_beauty_and_functionality())
    
    if result:
        print(f"\n✅ Test completed successfully!")
        print(f"📊 Overall rating: {result['overall_rating'].upper()}")
    else:
        print("\n❌ Test failed or could not complete")