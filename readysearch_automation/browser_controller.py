"""Browser automation and page interaction module."""

import asyncio
import logging
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import Optional, Dict, Any
from .popup_handler import PopupHandler

logger = logging.getLogger(__name__)

class BrowserController:
    """Controls browser automation and page interactions."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.popup_handler: Optional[PopupHandler] = None
        
    async def start_browser(self):
        """Initialize browser and create page."""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with configuration
            self.browser = await playwright.chromium.launch(
                headless=self.config['headless'],
                args=self.config['browser_args']
            )
            
            # Create browser context with realistic settings
            self.context = await self.browser.new_context(
                user_agent=self.config['user_agent'],
                viewport={'width': 1920, 'height': 1080},
                locale='en-AU',  # Australian locale for ReadySearch
                timezone_id='Australia/Sydney'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set up popup handler
            self.popup_handler = PopupHandler(self.page)
            await self.popup_handler.setup_dialog_handlers()
            
            # Set timeouts
            self.page.set_default_timeout(self.config['element_timeout'])
            self.page.set_default_navigation_timeout(self.config['page_timeout'])
            
            logger.info("Browser started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            await self.cleanup()
            raise
            
    async def navigate_to_search_page(self) -> bool:
        """
        Navigate to ReadySearch person search page and handle initial setup.
        
        Returns:
            True if navigation successful
        """
        try:
            logger.info(f"Navigating to ReadySearch person search: {self.config['base_url']}")
            
            # Navigate to the person search page
            response = await self.page.goto(
                self.config['base_url'],
                wait_until="networkidle"
            )
            
            if response and response.status >= 400:
                logger.error(f"HTTP error {response.status} when loading page")
                return False
                
            # Wait for page to be ready and handle pop-ups
            await self.popup_handler.wait_for_page_ready()
            
            # Handle cookie consent if present
            await self.popup_handler.handle_cookie_consent()
            
            # Wait for person search form to be available
            await self._wait_for_person_search_form()
            
            logger.info("Successfully navigated to person search page")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to person search page: {str(e)}")
            return False

    async def _wait_for_person_search_form(self):
        """Wait for the person search form to be available."""
        try:
            # Wait for the main search form elements to be present
            form_selectors = [
                'input[name="name"]',
                'input[placeholder*="name"]',
                '#name',
                'form',
                '.search-form'
            ]
            
            for selector in form_selectors:
                try:
                    await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    logger.info(f"Person search form ready, found: {selector}")
                    return
                except:
                    continue
                    
            logger.warning("Person search form elements not found, continuing anyway")
            
        except Exception as e:
            logger.warning(f"Error waiting for person search form: {str(e)}")

    async def set_birth_year_range(self, start_year: int = None, end_year: int = None):
        """
        Set birth year range dropdowns if available.
        
        Args:
            start_year: Starting birth year (defaults to config value)
            end_year: Ending birth year (defaults to config value)
        """
        try:
            if start_year is None:
                start_year = self.config.get('birth_year_start', 1900)
            if end_year is None:
                end_year = self.config.get('birth_year_end', 2025)
                
            # Try to set start year dropdown
            await self._set_birth_year_dropdown('start', start_year)
            
            # Try to set end year dropdown  
            await self._set_birth_year_dropdown('end', end_year)
            
        except Exception as e:
            logger.warning(f"Error setting birth year range: {str(e)}")

    async def _set_birth_year_dropdown(self, dropdown_type: str, year: int):
        """
        Set a specific birth year dropdown.
        
        Args:
            dropdown_type: 'start' or 'end'
            year: Year to select
        """
        try:
            # Get selectors from config
            selectors = self.config.get('selectors', {})
            
            if dropdown_type == 'start':
                dropdown_selectors = [
                    selectors.get('birth_year_start', ''),
                    'select[name="birth_year_start"]',
                    'select[name="start_year"]', 
                    '#start_year',
                    'select:has(option[value*="19"])'  # Fallback for year dropdowns
                ]
            else:
                dropdown_selectors = [
                    selectors.get('birth_year_end', ''),
                    'select[name="birth_year_end"]',
                    'select[name="end_year"]',
                    '#end_year',
                    'select:has(option[value*="20"])'  # Fallback for year dropdowns
                ]
                
            for selector in dropdown_selectors:
                if not selector:  # Skip empty selectors
                    continue
                    
                try:
                    dropdown = await self.page.query_selector(selector)
                    if dropdown:
                        is_visible = await dropdown.is_visible()
                        if is_visible:
                            # Try to select the year
                            await dropdown.select_option(str(year))
                            logger.info(f"Set {dropdown_type} year to {year} using {selector}")
                            return
                            
                except Exception as e:
                    logger.debug(f"Birth year selector {selector} failed: {str(e)}")
                    continue
                    
            logger.debug(f"No {dropdown_type} year dropdown found or selectable")
            
        except Exception as e:
            logger.warning(f"Error setting {dropdown_type} year dropdown: {str(e)}")
            
    async def search_name(self, name: str) -> Dict[str, Any]:
        """
        Search for a specific name on the page.
        
        Args:
            name: The name to search for
            
        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f"Searching for: {name}")
            
            # Handle any pop-ups before searching
            await self.popup_handler.handle_modal_popups()
            await self.popup_handler.handle_readysearch_popups()
            
            # Find search input field
            search_input = await self._find_search_input()
            if not search_input:
                return self._create_error_result(name, "Search input not found")
                
            # Clear and fill search input
            await search_input.click()
            await search_input.fill("")  # Clear existing text
            await search_input.type(name, delay=50)  # Type with human-like delay
            
            # Set birth year range if dropdowns are available
            await self.set_birth_year_range()
            
            # Submit search
            submit_success = await self._submit_search()
            if not submit_success:
                return self._create_error_result(name, "Failed to submit search")
                
            # Wait for results to load
            await self._wait_for_results()
            
            # Handle any post-search pop-ups
            await self.popup_handler.handle_modal_popups()
            await self.popup_handler.handle_readysearch_popups()
            
            logger.info(f"Search completed for: {name}")
            return {'name': name, 'status': 'search_completed'}
            
        except Exception as e:
            logger.error(f"Error searching for {name}: {str(e)}")
            return self._create_error_result(name, str(e))
            
    async def _find_search_input(self) -> Optional[Any]:
        """Find the name search input field using ReadySearch-specific selectors."""
        # Get selectors from config first
        selectors = self.config.get('selectors', {})
        
        search_selectors = [
            # ReadySearch-specific selectors from config
            selectors.get('name_input', ''),
            selectors.get('first_name_input', ''),
            selectors.get('last_name_input', ''),
            
            # ReadySearch-specific patterns
            'input[name="name"]',
            'input[name="first_name"]', 
            'input[name="last_name"]',
            'input[placeholder*="name"]',
            'input[placeholder*="first"]',
            'input[placeholder*="last"]',
            '#name',
            '#first_name',
            '#last_name',
            
            # Generic fallback patterns
            'input[type="text"]',
            'input[type="search"]',
            'input[name*="search"]',
            'input[name*="query"]',
            'input[placeholder*="search"]',
            'input[placeholder*="enter"]',
            
            # ID-based selectors
            '#search',
            '#query',
            '#searchInput',
            '#nameSearch',
            
            # Class-based selectors
            '.search-input',
            '.search-field',
            '.query-input',
            '[class*="search"]',
            
            # ARIA selectors
            '[role="searchbox"]',
            '[aria-label*="search"]',
            '[aria-label*="name"]'
        ]
        
        for selector in search_selectors:
            try:
                element = await self.page.wait_for_selector(
                    selector, 
                    timeout=2000,
                    state="visible"
                )
                if element:
                    # Verify element is interactable
                    is_enabled = await element.is_enabled()
                    is_visible = await element.is_visible()
                    
                    if is_enabled and is_visible:
                        logger.info(f"Found search input with selector: {selector}")
                        return element
                        
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {str(e)}")
                continue
                
        logger.error("No search input field found")
        return None
        
    async def _submit_search(self) -> bool:
        """Submit the search form using ReadySearch-specific selectors."""
        # Get selectors from config first
        selectors = self.config.get('selectors', {})
        
        submit_selectors = [
            # ReadySearch-specific blue arrow button
            '.sch_but',
            selectors.get('search_button', ''),
            
            # ReadySearch-specific patterns
            'button.sch_but',
            'input.sch_but',
            '[class*="sch_but"]',
            
            # Generic submit button patterns
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Search")',
            'button:has-text("Find")',
            'button:has-text("Go")',
            'button:has-text("Submit")',
            
            # Form submission
            'form button',
            '[class*="search"] button',
            '[class*="submit"]',
            
            # Icon buttons and arrows
            'button[aria-label*="search"]',
            '[role="button"]:has-text("Search")',
            'button:has-text("→")',
            'button:has-text("▶")',
            '[class*="arrow"]',
            '[class*="btn"]'
        ]
        
        for selector in submit_selectors:
            try:
                button = await self.page.wait_for_selector(
                    selector,
                    timeout=2000,
                    state="visible"
                )
                
                if button:
                    is_enabled = await button.is_enabled()
                    is_visible = await button.is_visible()
                    
                    if is_enabled and is_visible:
                        logger.info(f"Clicking submit button: {selector}")
                        await button.click()
                        return True
                        
            except Exception as e:
                logger.debug(f"Submit selector {selector} failed: {str(e)}")
                continue
                
        # Try pressing Enter as fallback
        try:
            logger.info("Trying Enter key to submit search")
            await self.page.keyboard.press('Enter')
            return True
        except Exception as e:
            logger.error(f"Enter key submission failed: {str(e)}")
            
        return False
        
    async def _wait_for_results(self):
        """Wait for search results to load."""
        try:
            # Wait for network activity to settle
            await self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # Look for results containers
            result_selectors = [
                '.results',
                '.search-results', 
                '[class*="result"]',
                '.result-list',
                '.search-result',
                '[id*="result"]'
            ]
            
            # Wait for any results container to appear
            for selector in result_selectors:
                try:
                    await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    logger.info(f"Results loaded, found container: {selector}")
                    break
                except:
                    continue
                    
            # Additional wait for dynamic content
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.warning(f"Error waiting for results: {str(e)}")
            
    def _create_error_result(self, name: str, error: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {
            'name': name,
            'status': 'error',
            'error': error
        }
        
    async def get_page_content(self) -> str:
        """Get current page HTML content."""
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {str(e)}")
            return ""
            
    async def take_screenshot(self, path: str):
        """Take screenshot for debugging."""
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")