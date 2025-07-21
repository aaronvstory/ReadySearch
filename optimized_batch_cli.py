#!/usr/bin/env python3
"""
Optimized ReadySearch CLI - High-performance batch processing with browser pooling
Designed to handle 1-100+ searches efficiently with concurrent processing
"""

import asyncio
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json
import csv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from readysearch_automation.input_loader import SearchRecord
from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

@dataclass
class OptimizedSearchResult:
    """Enhanced search result for batch processing"""
    name: str
    status: str
    search_duration: float
    matches_found: int
    exact_matches: int
    partial_matches: int
    match_category: str
    match_reasoning: str
    detailed_results: List[Dict[str, Any]]
    timestamp: str
    birth_year: Optional[int] = None
    error: Optional[str] = None
    browser_id: Optional[str] = None  # For debugging/tracking

class BrowserPool:
    """Manages a pool of browser instances for efficient batch processing"""
    
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self.browsers: List[Browser] = []
        self.available_contexts: List[BrowserContext] = []
        self.busy_contexts: set = set()
        self.playwright_instance = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the browser pool"""
        if self.initialized:
            return
            
        print(f"🚀 Initializing browser pool with {self.pool_size} instances...")
        self.playwright_instance = await async_playwright().start()
        
        for i in range(self.pool_size):
            browser = await self.playwright_instance.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            self.browsers.append(browser)
            
            # Create initial context for each browser
            context = await browser.new_context()
            self.available_contexts.append(context)
            print(f"   ✅ Browser {i+1} initialized")
        
        self.initialized = True
        print(f"🎯 Browser pool ready with {len(self.available_contexts)} contexts")
    
    async def get_context(self) -> tuple[BrowserContext, str]:
        """Get an available browser context"""
        if not self.available_contexts:
            # If no contexts available, wait a bit and try again
            await asyncio.sleep(0.1)
            if not self.available_contexts:
                raise Exception("No browser contexts available")
        
        context = self.available_contexts.pop(0)
        browser_id = f"browser_{len(self.busy_contexts) % self.pool_size}"
        self.busy_contexts.add(context)
        return context, browser_id
    
    async def return_context(self, context: BrowserContext):
        """Return a browser context to the pool"""
        if context in self.busy_contexts:
            self.busy_contexts.remove(context)
            
            # Close all pages in the context to free memory
            for page in context.pages:
                await page.close()
            
            # Create a new page for the next use
            await context.new_page()
            self.available_contexts.append(context)
    
    async def cleanup(self):
        """Clean up all browser instances"""
        print("🧹 Cleaning up browser pool...")
        
        # Close all contexts
        all_contexts = self.available_contexts + list(self.busy_contexts)
        for context in all_contexts:
            try:
                await context.close()
            except:
                pass
        
        # Close all browsers
        for browser in self.browsers:
            try:
                await browser.close()
            except:
                pass
        
        # Stop playwright
        if self.playwright_instance:
            try:
                await self.playwright_instance.stop()
            except:
                pass
        
        print("✅ Browser pool cleanup completed")

class OptimizedBatchSearcher:
    """High-performance batch searcher with browser pooling and concurrency"""
    
    def __init__(self, pool_size: int = 3, max_concurrent: int = 3):
        self.pool_size = pool_size
        self.max_concurrent = max_concurrent
        self.browser_pool = BrowserPool(pool_size)
        self.matcher = AdvancedNameMatcher()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the batch searcher"""
        await self.browser_pool.initialize()
    
    async def search_single_optimized(self, search_record: SearchRecord) -> OptimizedSearchResult:
        """
        Perform optimized single search using browser pool
        """
        async with self.semaphore:  # Limit concurrent searches
            start_time = time.time()
            context = None
            browser_id = None
            
            try:
                # Get browser context from pool
                context, browser_id = await self.browser_pool.get_context()
                page = context.pages[0] if context.pages else await context.new_page()
                
                # Navigate to ReadySearch
                await page.goto("https://readysearch.com.au/products?person", timeout=15000, wait_until="networkidle")
                
                # Perform search
                name_input = await page.wait_for_selector('input[name="search"]', timeout=5000)
                await name_input.click()
                await name_input.fill(search_record.name)
                
                # Set birth year range if provided
                if search_record.birth_year:
                    start_year = search_record.birth_year - 2
                    end_year = search_record.birth_year + 2
                    
                    start_select = await page.wait_for_selector('select[name="yobs"]', timeout=3000)
                    await start_select.select_option(str(start_year))
                    
                    end_select = await page.wait_for_selector('select[name="yobe"]', timeout=3000)
                    await end_select.select_option(str(end_year))
                
                # Submit search
                submit_button = await page.wait_for_selector('.sch_but', timeout=3000)
                await submit_button.click()
                
                # Handle popup if it appears
                try:
                    await page.wait_for_selector('text="ONE PERSON MAY HAVE MULTIPLE RECORDS"', timeout=3000)
                    await page.keyboard.press('Enter')
                except:
                    pass
                
                # Wait for results
                await page.wait_for_load_state('networkidle', timeout=30000)
                
                # Extract results (reusing existing extraction logic)
                results = await self.extract_results_optimized(page, search_record)
                
                search_duration = time.time() - start_time
                
                return OptimizedSearchResult(
                    name=search_record.name,
                    status=results['status'],
                    search_duration=search_duration,
                    matches_found=results['matches_found'],
                    exact_matches=results['exact_matches'],
                    partial_matches=results['partial_matches'],
                    match_category=results['match_category'],
                    match_reasoning=results['match_reasoning'],
                    detailed_results=results['detailed_results'],
                    timestamp=datetime.now().isoformat(),
                    birth_year=search_record.birth_year,
                    browser_id=browser_id
                )
                
            except Exception as e:
                search_duration = time.time() - start_time
                return OptimizedSearchResult(
                    name=search_record.name,
                    status='Error',
                    search_duration=search_duration,
                    matches_found=0,
                    exact_matches=0,
                    partial_matches=0,
                    match_category='ERROR',
                    match_reasoning=f'Search failed: {str(e)}',
                    detailed_results=[],
                    timestamp=datetime.now().isoformat(),
                    birth_year=search_record.birth_year,
                    error=str(e),
                    browser_id=browser_id
                )
            finally:
                # Return context to pool
                if context:
                    await self.browser_pool.return_context(context)
    
    async def extract_results_optimized(self, page: Page, search_record: SearchRecord) -> Dict[str, Any]:
        """Optimized result extraction (reusing existing logic)"""
        try:
            result_rows = await page.query_selector_all('tr')
            detailed_results = []
            matches_found = 0
            
            for i, row in enumerate(result_rows):
                try:
                    row_text = await row.inner_text()
                    
                    if not row_text.strip() or "Date of Birth:" not in row_text:
                        continue
                    
                    # Extract name and date patterns (reusing existing logic)
                    row_text_clean = row_text.strip()
                    
                    if "|" in row_text_clean:
                        parts = row_text_clean.split("|")
                        for part in parts:
                            part = part.strip()
                            if "Date of Birth:" in part:
                                name_part = ""
                                date_part = part
                                
                                for prev_part in parts:
                                    prev_part = prev_part.strip()
                                    if prev_part and "Date of Birth:" not in prev_part and len(prev_part) > 2:
                                        if prev_part.replace(' ', '').replace('-', '').replace('.', '').isalpha():
                                            name_part = prev_part
                                            break
                                
                                date_match = ""
                                if "Date of Birth:" in date_part:
                                    date_text = date_part.split("Date of Birth:")[1].strip()
                                    date_match = date_text.split()[0] if date_text else ""
                                
                                if name_part:
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
                                break
                
                except Exception:
                    continue
            
            # Categorize results
            exact_matches = len([r for r in detailed_results if 'EXACT' in r['match_type']])
            partial_matches = len([r for r in detailed_results if 'PARTIAL' in r['match_type']])
            
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
                'status': status,
                'matches_found': matches_found,
                'exact_matches': exact_matches,
                'partial_matches': partial_matches,
                'match_category': category,
                'match_reasoning': reasoning,
                'detailed_results': detailed_results
            }
            
        except Exception as e:
            return {
                'status': 'Error',
                'matches_found': 0,
                'exact_matches': 0,
                'partial_matches': 0,
                'match_category': 'ERROR',
                'match_reasoning': f'Result extraction failed: {str(e)}',
                'detailed_results': []
            }
    
    async def batch_search_concurrent(self, search_records: List[SearchRecord]) -> List[OptimizedSearchResult]:
        """
        Perform concurrent batch search with progress tracking
        """
        print(f"🎯 Starting optimized batch search for {len(search_records)} records")
        print(f"⚡ Concurrent searches: {self.max_concurrent}")
        print(f"🌐 Browser pool size: {self.pool_size}")
        
        # Create tasks for all searches
        tasks = []
        for i, search_record in enumerate(search_records):
            task = asyncio.create_task(
                self.search_single_optimized(search_record),
                name=f"search_{i}_{search_record.name}"
            )
            tasks.append(task)
        
        # Execute with progress tracking
        results = []
        completed = 0
        total = len(tasks)
        
        print(f"\n{'='*60}")
        print("🚀 EXECUTING CONCURRENT SEARCHES")
        print('='*60)
        
        # Process tasks as they complete
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                results.append(result)
                completed += 1
                
                # Progress update
                status_emoji = "✅" if result.matches_found > 0 else "⭕" if result.status != "Error" else "❌"
                print(f"{status_emoji} [{completed:3d}/{total:3d}] {result.name} - {result.status} ({result.search_duration:.2f}s)")
                
            except Exception as e:
                completed += 1
                print(f"❌ [{completed:3d}/{total:3d}] Search task failed: {str(e)}")
        
        # Sort results by original order
        task_names = [task.get_name() for task in tasks]
        result_map = {f"search_{i}_{result.name}": result for i, result in enumerate(results)}
        sorted_results = []
        
        for task_name in task_names:
            if task_name in result_map:
                sorted_results.append(result_map[task_name])
        
        return sorted_results
    
    async def cleanup(self):
        """Clean up resources"""
        await self.browser_pool.cleanup()

def parse_names_input(names_input: str) -> List[SearchRecord]:
    """Parse names input into SearchRecord objects"""
    search_records = []
    names = names_input.split(';')
    
    for name_entry in names:
        name_entry = name_entry.strip()
        if not name_entry:
            continue
            
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
    
    return search_records

def export_results_json(results: List[OptimizedSearchResult], filename: str):
    """Export results as JSON"""
    data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'tool_version': 'Optimized ReadySearch CLI v1.0',
            'optimization_features': [
                'Browser connection pooling',
                'Concurrent processing',
                'Memory optimization',
                'Performance monitoring'
            ]
        },
        'performance_summary': {
            'total_searches': len(results),
            'successful_searches': len([r for r in results if r.status != 'Error']),
            'total_duration': sum(r.search_duration for r in results),
            'average_duration': sum(r.search_duration for r in results) / len(results),
            'matches_found': sum(r.matches_found for r in results),
            'exact_matches': sum(r.exact_matches for r in results)
        },
        'results': [
            {
                'name': r.name,
                'status': r.status,
                'search_duration': r.search_duration,
                'matches_found': r.matches_found,
                'exact_matches': r.exact_matches,
                'partial_matches': r.partial_matches,
                'match_category': r.match_category,
                'match_reasoning': r.match_reasoning,
                'detailed_results': r.detailed_results,
                'timestamp': r.timestamp,
                'birth_year': r.birth_year,
                'error': r.error,
                'browser_id': r.browser_id
            } for r in results
        ]
    }
    
    with open(f"{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def main():
    """Main optimized CLI function"""
    print("🚀 OPTIMIZED READYSEARCH CLI - HIGH PERFORMANCE BATCH PROCESSING")
    print("⚡ Features: Browser pooling, concurrent processing, memory optimization")
    print("📊 Supports: 1-100+ searches with intelligent resource management")
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
    search_records = parse_names_input(names_input)
    print(f"📊 Parsed {len(search_records)} search records")
    
    # Optimize pool and concurrency based on batch size
    batch_size = len(search_records)
    if batch_size <= 5:
        pool_size, max_concurrent = 2, 2
    elif batch_size <= 20:
        pool_size, max_concurrent = 3, 3
    elif batch_size <= 50:
        pool_size, max_concurrent = 4, 4
    else:  # 50+
        pool_size, max_concurrent = 5, 5
    
    print(f"🎯 Optimization settings: {pool_size} browsers, {max_concurrent} concurrent searches")
    
    # Initialize optimized searcher
    searcher = OptimizedBatchSearcher(pool_size=pool_size, max_concurrent=max_concurrent)
    
    try:
        # Initialize browser pool
        await searcher.initialize()
        
        # Execute batch search
        total_start = time.time()
        results = await searcher.batch_search_concurrent(search_records)
        total_duration = time.time() - total_start
        
        # Generate comprehensive report
        print(f"\n{'='*60}")
        print("🎯 OPTIMIZED BATCH PROCESSING REPORT")
        print('='*60)
        
        matches = [r for r in results if r.matches_found > 0]
        no_matches = [r for r in results if r.matches_found == 0 and r.status != 'Error']
        errors = [r for r in results if r.status == 'Error']
        
        print(f"📊 PERFORMANCE SUMMARY:")
        print(f"   Total Searches: {len(results)}")
        print(f"   Total Time: {total_duration:.2f}s")
        print(f"   Average per Search: {total_duration/len(results):.2f}s")
        print(f"   Throughput: {len(results)/(total_duration/60):.1f} searches/minute")
        
        print(f"\n📋 RESULTS BREAKDOWN:")
        print(f"   ✅ Found Matches: {len(matches)}")
        print(f"   ⭕ No Matches: {len(no_matches)}")
        print(f"   ❌ Errors: {len(errors)}")
        print(f"   🎯 Success Rate: {((len(matches) + len(no_matches))/len(results)*100):.1f}%")
        
        # Performance comparison
        theoretical_sequential = len(results) * 7.6  # Average from analysis
        improvement = ((theoretical_sequential - total_duration) / theoretical_sequential) * 100
        print(f"\n⚡ OPTIMIZATION IMPACT:")
        print(f"   Sequential Est: {theoretical_sequential:.1f}s")
        print(f"   Optimized Actual: {total_duration:.1f}s")
        print(f"   Performance Gain: {improvement:.1f}%")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_batch_results_{timestamp}"
        export_results_json(results, filename)
        print(f"\n💾 Results exported to {filename}.json")
        
        print('='*60)
        print("🎉 OPTIMIZED BATCH PROCESSING COMPLETED!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during batch processing: {str(e)}")
    finally:
        # Clean up resources
        await searcher.cleanup()

if __name__ == "__main__":
    asyncio.run(main())