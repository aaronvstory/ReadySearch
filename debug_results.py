#!/usr/bin/env python3
"""
DEBUG RESULTS - Inspect actual results page content
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from readysearch_automation.input_loader import SearchRecord

async def debug_results_extraction(name="Andro Cutuk", birth_year=1975):
    """Debug what's actually on the results page"""
    
    print(f"🔍 DEBUGGING RESULTS FOR: {name} (born {birth_year})")
    print("🎯 Running with VISIBLE browser to see actual content")
    print("")
    
    async with async_playwright() as p:
        try:
            # Launch VISIBLE browser for debugging
            print("🚀 Launching VISIBLE browser...")
            browser = await p.chromium.launch(
                headless=False,  # VISIBLE for debugging
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to ReadySearch
            print("🌐 Navigating to ReadySearch...")
            await page.goto("https://readysearch.com.au/products?person", timeout=15000, wait_until="networkidle")
            print("✅ Page loaded")
            
            # Enter search details
            print(f"⌨️ Entering search: {name}")
            name_input = await page.wait_for_selector('input[name="search"]', timeout=5000)
            await name_input.click()
            await name_input.fill(name)
            
            # Set birth year range
            start_year = birth_year - 2
            end_year = birth_year + 2
            print(f"📅 Setting birth year range: {start_year} to {end_year}")
            
            start_select = await page.wait_for_selector('select[name="yobs"]', timeout=3000)
            await start_select.select_option(str(start_year))
            
            end_select = await page.wait_for_selector('select[name="yobe"]', timeout=3000)
            await end_select.select_option(str(end_year))
            
            # Submit search
            print("🚀 Submitting search...")
            submit_button = await page.wait_for_selector('.sch_but', timeout=3000)
            await submit_button.click()
            
            # Handle popup if it appears
            try:
                await page.wait_for_selector('text="ONE PERSON MAY HAVE MULTIPLE RECORDS"', timeout=3000)
                print("📋 Handling popup...")
                await page.keyboard.press('Enter')
            except:
                print("ℹ️ No popup appeared")
            
            # Wait for results
            print("⏳ Waiting for results...")
            await page.wait_for_load_state('networkidle', timeout=30000)
            print("✅ Results page loaded")
            
            print("\n" + "="*60)
            print("🔍 DEBUGGING RESULTS PAGE CONTENT")
            print("="*60)
            
            # Get page title and URL
            title = await page.title()
            url = page.url
            print(f"📄 Page Title: {title}")
            print(f"🌐 Current URL: {url}")
            
            # Look for different result containers
            print("\n🔍 SEARCHING FOR RESULT CONTAINERS:")
            
            containers_to_check = [
                'table',
                '.results-table', 
                '#results',
                '.result-container',
                '.search-results',
                'tbody',
                '.content'
            ]
            
            for container in containers_to_check:
                try:
                    elements = await page.query_selector_all(container)
                    if elements:
                        print(f"   ✅ Found {len(elements)} elements with selector: {container}")
                        # Get content from first element
                        if elements:
                            content = await elements[0].inner_text()
                            print(f"      Preview: {content[:100]}...")
                    else:
                        print(f"   ❌ No elements found for: {container}")
                except Exception as e:
                    print(f"   ⚠️ Error checking {container}: {e}")
            
            # Get ALL table rows
            print("\n📋 ANALYZING TABLE ROWS:")
            try:
                all_rows = await page.query_selector_all('tr')
                print(f"   Found {len(all_rows)} total table rows")
                
                for i, row in enumerate(all_rows[:10]):  # Show first 10 rows
                    try:
                        row_text = await row.inner_text()
                        row_text = row_text.replace('\n', ' | ').strip()
                        if row_text:
                            print(f"   Row {i+1}: {row_text}")
                    except:
                        print(f"   Row {i+1}: [Could not extract text]")
                        
                if len(all_rows) > 10:
                    print(f"   ... and {len(all_rows) - 10} more rows")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing rows: {e}")
            
            # Check for "no results" messages
            print("\n🚫 CHECKING FOR 'NO RESULTS' MESSAGES:")
            no_results_patterns = [
                'No results',
                'No matches', 
                'No records found',
                'Sorry, no results',
                'No data found',
                'Nothing found'
            ]
            
            page_content = await page.content()
            page_text = await page.inner_text('body')
            
            for pattern in no_results_patterns:
                if pattern.lower() in page_text.lower():
                    print(f"   ⚠️ Found message: '{pattern}' in page content")
                    break
            else:
                print("   ✅ No 'no results' messages found")
            
            # Save page content for detailed analysis
            print("\n💾 SAVING PAGE CONTENT FOR ANALYSIS:")
            
            # Save HTML
            html_content = await page.content()
            with open('debug_results.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("   ✅ Saved debug_results.html")
            
            # Save text content
            with open('debug_results.txt', 'w', encoding='utf-8') as f:
                f.write(page_text)
            print("   ✅ Saved debug_results.txt")
            
            print(f"\n📊 SUMMARY:")
            print(f"   Page Title: {title}")
            print(f"   Total Content Length: {len(page_text)} characters")
            print(f"   Total Table Rows: {len(all_rows) if 'all_rows' in locals() else 'Unknown'}")
            
            # Keep browser open for manual inspection
            print("\n⏸️ Browser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ Error during debugging: {str(e)}")
            try:
                await browser.close()
            except:
                pass

if __name__ == "__main__":
    print("🔍 RESULTS DEBUGGING TOOL")
    print("🎯 This will show exactly what's on the results page")
    print("")
    
    # Test with Andro Cutuk first
    asyncio.run(debug_results_extraction("Andro Cutuk", 1975))