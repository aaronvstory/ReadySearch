"""
High-Performance ReadySearch Automation with Strict Timing Controls
- Max 30 seconds per action
- Max 60 seconds per search
- Headless mode only
- Aggressive timeouts for speed
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Set up minimal logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class SpeedTestResult:
    """Result of a speed test search."""
    name: str
    birth_year: int
    status: str  # 'match', 'no_match', 'error', 'timeout'
    matches_found: int = 0
    total_time: float = 0.0
    match_details: List[Dict[str, Any]] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.match_details is None:
            self.match_details = []

class SpeedTestAutomation:
    """High-performance automation with strict timing controls."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results: List[SpeedTestResult] = []
        
    async def setup_browser(self) -> bool:
        """Setup browser with aggressive performance settings."""
        try:
            logger.info("🚀 Starting high-performance browser...")
            start_time = time.time()
            
            from playwright.async_api import async_playwright
            
            # Start playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser with performance optimizations
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Always headless for speed
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-extensions',
                    '--disable-ipc-flooding-protection',
                    '--disable-hang-monitor',
                    '--disable-prompt-on-repost',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-client-side-phishing-detection',
                    '--disable-sync',
                    '--disable-translate',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            )
            
            # Create context with minimal settings
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                locale='en-AU',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page with aggressive timeouts
            self.page = await self.context.new_page()
            self.page.set_default_timeout(30000)  # 30 second max per action
            self.page.set_default_navigation_timeout(30000)  # 30 second max navigation
            
            setup_time = time.time() - start_time
            logger.info(f"✅ Browser setup completed in {setup_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {str(e)}")
            return False
    
    async def search_single_name(self, name: str, birth_year: int) -> SpeedTestResult:
        """Search for a single name with strict timing controls."""
        result = SpeedTestResult(name=name, birth_year=birth_year, status="error")
        search_start = time.time()
        
        try:
            logger.info(f"🔍 Speed test: {name} ({birth_year}) - Max 60s")
            
            # Step 1: Navigate to search page (max 30s)
            logger.info("🌐 Navigating to ReadySearch...")
            await self.page.goto("https://readysearch.com.au/products?person", timeout=30000)
            
            # Step 2: Handle any popups quickly (max 5s)
            try:
                await self.page.wait_for_selector('.modal, .popup, .alert', timeout=5000)
                await self.page.click('.close, .modal-close, button:contains("Close")', timeout=5000)
            except:
                pass  # No popups found
            
            # Step 3: Find and fill name input (max 10s)
            logger.info(f"✏️ Entering name: {name}")
            name_input = await self.page.wait_for_selector('input[type="text"]', timeout=10000)
            await name_input.click()
            await name_input.fill(name)
            
            # Step 4: Set birth year ranges (max 10s)
            start_year = birth_year - 2
            end_year = birth_year + 2
            logger.info(f"📅 Setting birth year range: {start_year} - {end_year}")
            
            # Find year dropdowns
            try:
                year_selects = await self.page.query_selector_all('select')
                if len(year_selects) >= 2:
                    await year_selects[0].select_option(str(start_year))
                    await year_selects[1].select_option(str(end_year))
                    logger.info(f"✅ Birth year range set")
                else:
                    logger.warning("⚠️ Year dropdowns not found")
            except Exception as e:
                logger.warning(f"⚠️ Year setting failed: {str(e)}")
            
            # Step 5: Submit search (max 5s)
            logger.info("🚀 Submitting search...")
            submit_button = await self.page.wait_for_selector('.sch_but, button[type="submit"]', timeout=5000)
            await submit_button.click()
            
            # Handle alert if present
            try:
                await self.page.wait_for_event('dialog', timeout=5000)
                await self.page.click('text=OK', timeout=2000)
            except:
                pass
            
            # Step 6: Wait for results (max 20s)
            logger.info("⏳ Waiting for results...")
            await self.page.wait_for_load_state('networkidle', timeout=20000)
            
            # Step 7: Extract results quickly (max 10s)
            logger.info("📊 Extracting results...")
            page_content = await self.page.content()
            
            # Find dates of birth in the page
            import re
            dob_pattern = r'Date of Birth:\s*(\d{2}/\d{2}/\d{4})'
            dob_matches = re.findall(dob_pattern, page_content)
            
            if dob_matches:
                result.status = "match"
                result.matches_found = len(dob_matches)
                result.match_details = []
                
                for i, dob in enumerate(dob_matches):
                    # Extract year from date
                    year = int(dob.split('/')[-1])
                    result.match_details.append({
                        'date_of_birth': dob,
                        'year': year,
                        'name': name,
                        'within_range': start_year <= year <= end_year
                    })
                
                logger.info(f"✅ {result.matches_found} matches found for {name}")
                
                # Check if all matches are within range
                invalid_matches = [m for m in result.match_details if not m['within_range']]
                if invalid_matches:
                    logger.warning(f"⚠️ {len(invalid_matches)} matches outside expected range")
                    
            else:
                result.status = "no_match"
                logger.info(f"○ No matches found for {name}")
            
            result.total_time = time.time() - search_start
            logger.info(f"🏁 Search completed in {result.total_time:.2f}s")
            
            # Check if we exceeded 60s limit
            if result.total_time > 60:
                logger.warning(f"⚠️ Search exceeded 60s limit ({result.total_time:.2f}s)")
                result.status = "timeout"
                result.error_message = f"Search exceeded 60s limit ({result.total_time:.2f}s)"
            
            return result
            
        except Exception as e:
            result.total_time = time.time() - search_start
            result.error_message = str(e)
            logger.error(f"❌ Search failed for {name}: {str(e)} ({result.total_time:.2f}s)")
            return result
    
    async def run_speed_tests(self, names_and_years: List[tuple]) -> List[SpeedTestResult]:
        """Run speed tests for all names."""
        logger.info(f"🚀 Starting speed tests for {len(names_and_years)} names")
        
        # Setup browser
        if not await self.setup_browser():
            logger.error("❌ Browser setup failed")
            return []
        
        results = []
        
        try:
            for i, (name, birth_year) in enumerate(names_and_years, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"🎯 Test {i}/{len(names_and_years)}: {name} ({birth_year})")
                logger.info(f"{'='*60}")
                
                result = await self.search_single_name(name, birth_year)
                results.append(result)
                
                # Brief pause between searches
                if i < len(names_and_years):
                    await asyncio.sleep(1)
                
        finally:
            # Cleanup browser
            if self.browser:
                await self.browser.close()
                await self.playwright.stop()
        
        return results
    
    def print_results_summary(self, results: List[SpeedTestResult]):
        """Print comprehensive results summary."""
        logger.info(f"\n{'='*80}")
        logger.info("📊 SPEED TEST RESULTS SUMMARY")
        logger.info(f"{'='*80}")
        
        total_time = sum(r.total_time for r in results)
        matches = [r for r in results if r.status == "match"]
        no_matches = [r for r in results if r.status == "no_match"]
        errors = [r for r in results if r.status == "error"]
        timeouts = [r for r in results if r.status == "timeout"]
        
        logger.info(f"🏁 Total execution time: {total_time:.2f}s")
        logger.info(f"✅ Matches found: {len(matches)}")
        logger.info(f"○ No matches: {len(no_matches)}")
        logger.info(f"❌ Errors: {len(errors)}")
        logger.info(f"⏰ Timeouts: {len(timeouts)}")
        
        logger.info(f"\n{'='*80}")
        logger.info("📋 DETAILED RESULTS")
        logger.info(f"{'='*80}")
        
        for result in results:
            logger.info(f"\n🔍 {result.name} (born ~{result.birth_year})")
            logger.info(f"   Status: {result.status.upper()}")
            logger.info(f"   Time: {result.total_time:.2f}s")
            
            if result.status == "match":
                logger.info(f"   Matches: {result.matches_found}")
                for i, match in enumerate(result.match_details, 1):
                    status = "✅" if match['within_range'] else "❌"
                    logger.info(f"   {status} Match {i}: DOB {match['date_of_birth']} (year {match['year']})")
                    
            elif result.status == "no_match":
                logger.info(f"   No matches found in database")
                
            elif result.status == "error":
                logger.info(f"   Error: {result.error_message}")
                
            elif result.status == "timeout":
                logger.info(f"   Timeout: {result.error_message}")

async def main():
    """Main speed test execution."""
    names_and_years = [
        ("Andro Cutuk", 1975),
        ("Anthony Bek", 1993), 
        ("Ghafoor Jaggi Nadery", 1978)
    ]
    
    automation = SpeedTestAutomation()
    results = await automation.run_speed_tests(names_and_years)
    automation.print_results_summary(results)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())