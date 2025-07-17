"""Main automation script for ReadySearch.com.au name matching."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

from config import Config
from readysearch_automation import (
    InputLoader, BrowserController, ResultParser, 
    NameMatcher, Reporter
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
    """Main automation class for ReadySearch.com.au."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser_controller = BrowserController(config)
        self.name_matcher = NameMatcher(strict_mode=True)
        self.reporter = Reporter(config['output_file'])
        
        # Set up logging
        setup_logging(config)
        self.logger = logging.getLogger(__name__)
        
    async def run_automation(self, names: List[str]) -> bool:
        """
        Run the complete automation process.
        
        Args:
            names: List of names to search
            
        Returns:
            True if automation completed successfully
        """
        try:
            self.logger.info(f"Starting automation for {len(names)} names")
            
            # Start browser
            await self.browser_controller.start_browser()
            
            # Navigate to search page
            navigation_success = await self.browser_controller.navigate_to_search_page()
            if not navigation_success:
                self.logger.error("Failed to navigate to search page")
                return False
                
            # Process each name
            for i, name in enumerate(names, 1):
                self.logger.info(f"Processing {i}/{len(names)}: {name}")
                
                try:
                    # Search for the name
                    search_result = await self._search_single_name(name)
                    
                    # Add result to reporter
                    if search_result['status'] == 'Match':
                        self.reporter.add_result(
                            name=name,
                            status='Match',
                            matches_found=len(search_result.get('matches', [])),
                            match_details=search_result.get('matches', [])
                        )
                    elif search_result['status'] == 'No Match':
                        self.reporter.add_result(
                            name=name,
                            status='No Match',
                            results_found=len(search_result.get('all_results', []))
                        )
                    else:
                        self.reporter.add_result(
                            name=name,
                            status='Error',
                            error=search_result.get('error', 'Unknown error')
                        )
                        
                except Exception as e:
                    self.logger.error(f"Error processing {name}: {str(e)}")
                    self.reporter.add_result(
                        name=name,
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
            
            self.logger.info("Automation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
            return False
            
        finally:
            # Clean up browser
            await self.browser_controller.cleanup()
            
    async def _search_single_name(self, name: str) -> Dict[str, Any]:
        """
        Search for a single name with retry logic.
        
        Args:
            name: Name to search for
            
        Returns:
            Dictionary with search results
        """
        last_error = None
        
        for attempt in range(self.config['max_retries']):
            try:
                self.logger.debug(f"Search attempt {attempt + 1} for: {name}")
                
                # Perform search
                search_result = await self.browser_controller.search_name(name)
                
                if search_result.get('status') == 'error':
                    raise Exception(search_result.get('error', 'Search failed'))
                    
                # Parse results
                result_parser = ResultParser(self.browser_controller.page)
                extracted_results = await result_parser.extract_search_results()
                
                # Find exact matches
                match_found, matches = self.name_matcher.find_exact_matches(
                    name, extracted_results
                )
                
                if match_found:
                    return {
                        'status': 'Match',
                        'matches': matches,
                        'all_results': extracted_results
                    }
                else:
                    return {
                        'status': 'No Match',
                        'matches': [],
                        'all_results': extracted_results
                    }
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed for {name}: {str(e)}")
                
                if attempt < self.config['max_retries'] - 1:
                    # Wait before retry
                    await asyncio.sleep(self.config['retry_delay'] * (attempt + 1))
                    
                    # Try to navigate back to search page
                    try:
                        await self.browser_controller.navigate_to_search_page()
                    except:
                        pass
                        
        # All attempts failed
        return {
            'status': 'Error',
            'error': str(last_error) if last_error else 'All retry attempts failed'
        }

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
        
        # Confirm before starting
        proceed = input("Start automation? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Automation cancelled.")
            return
            
        # Run automation
        automation = ReadySearchAutomation(config)
        success = await automation.run_automation(names)
        
        if success:
            print(f"\nAutomation completed! Results saved to: {config['output_file']}")
        else:
            print("\nAutomation failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.error(f"Main error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())