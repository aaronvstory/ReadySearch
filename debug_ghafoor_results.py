#!/usr/bin/env python3
"""Debug script to examine why Ghafoor Nadery shows only 2 results instead of 600+."""

import asyncio
import time
import requests
import json
from playwright.async_api import async_playwright

async def debug_ghafoor_results():
    """Debug the Ghafoor Nadery result extraction issue."""
    print("🔍 Debugging Ghafoor Nadery Result Extraction")
    print("=" * 60)
    
    # Start browser manually to inspect the page
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible browser for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to ReadySearch
            print("📄 Navigating to ReadySearch...")
            await page.goto("https://readysearch.com.au/personsearch.aspx", wait_until="domcontentloaded")
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Search for Ghafoor Nadery
            print("🔍 Searching for 'Ghafoor Nadery'...")
            
            # Find and fill search input - try multiple selectors
            search_input = None
            search_selectors = [
                'input[name="name"]',
                'input[placeholder*="name"]',
                'input[type="text"]',
                '#name',
                '.search-input'
            ]
            
            for selector in search_selectors:
                try:
                    search_input = await page.wait_for_selector(selector, timeout=2000)
                    print(f"✅ Found search input: {selector}")
                    break
                except:
                    continue
            
            if not search_input:
                print("❌ Could not find search input")
                # Save page for analysis
                html_content = await page.content()
                with open("readysearch_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("💾 Saved page content to readysearch_page.html")
                return
            
            await search_input.fill("Ghafoor Nadery")
            
            # Submit search - try multiple selectors
            search_button = None
            button_selectors = [
                '.sch_but',
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Search")'
            ]
            
            for selector in button_selectors:
                try:
                    search_button = await page.wait_for_selector(selector, timeout=2000)
                    print(f"✅ Found search button: {selector}")
                    break
                except:
                    continue
            
            if search_button:
                await search_button.click()
            else:
                print("⚠️ No search button found, trying Enter key")
                await page.keyboard.press('Enter')
            
            # Wait for results
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await asyncio.sleep(3)
            
            # Check page content
            print("📊 Analyzing page content...")
            
            # Get page text to see what's displayed
            page_text = await page.inner_text('body')
            
            # Look for result indicators
            if "Tick ALL records" in page_text:
                print("✅ Found results page")
                
                # Count visible results
                tables = await page.locator('table').count()
                print(f"📊 Found {tables} tables on page")
                
                # Look for result text patterns
                if "624 results" in page_text:
                    print("✅ Page shows 624 results in text")
                elif "results found" in page_text:
                    print("✅ Page shows results found")
                else:
                    print("❌ No result count found in page text")
                
                # Extract all table rows
                total_rows = 0
                for i in range(tables):
                    table = page.locator('table').nth(i)
                    rows = await table.locator('tr').count()
                    table_text = await table.inner_text()
                    print(f"   Table {i+1}: {rows} rows, {len(table_text)} characters")
                    total_rows += rows
                    
                    # Show first few rows of content
                    if i == 0 and rows > 0:
                        print(f"   First table content preview:")
                        first_rows = min(5, rows)
                        for r in range(first_rows):
                            row_text = await table.locator('tr').nth(r).inner_text()
                            print(f"     Row {r}: {row_text[:100]}...")
                
                print(f"📊 Total table rows found: {total_rows}")
                
                # Look for pagination or "show more" elements
                pagination_selectors = [
                    'a[href*="page"]',
                    'button[onclick*="page"]',
                    'input[name*="page"]',
                    '.pagination',
                    '.pager'
                ]
                
                for selector in pagination_selectors:
                    elements = await page.locator(selector).count()
                    if elements > 0:
                        print(f"📄 Found {elements} pagination elements: {selector}")
                
                # Save page content for analysis
                html_content = await page.content()
                with open("ghafoor_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("💾 Saved page content to ghafoor_debug.html")
                
                # Take screenshot
                await page.screenshot(path="ghafoor_debug.png")
                print("📸 Saved screenshot to ghafoor_debug.png")
                
            else:
                print("❌ No results found on page")
                print("Page text preview:")
                print(page_text[:500])
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_ghafoor_results())