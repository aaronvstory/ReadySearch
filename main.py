"""Main automation script for ReadySearch.com.au name matching."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from config import Config
from readysearch_automation import (
    InputLoader, BrowserController, Reporter
)
from readysearch_automation.enhanced_result_parser import (
    EnhancedResultParser, EnhancedNameMatcher, SearchStatistics
)

# Set up logging
def setup_logging(config: Dict[str, Any]):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config['log_level']),
        format=config['log_format'],
        handlers=[
            logging.FileHandler(config['log_file']),
            logging.StreamHandler(sys.stdout)
        ]
    )

class ReadySearchAutomation:
    """Main automation class for ReadySearch.com.au with enhanced validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser_controller = BrowserController(config)
        self.name_matcher = EnhancedNameMatcher(strict_mode=True)
        self.reporter = Reporter(config['output_file'])
        
        # Set up logging
        setup_logging(config)
        self.logger = logging.getLogger(__name__)
        
    async def run_automation(self, names: List[str]) -> bool:
        """
        Run the complete automation process with enhanced validation.
        
        Args:
            names: List of names to search
            
        Returns:
            True if automation completed successfully
        """
        try:
            self.logger.info(f"Starting enhanced automation for {len(names)} names")
            
            # Start browser
            await self.browser_controller.start_browser()
            
            # Navigate to search page
            navigation_success = await self.browser_controller.navigate_to_search_page()
            if not navigation_success:
                self.logger.error("Failed to navigate to search page")
                return False
                
            # Process each name with enhanced validation
            for i, name in enumerate(names, 1):
                # Extract name string for logging and reporting
                name_str = name.name if hasattr(name, 'name') else str(name)
                self.logger.info(f"Processing {i}/{len(names)}: {name_str}")
                
                try:
                    # Search for the name with enhanced validation
                    search_result = await self._search_single_name_enhanced(name)
                    
                    # Process results with detailed statistics
                    self._process_search_result(name, search_result)
                        
                except Exception as e:
                    self.logger.error(f"Error processing {name_str}: {str(e)}")
                    self.reporter.add_result(
                        name=name_str,
                        status='Error',
                        error=str(e)
                    )
                    
                # Rate limiting delay
                if i < len(names):
                    await asyncio.sleep(self.config['delay'])
                    
            # Save results
            self.reporter.save_results_csv()
            self.reporter.save_results_json()
            self.reporter.print_summary()
            
            self.logger.info("Enhanced automation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
            return False
            
        finally:
            # Clean up browser
            await self.browser_controller.cleanup()
    
    def _process_search_result(self, name: str, search_result: Dict[str, Any]):
        """Process search result with enhanced statistics."""
        try:
            status = search_result.get('status', 'Error')
            statistics = search_result.get('statistics')
            matches = search_result.get('exact_matches', [])
            all_results = search_result.get('all_results', [])
            
            if status == 'Match':
                # Add detailed match information
                match_details = []
                for match in matches:
                    match_details.append({
                        'matched_name': match.name,
                        'location': match.location,
                        'confidence': match.confidence_score,
                        'match_type': match.match_type,
                        'additional_info': match.additional_info
                    })
                
                self.reporter.add_result(
                    name=name,
                    status='Match',
                    matches_found=len(matches),
                    total_results=statistics.total_results_found if statistics else 0,
                    exact_matches=statistics.exact_matches if statistics else 0,
                    partial_matches=statistics.partial_matches if statistics else 0,
                    search_time=statistics.search_time if statistics else 0.0,
                    match_details=match_details
                )
                
                # Log detailed match information
                self.logger.info(f"✅ MATCH FOUND for '{name}':")
                self.logger.info(f"   Total results: {statistics.total_results_found if statistics else 0}")
                self.logger.info(f"   Exact matches: {len(matches)}")
                for i, match in enumerate(matches, 1):
                    self.logger.info(f"   Match {i}: {match.name} ({match.confidence_score:.2f} confidence)")
                    if match.location:
                        self.logger.info(f"            Location: {match.location}")
                
            elif status == 'No Match':
                self.reporter.add_result(
                    name=name,
                    status='No Match',
                    results_found=statistics.total_results_found if statistics else 0,
                    search_time=statistics.search_time if statistics else 0.0,
                    total_results=statistics.total_results_found if statistics else 0
                )
                
                # Log detailed no-match information
                self.logger.info(f"❌ NO MATCH for '{name}':")
                self.logger.info(f"   Total results found: {statistics.total_results_found if statistics else 0}")
                if statistics and statistics.total_results_found > 0:
                    self.logger.info(f"   Results examined but none matched exactly")
                    # Log first few results for debugging
                    for i, result in enumerate(all_results[:3], 1):
                        self.logger.info(f"   Result {i}: {result.name} (no match)")
                else:
                    self.logger.info(f"   No results returned from search")
                
            else:
                # Error case
                self.reporter.add_result(
                    name=name,
                    status='Error',
                    error=search_result.get('error', 'Unknown error'),
                    search_time=statistics.search_time if statistics else 0.0
                )
                
                self.logger.error(f"❗ ERROR searching for '{name}': {search_result.get('error', 'Unknown error')}")
        
        except Exception as e:
            self.logger.error(f"Error processing search result for {name}: {str(e)}")
            
    async def _search_single_name_enhanced(self, name: str) -> Dict[str, Any]:
        """
        Search for a single name with enhanced validation and retry logic.
        
        Args:
            name: Name to search for
            
        Returns:
            Dictionary with enhanced search results including statistics
        """
        last_error = None
        
        for attempt in range(self.config['max_retries']):
            try:
                self.logger.debug(f"Enhanced search attempt {attempt + 1} for: {name}")
                
                # Perform search
                search_result = await self.browser_controller.search_name(name)
                
                if search_result.get('status') == 'error':
                    raise Exception(search_result.get('error', 'Search failed'))
                
                # Enhanced result parsing with validation
                result_parser = EnhancedResultParser(self.browser_controller.page)
                statistics, extracted_results = await result_parser.extract_and_validate_results(name)
                
                # Check for errors in statistics
                if statistics.error_occurred:
                    raise Exception(statistics.error_message)
                
                # Find exact matches using enhanced matcher
                match_found, exact_matches = self.name_matcher.find_exact_matches(name, extracted_results)
                
                if match_found:
                    return {
                        'status': 'Match',
                        'exact_matches': exact_matches,
                        'all_results': extracted_results,
                        'statistics': statistics
                    }
                else:
                    return {
                        'status': 'No Match',
                        'exact_matches': [],
                        'all_results': extracted_results,
                        'statistics': statistics
                    }
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed for {name}: {str(e)}")
                
                if attempt < self.config['max_retries'] - 1:
                    # Wait before retry
                    retry_delay = self.config['retry_delay'] * (attempt + 1)
                    self.logger.info(f"Waiting {retry_delay}s before retry...")
                    await asyncio.sleep(retry_delay)
                    
                    # Try to navigate back to search page
                    try:
                        await self.browser_controller.navigate_to_search_page()
                    except:
                        pass
                        
        # All attempts failed
        return {
            'status': 'Error',
            'error': str(last_error) if last_error else 'All retry attempts failed',
            'statistics': SearchStatistics(error_occurred=True, error_message=str(last_error))
        }

    async def _search_single_name(self, name: str) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return await self._search_single_name_enhanced(name)

async def main():
    """Main entry point."""
    try:
        # Get configuration
        config = Config.get_config()
        
        # Load input names
        input_loader = InputLoader(config['input_file'])
        
        # Check if input file exists, create sample if not
        if not Path(config['input_file']).exists():
            print(f"Input file '{config['input_file']}' not found.")
            create_sample = input("Create sample input file? (y/n): ").lower().strip()
            
            if create_sample == 'y':
                InputLoader.create_sample_input(config['input_file'])
                print(f"Sample input file created: {config['input_file']}")
                print("Please edit the file with your names and run the script again.")
                return
            else:
                print("Exiting. Please create input file and try again.")
                return
                
        # Load names
        names = input_loader.load_names()
        
        if not names:
            print("No names found in input file.")
            return
            
        print(f"Loaded {len(names)} names to search")
        print("\n🔍 Enhanced ReadySearch Automation")
        print("Features:")
        print("  ✅ Accurate result validation")
        print("  ✅ Detailed match statistics")
        print("  ✅ Confidence scoring")
        print("  ✅ Enhanced error handling")
        print()
        
        # Confirm before starting
        proceed = input("Start enhanced automation? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Automation cancelled.")
            return
            
        # Run automation
        automation = ReadySearchAutomation(config)
        success = await automation.run_automation(names)
        
        if success:
            print(f"\n✅ Enhanced automation completed! Results saved to: {config['output_file']}")
        else:
            print("\n❌ Automation failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.error(f"Main error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())