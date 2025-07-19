#!/usr/bin/env python3
"""
Simple GUI Visual Assessment Test
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_gui_assessment():
    """Simple visual assessment of the GUI"""
    
    print("🎨 SIMPLE GUI VISUAL ASSESSMENT")
    print("=" * 40)
    
    async with async_playwright() as p:
        try:
            # Launch browser
            print("🚀 Opening GUI in browser...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={'width': 1400, 'height': 900})
            page = await context.new_page()
            
            # Navigate to GUI
            print("🌐 Loading ReadySearch GUI...")
            await page.goto("http://localhost:5173", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(5000)  # Wait for React to fully load
            
            # Get basic info
            title = await page.title()
            url = page.url
            
            print(f"📄 Title: {title}")
            print(f"🌐 URL: {url}")
            
            # Take a full-page screenshot
            print("📸 Taking screenshot...")
            await page.screenshot(path="gui_final_assessment.png", full_page=True)
            
            # Check page content
            body_text = await page.inner_text("body")
            
            print(f"\n📊 CONTENT ANALYSIS:")
            print(f"   Total page text length: {len(body_text)} characters")
            
            # Check for key ReadySearch elements
            readysearch_mentions = body_text.lower().count("readysearch")
            automation_mentions = body_text.lower().count("automation")
            
            print(f"   'ReadySearch' mentions: {readysearch_mentions}")
            print(f"   'Automation' mentions: {automation_mentions}")
            
            # Look for form elements
            print(f"\n🔍 UI ELEMENT COUNT:")
            inputs = await page.query_selector_all("input")
            buttons = await page.query_selector_all("button")
            selects = await page.query_selector_all("select")
            textareas = await page.query_selector_all("textarea")
            
            print(f"   Input fields: {len(inputs)}")
            print(f"   Buttons: {len(buttons)}")
            print(f"   Select dropdowns: {len(selects)}")
            print(f"   Text areas: {len(textareas)}")
            
            # Check if it looks like a working React app
            has_react_root = await page.query_selector("div#root")
            
            print(f"\n✅ FUNCTIONALITY INDICATORS:")
            print(f"   React root element: {'Yes' if has_react_root else 'No'}")
            print(f"   Interactive elements: {len(inputs) + len(buttons) + len(selects)}")
            print(f"   Content loaded: {'Yes' if len(body_text) > 100 else 'No'}")
            
            # Check for modern UI frameworks
            print(f"\n🎨 DESIGN FRAMEWORK DETECTION:")
            
            # Look for Tailwind classes in the DOM
            page_html = await page.content()
            has_tailwind = any(cls in page_html for cls in ['bg-', 'text-', 'p-', 'm-', 'flex', 'grid'])
            has_shadcn = 'shadcn' in page_html.lower() or 'cn(' in page_html
            
            print(f"   Tailwind CSS: {'Detected' if has_tailwind else 'Not detected'}")
            print(f"   Shadcn/UI: {'Detected' if has_shadcn else 'Not detected'}")
            
            # Overall assessment
            score = 0
            if has_react_root:
                score += 2
            if len(inputs) > 0:
                score += 2
            if len(buttons) > 0:
                score += 2
            if len(body_text) > 500:
                score += 2
            if has_tailwind:
                score += 1
            if readysearch_mentions > 0:
                score += 1
            
            print(f"\n🏆 OVERALL ASSESSMENT:")
            print(f"   Score: {score}/10")
            
            if score >= 8:
                rating = "EXCELLENT"
                emoji = "🎉"
            elif score >= 6:
                rating = "GOOD"
                emoji = "✅"
            elif score >= 4:
                rating = "ACCEPTABLE"
                emoji = "⚠️"
            else:
                rating = "NEEDS WORK"
                emoji = "❌"
            
            print(f"   Rating: {emoji} {rating}")
            
            # Manual inspection time
            print(f"\n👀 Browser will stay open for 20 seconds for visual inspection...")
            print(f"📸 Screenshot saved as: gui_final_assessment.png")
            
            await page.wait_for_timeout(20000)
            
            await browser.close()
            
            return {
                'title': title,
                'score': score,
                'rating': rating,
                'elements': {
                    'inputs': len(inputs),
                    'buttons': len(buttons),
                    'selects': len(selects)
                },
                'frameworks': {
                    'tailwind': has_tailwind,
                    'shadcn': has_shadcn
                }
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            try:
                await browser.close()
            except:
                pass
            return None

if __name__ == "__main__":
    print("🎨 ReadySearch GUI Simple Assessment")
    print("🎯 Quick visual check of GUI beauty and functionality")
    print("")
    
    result = asyncio.run(simple_gui_assessment())
    
    if result:
        print(f"\n✅ Assessment completed!")
        print(f"🏆 Final rating: {result['rating']}")
    else:
        print("\n❌ Assessment failed")