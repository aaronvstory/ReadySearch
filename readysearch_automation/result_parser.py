"""
Result Parser for ReadySearch.com.au
====================================

This module handles parsing and analysis of search results from ReadySearch.com.au.
It extracts person information from result tables and provides exact name matching capabilities.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import Page, Locator


@dataclass
class PersonRecord:
    """Represents a person record from search results."""
    name: str
    location: str = ""
    birth_year: str = ""
    additional_info: str = ""
    confidence_score: float = 0.0
    
    def __post_init__(self):
        # Normalize the name for better matching
        self.normalized_name = self._normalize_name(self.name)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        normalized = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove common titles and suffixes
        titles = ['mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        words = normalized.split()
        filtered_words = []
        
        for word in words:
            clean_word = word.strip('.,')
            if clean_word not in titles + suffixes:
                filtered_words.append(clean_word)
        
        return ' '.join(filtered_words)


class ResultParser:
    """Parse search results from ReadySearch.com.au"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
        # Updated selectors for ReadySearch.com.au
        self.selectors = {
            'results_table': 'table, .results-table, .search-results',
            'result_rows': 'tr, .result-row, .person-record',
            'person_name': '.name, .person-name, td:first-child, .result-name',
            'location': '.location, .address, .place',
            'birth_info': '.birth, .dob, .year',
            'no_results': '.no-results, .no-matches, .empty-results',
            'error_message': '.error, .alert-error, .message-error',
            'popup_close': '.close, .dismiss, button[class*="close"]',
            'continue_button': '.continue, .next, button[class*="continue"]'
        }
    
    async def extract_search_results(self) -> List[PersonRecord]:
        """
        Extract person records from the current search results page.
        
        Returns:
            List of PersonRecord objects found on the page
        """
        try:
            self.logger.debug("Starting result extraction")
            
            # Wait for page to load completely
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Handle any popups first
            await self._handle_popups()
            
            # Check for no results message
            if await self._check_no_results():
                self.logger.info("No results found on page")
                return []
            
            # Extract results from table or list format
            results = await self._extract_from_table()
            
            if not results:
                # Try alternative extraction methods
                results = await self._extract_from_divs()
            
            self.logger.info(f"Extracted {len(results)} person records")
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting results: {str(e)}")
            return []
    
    async def _handle_popups(self) -> None:
        """Handle any popups or modal dialogs."""
        try:
            # Common popup patterns for ReadySearch
            popup_selectors = [
                'button:has-text("OK")',
                'button:has-text("Close")',
                'button:has-text("Continue")',
                '.popup .close',
                '.modal .close',
                '.alert .close'
            ]
            
            for selector in popup_selectors:
                try:
                    popup_element = self.page.locator(selector).first
                    if await popup_element.is_visible(timeout=2000):
                        self.logger.debug(f"Closing popup with selector: {selector}")
                        await popup_element.click()
                        await self.page.wait_for_timeout(1000)
                        break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Popup handling error: {str(e)}")
    
    async def _check_no_results(self) -> bool:
        """Check if the page indicates no results were found."""
        try:
            no_results_indicators = [
                'text="No records found"',
                'text="No results"',
                'text="No matches"',
                '.no-results',
                '.empty-results'
            ]
            
            for indicator in no_results_indicators:
                try:
                    element = self.page.locator(indicator).first
                    if await element.is_visible(timeout=2000):
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    async def _extract_from_table(self) -> List[PersonRecord]:
        """Extract results from table format."""
        results = []
        
        try:
            # Find tables
            tables = self.page.locator('table')
            table_count = await tables.count()
            
            for i in range(table_count):
                table = tables.nth(i)
                
                # Get all rows except header
                rows = table.locator('tr')
                row_count = await rows.count()
                
                # Skip header row if present
                start_row = 1 if row_count > 1 else 0
                
                for j in range(start_row, row_count):
                    row = rows.nth(j)
                    
                    try:
                        person = await self._extract_person_from_row(row)
                        if person and person.name:
                            results.append(person)
                    except Exception as e:
                        self.logger.debug(f"Error extracting person from row {j}: {str(e)}")
                        continue
            
        except Exception as e:
            self.logger.debug(f"Table extraction error: {str(e)}")
        
        return results
    
    async def _extract_from_divs(self) -> List[PersonRecord]:
        """Extract results from div-based layout."""
        results = []
        
        try:
            # Look for common result container patterns
            container_selectors = [
                '.result-item',
                '.person-result',
                '.search-result',
                '[class*="result"]',
                '[class*="person"]'
            ]
            
            for selector in container_selectors:
                containers = self.page.locator(selector)
                count = await containers.count()
                
                if count > 0:
                    for i in range(count):
                        container = containers.nth(i)
                        
                        try:
                            person = await self._extract_person_from_container(container)
                            if person and person.name:
                                results.append(person)
                        except Exception as e:
                            self.logger.debug(f"Error extracting person from container {i}: {str(e)}")
                            continue
                    
                    if results:
                        break  # Found results, stop trying other selectors
            
        except Exception as e:
            self.logger.debug(f"Div extraction error: {str(e)}")
        
        return results
    
    async def _extract_person_from_row(self, row: Locator) -> Optional[PersonRecord]:
        """Extract person information from a table row."""
        try:
            cells = row.locator('td')
            cell_count = await cells.count()
            
            if cell_count == 0:
                return None
            
            # Extract name (usually first cell)
            name = ""
            if cell_count > 0:
                name_text = await cells.nth(0).inner_text()
                name = name_text.strip()
            
            # Extract location (often second cell)
            location = ""
            if cell_count > 1:
                location_text = await cells.nth(1).inner_text()
                location = location_text.strip()
            
            # Extract additional info from remaining cells
            additional_info = ""
            if cell_count > 2:
                info_parts = []
                for i in range(2, cell_count):
                    cell_text = await cells.nth(i).inner_text()
                    if cell_text.strip():
                        info_parts.append(cell_text.strip())
                additional_info = " | ".join(info_parts)
            
            if name:
                return PersonRecord(
                    name=name,
                    location=location,
                    additional_info=additional_info
                )
            
        except Exception as e:
            self.logger.debug(f"Row extraction error: {str(e)}")
        
        return None
    
    async def _extract_person_from_container(self, container: Locator) -> Optional[PersonRecord]:
        """Extract person information from a div container."""
        try:
            # Try to find name
            name = ""
            name_selectors = ['.name', '.person-name', '.title', 'h3', 'h4', '.heading']
            
            for selector in name_selectors:
                try:
                    name_element = container.locator(selector).first
                    if await name_element.is_visible():
                        name = await name_element.inner_text()
                        name = name.strip()
                        break
                except:
                    continue
            
            # If no specific name selector, try getting all text and parsing
            if not name:
                all_text = await container.inner_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                if lines:
                    name = lines[0]  # Assume first line is the name
            
            # Try to find location
            location = ""
            location_selectors = ['.location', '.address', '.place', '.city']
            
            for selector in location_selectors:
                try:
                    loc_element = container.locator(selector).first
                    if await loc_element.is_visible():
                        location = await loc_element.inner_text()
                        location = location.strip()
                        break
                except:
                    continue
            
            if name:
                return PersonRecord(name=name, location=location)
            
        except Exception as e:
            self.logger.debug(f"Container extraction error: {str(e)}")
        
        return None
    
    async def wait_for_results(self, timeout: int = 30000) -> bool:
        """
        Wait for search results to appear.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if results appear, False if timeout
        """
        try:
            # Wait for either results or no-results message
            await self.page.wait_for_function(
                """
                () => {
                    // Check for table with data
                    const tables = document.querySelectorAll('table');
                    for (let table of tables) {
                        if (table.rows.length > 1) return true;
                    }
                    
                    // Check for result containers
                    const containers = document.querySelectorAll('[class*="result"], [class*="person"]');
                    if (containers.length > 0) return true;
                    
                    // Check for no results message
                    const noResults = document.querySelector('[class*="no-result"], [class*="empty"]');
                    if (noResults) return true;
                    
                    return false;
                }
                """,
                timeout=timeout
            )
            return True
            
        except Exception as e:
            self.logger.warning(f"Timeout waiting for results: {str(e)}")
            return False


class NameMatcher:
    """Advanced name matching for exact match detection."""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        
        # Common name variations
        self.name_variations = {
            'william': ['bill', 'will', 'billy'],
            'robert': ['bob', 'rob', 'bobby'],
            'richard': ['rick', 'dick', 'rich'],
            'james': ['jim', 'jimmy'],
            'michael': ['mike', 'mick'],
            'david': ['dave', 'davy'],
            'christopher': ['chris'],
            'matthew': ['matt'],
            'anthony': ['tony'],
            'daniel': ['dan', 'danny'],
            'elizabeth': ['liz', 'beth', 'betty'],
            'jennifer': ['jen', 'jenny'],
            'margaret': ['meg', 'maggie', 'peggy'],
            'catherine': ['kate', 'cathy', 'katie'],
            'patricia': ['pat', 'patty'],
            'susan': ['sue', 'susie'],
            'deborah': ['deb', 'debbie'],
            'barbara': ['barb', 'babs']
        }
    
    def find_exact_matches(self, search_name: str, results: List[PersonRecord]) -> Tuple[bool, List[PersonRecord]]:
        """
        Find exact matches for the search name in results.
        
        Args:
            search_name: The name being searched for
            results: List of PersonRecord objects to search through
            
        Returns:
            Tuple of (match_found: bool, matching_records: List[PersonRecord])
        """
        if not search_name or not results:
            return False, []
        
        normalized_search = self._normalize_name(search_name)
        matches = []
        
        for record in results:
            if self._is_match(normalized_search, record.normalized_name):
                record.confidence_score = self._calculate_confidence(normalized_search, record.normalized_name)
                matches.append(record)
        
        # Sort by confidence score
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.logger.info(f"Found {len(matches)} matches for '{search_name}'")
        return len(matches) > 0, matches
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        normalized = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove common titles and suffixes
        titles = ['mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        words = normalized.split()
        filtered_words = []
        
        for word in words:
            clean_word = word.strip('.,')
            if clean_word not in titles + suffixes:
                filtered_words.append(clean_word)
        
        return ' '.join(filtered_words)
    
    def _is_match(self, search_name: str, result_name: str) -> bool:
        """Check if two normalized names match."""
        if search_name == result_name:
            return True
        
        if not self.strict_mode:
            return self._is_partial_match(search_name, result_name)
        
        return False
    
    def _is_partial_match(self, search_name: str, result_name: str) -> bool:
        """Check for partial matches including name variations."""
        search_words = search_name.split()
        result_words = result_name.split()
        
        # Check if all search words have matches in result
        for search_word in search_words:
            found_match = False
            
            # Direct match
            if search_word in result_words:
                found_match = True
            else:
                # Check variations
                for result_word in result_words:
                    if self._are_name_variations(search_word, result_word):
                        found_match = True
                        break
            
            if not found_match:
                return False
        
        return True
    
    def _are_name_variations(self, name1: str, name2: str) -> bool:
        """Check if two names are variations of each other."""
        # Check direct variations
        for full_name, variations in self.name_variations.items():
            if (name1 == full_name and name2 in variations) or \
               (name2 == full_name and name1 in variations) or \
               (name1 in variations and name2 in variations):
                return True
        
        return False
    
    def _calculate_confidence(self, search_name: str, result_name: str) -> float:
        """Calculate confidence score for a match."""
        if search_name == result_name:
            return 1.0
        
        search_words = set(search_name.split())
        result_words = set(result_name.split())
        
        # Jaccard similarity
        intersection = len(search_words & result_words)
        union = len(search_words | result_words)
        
        if union == 0:
            return 0.0
        
        return intersection / union
