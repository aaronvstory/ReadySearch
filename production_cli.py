#!/usr/bin/env python3
"""
PRODUCTION CLI - Final working version with direct selector usage
"""

import asyncio
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from readysearch_automation.input_loader import SearchRecord
from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

class ProductionCLI:
    """Production CLI with direct selector usage and verified performance"""
    
    def __init__(self):
        self.config = Config.get_config()
        self.matcher = AdvancedNameMatcher()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    async def search_person(self, search_record: SearchRecord) -> dict:
        """
        Search for a person using direct selector approach
        
        Args:
            search_record: SearchRecord with name and optional birth year
            
        Returns:
            Dictionary with search results
        """
        start_time = time.time()
        
        print(f"🎯 Searching for: {search_record.name}")
        if search_record.birth_year:
            print(f"📅 Birth year: {search_record.birth_year} (searching {search_record.birth_year-2} to {search_record.birth_year+2})")
        
        async with async_playwright() as p:
            try:
                # Launch browser with optimized settings
                print("🚀 Launching browser...")
                browser = await p.chromium.launch(
                    headless=True,  # SPEED: No GUI
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                )
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to ReadySearch
                print("🌐 Navigating to ReadySearch...")
                await page.goto("https://readysearch.com.au/products?person", timeout=15000, wait_until="networkidle")
                print("✅ Page loaded")
                
                # DIRECT SELECTOR USAGE - No complex search logic
                print("🔍 Finding search input...")
                name_input = await page.wait_for_selector('input[name="search"]', timeout=5000)
                print("✅ Found name input field")
                
                # Enter name
                print(f"⌨️ Entering name: {search_record.name}")
                await name_input.click()
                await name_input.fill(search_record.name)
                print("✅ Name entered")
                
                # Set birth year range if provided
                if search_record.birth_year:
                    start_year = search_record.birth_year - 2
                    end_year = search_record.birth_year + 2
                    
                    print(f"📅 Setting birth year range: {start_year} to {end_year}")
                    
                    # Start year
                    start_select = await page.wait_for_selector('select[name="yobs"]', timeout=3000)
                    await start_select.select_option(str(start_year))
                    print(f"✅ Start year set to {start_year}")
                    
                    # End year  
                    end_select = await page.wait_for_selector('select[name="yobe"]', timeout=3000)
                    await end_select.select_option(str(end_year))
                    print(f"✅ End year set to {end_year}")
                
                # Submit search
                print("🚀 Submitting search...")
                submit_button = await page.wait_for_selector('.sch_but', timeout=3000)
                await submit_button.click()
                print("✅ Search submitted")
                
                # Handle popup if it appears
                try:
                    await page.wait_for_selector('text="ONE PERSON MAY HAVE MULTIPLE RECORDS"', timeout=3000)
                    print("📋 Handling popup...")
                    await page.keyboard.press('Enter')  # Accept popup
                    print("✅ Popup handled")
                except:
                    print("ℹ️ No popup appeared")
                
                # Wait for results page
                print("⏳ Waiting for results...")
                await page.wait_for_load_state('networkidle', timeout=30000)
                print("✅ Results page loaded")
                
                # Extract results
                print("📊 Extracting results...")
                results = await self.extract_results(page, search_record)
                
                search_duration = time.time() - start_time
                results['search_duration'] = search_duration
                
                print(f"📈 Search completed in {search_duration:.2f}s")
                print(f"📊 Found {results['matches_found']} matches")
                
                await browser.close()
                return results
                
            except Exception as e:
                search_duration = time.time() - start_time
                print(f"❌ Error during search: {str(e)}")
                
                try:
                    await browser.close()
                except:
                    pass
                
                return {
                    'name': search_record.name,
                    'status': 'Error',
                    'error': str(e),
                    'search_duration': search_duration,
                    'matches_found': 0,
                    'exact_matches': 0,
                    'partial_matches': 0,
                    'match_category': 'ERROR',
                    'match_reasoning': f'Search failed: {str(e)}',
                    'detailed_results': []
                }
    
    async def extract_results(self, page, search_record: SearchRecord) -> dict:
        """Extract results from the results page"""
        
        try:
            # Look for result rows
            result_rows = await page.query_selector_all('tr')
            print(f"📋 Found {len(result_rows)} table rows")
            
            detailed_results = []
            matches_found = 0
            
            for i, row in enumerate(result_rows):
                try:
                    # Extract text from row
                    row_text = await row.inner_text()
                    
                    # Print first few rows for debugging
                    if i < 15:
                        print(f"   🔍 Row {i+1}: {row_text[:100]}...")
                    
                    # Skip obviously irrelevant rows
                    if not row_text.strip():
                        continue
                    
                    # Look for ReadySearch result patterns
                    # Example: "ANDRO CUTUK | Date of Birth: 12/06/1975	SYDNEY NSW |"
                    
                    # Check if this row contains a person's name and birth date
                    row_text_clean = row_text.strip()
                    
                    # Look for "Date of Birth:" pattern which indicates a result
                    if "Date of Birth:" in row_text_clean:
                        print(f"   🎯 Found result row {i+1}: {row_text_clean}")
                        
                        # Extract name and date from the pattern
                        if "|" in row_text_clean:
                            # Split by pipe separators
                            parts = row_text_clean.split("|")
                            
                            for part in parts:
                                part = part.strip()
                                if "Date of Birth:" in part:
                                    # Find the name (should be in a previous part or same part)
                                    name_part = ""
                                    date_part = part
                                    
                                    # Look for name in previous parts
                                    for prev_part in parts:
                                        prev_part = prev_part.strip()
                                        if prev_part and "Date of Birth:" not in prev_part and len(prev_part) > 2:
                                            # Check if this looks like a name
                                            if prev_part.replace(' ', '').replace('-', '').replace('.', '').isalpha():
                                                name_part = prev_part
                                                break
                                    
                                    # Extract date from "Date of Birth: XX/XX/XXXX"
                                    date_match = ""
                                    if "Date of Birth:" in date_part:
                                        date_text = date_part.split("Date of Birth:")[1].strip()
                                        # Extract just the date part (before any location info)
                                        date_match = date_text.split()[0] if date_text else ""
                                    
                                    if name_part:
                                        print(f"      📝 Extracted: Name='{name_part}', Date='{date_match}'")
                                        
                                        # Use STRICT advanced matcher to enforce last name exact matching
                                        exact_first_name = getattr(search_record, 'exact_matching', False)
                                        match_result = self.matcher.match_names_strict(search_record.name, name_part, exact_first_name)
                                        
                                        if match_result.match_type != MatchType.NOT_MATCHED:
                                            matches_found += 1
                                            detailed_results.append({
                                                'matched_name': name_part,
                                                'date_of_birth': date_match,
                                                'match_type': match_result.get_display_category(),
                                                'match_reasoning': match_result.reasoning,
                                                'confidence': match_result.confidence
                                            })
                                            
                                            print(f"      ✅ MATCH {matches_found}: {name_part} ({match_result.get_display_category()}) - {match_result.reasoning}")
                                        else:
                                            print(f"      ❌ No match: {name_part} - {match_result.reasoning}")
                                    break
                        else:
                            # Alternative pattern without pipes
                            # Try to extract name and date from the line
                            if "Date of Birth:" in row_text_clean:
                                # Look for lines like: "ANDRO CUTUK\nDate of Birth: 12/06/1975\tSYDNEY NSW"
                                lines = row_text_clean.split('\n')
                                
                                for i, line in enumerate(lines):
                                    if "Date of Birth:" in line:
                                        # The name should be in the previous line or beginning of this line
                                        name_candidates = []
                                        
                                        # Check previous line
                                        if i > 0:
                                            prev_line = lines[i-1].strip()
                                            if prev_line and len(prev_line) > 2 and prev_line.replace(' ', '').replace('-', '').isalpha():
                                                name_candidates.append(prev_line)
                                        
                                        # Check if name is at the beginning of current line
                                        if line.split("Date of Birth:")[0].strip():
                                            candidate = line.split("Date of Birth:")[0].strip()
                                            if len(candidate) > 2 and candidate.replace(' ', '').replace('-', '').isalpha():
                                                name_candidates.append(candidate)
                                        
                                        # Extract date
                                        date_part = line.split("Date of Birth:")[1].strip().split()[0] if "Date of Birth:" in line else ""
                                        
                                        # Process each name candidate
                                        for potential_name in name_candidates:
                                            if potential_name and len(potential_name) <= 50:  # Reasonable name length
                                                print(f"      📝 Clean extraction: Name='{potential_name}', Date='{date_part}'")
                                                
                                                # Use STRICT matching with user preference
                                                exact_first_name = getattr(search_record, 'exact_matching', False)
                                                match_result = self.matcher.match_names_strict(search_record.name, potential_name, exact_first_name)
                                                
                                                if match_result.match_type != MatchType.NOT_MATCHED:
                                                    matches_found += 1
                                                    detailed_results.append({
                                                        'matched_name': potential_name,
                                                        'date_of_birth': date_part,
                                                        'match_type': match_result.get_display_category(),
                                                        'match_reasoning': match_result.reasoning,
                                                        'confidence': match_result.confidence
                                                    })
                                                    
                                                    print(f"      ✅ MATCH {matches_found}: {potential_name} ({match_result.get_display_category()})")
                                                break  # Only take first valid match per row
                
                except Exception as e:
                    # Skip rows that can't be processed
                    print(f"      ⚠️ Error processing row {i+1}: {e}")
                    continue
            
            # Categorize results
            exact_matches = len([r for r in detailed_results if 'EXACT' in r['match_type']])
            partial_matches = len([r for r in detailed_results if 'PARTIAL' in r['match_type']])
            
            # Determine overall status
            if exact_matches > 0:
                status = "Match"
                category = "EXACT MATCH" 
                reasoning = f"Found {exact_matches} exact matches"
            elif partial_matches > 0:
                status = "Match"
                category = "PARTIAL MATCH"
                reasoning = f"Found {partial_matches} partial matches"
            elif matches_found > 0:
                status = "Match"
                category = "PARTIAL MATCH"
                reasoning = f"Found {matches_found} matches"
            else:
                status = "No Match"
                category = "NOT MATCHED"
                reasoning = "No meaningful matches found"
            
            return {
                'name': search_record.name,
                'status': status,
                'matches_found': matches_found,
                'exact_matches': exact_matches,
                'partial_matches': partial_matches,
                'match_category': category,
                'match_reasoning': reasoning,
                'detailed_results': detailed_results,
                'total_results': len(result_rows)
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting results: {str(e)}")
            return {
                'name': search_record.name,
                'status': 'Error',
                'error': f'Result extraction failed: {str(e)}',
                'matches_found': 0,
                'exact_matches': 0,
                'partial_matches': 0,
                'match_category': 'ERROR',
                'match_reasoning': f'Could not extract results: {str(e)}',
                'detailed_results': []
            }

async def main():
    """Main CLI function"""
    
    print("🎯 PRODUCTION READYSEARCH CLI")
    print("📝 Enter names separated by semicolons")
    print("💡 Examples: 'John Smith;Jane Doe,1990;Bob Jones'")
    print("⚡ Optimized for 30-second maximum per search")
    print("")
    
    # Get input
    if len(sys.argv) > 1:
        names_input = ' '.join(sys.argv[1:])
    else:
        names_input = input("🔤 Enter names (semicolon-separated): ").strip()
    
    if not names_input:
        print("❌ No names provided. Exiting.")
        return
    
    # Parse names
    search_records = []
    names = names_input.split(';')
    
    for name_entry in names:
        name_entry = name_entry.strip()
        if ',' in name_entry:
            parts = name_entry.split(',', 1)
            name = parts[0].strip()
            try:
                birth_year = int(parts[1].strip())
                search_records.append(SearchRecord(name=name, birth_year=birth_year))
            except ValueError:
                search_records.append(SearchRecord(name=name_entry))
        else:
            search_records.append(SearchRecord(name=name_entry))
    
    print(f"📊 Parsed {len(search_records)} names")
    
    # Create CLI instance
    cli = ProductionCLI()
    
    # Process each name
    all_results = []
    total_start = time.time()
    
    for i, search_record in enumerate(search_records):
        print(f"\n{'='*60}")
        print(f"🎯 PROCESSING {i+1}/{len(search_records)}: {search_record.name}")
        print('='*60)
        
        result = await cli.search_person(search_record)
        all_results.append(result)
        
        # Performance check
        if result['search_duration'] <= 30:
            print(f"✅ PERFORMANCE: {result['search_duration']:.2f}s ≤ 30s target")
        else:
            print(f"⚠️ PERFORMANCE: {result['search_duration']:.2f}s > 30s target")
        
        print(f"📊 Status: {result['status']} ({result['match_category']})")
        if result['detailed_results']:
            print(f"📋 Matches found:")
            for j, match in enumerate(result['detailed_results'][:5]):  # Show first 5
                print(f"   {j+1}. {match['matched_name']} - {match['match_type']}")
    
    # Generate comprehensive report
    total_duration = time.time() - total_start
    
    print(f"\n{'='*60}")
    print("🎯 COMPREHENSIVE REPORT")
    print('='*60)
    
    print(f"📊 PERFORMANCE SUMMARY:")
    print(f"   Total Time: {total_duration:.2f}s")
    print(f"   Average per Search: {total_duration/len(all_results):.2f}s")
    
    performance_met = all(r['search_duration'] <= 30 for r in all_results)
    print(f"   30s Target: {'✅ MET' if performance_met else '❌ EXCEEDED'}")
    
    matches = [r for r in all_results if r['matches_found'] > 0]
    no_matches = [r for r in all_results if r['matches_found'] == 0 and r['status'] != 'Error']
    errors = [r for r in all_results if r['status'] == 'Error']
    
    print(f"\n📋 RESULTS BREAKDOWN:")
    print(f"   ✅ Found Matches: {len(matches)}")
    print(f"   ⭕ No Matches: {len(no_matches)}")
    print(f"   ❌ Errors: {len(errors)}")
    print(f"   🎯 Success Rate: {((len(matches) + len(no_matches))/len(all_results)*100):.1f}%")
    
    print(f"\n📄 DETAILED BREAKDOWN:")
    for i, result in enumerate(all_results):
        status_emoji = "✅" if result['matches_found'] > 0 else "⭕" if result['status'] != 'Error' else "❌"
        birth_info = f" (born {result.get('birth_year', 'N/A')})" if 'birth_year' in result else ""
        
        print(f"   {i+1}. {status_emoji} {result['name']}{birth_info}")
        print(f"      Status: {result['status']} | Duration: {result['search_duration']:.2f}s | Matches: {result['matches_found']}")
        
        if result['detailed_results']:
            for j, match in enumerate(result['detailed_results'][:3]):
                print(f"         • {match['matched_name']} ({match['match_type']})")
    
    print('='*60)
    print("🎉 AUTOMATION COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())