"""
Enhanced result parser with proper validation and statistics
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import Page
import asyncio

@dataclass
class SearchStatistics:
    """Statistics for a search operation."""
    total_results_found: int = 0
    exact_matches: int = 0
    partial_matches: int = 0
    no_matches: int = 0
    search_time: float = 0.0
    error_occurred: bool = False
    error_message: str = ""

@dataclass  
class PersonResult:
    """Enhanced person result with validation."""
    name: str
    location: str = ""
    additional_info: str = ""
    match_type: str = "none"  # exact, partial, none
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}
        self.normalized_name = self._normalize_name(self.name)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        normalized = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove common titles and suffixes
        titles = ['mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady', 'rev']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'phd', 'md', 'esq']
        
        words = normalized.split()
        filtered_words = []
        
        for word in words:
            clean_word = word.strip('.,')
            if clean_word not in titles + suffixes:
                filtered_words.append(clean_word)
        
        return ' '.join(filtered_words)


class EnhancedResultParser:
    """Enhanced result parser with proper validation."""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
        # ReadySearch.com.au specific selectors
        self.selectors = {
            'results_container': [
                '.search-results',
                '.results',
                'table[class*="result"]',
                '.result-container',
                '[id*="result"]'
            ],
            'result_rows': [
                'tr',
                '.result-row',
                '.person-row',
                '[class*="result-item"]'
            ],
            'person_name': [
                'td:first-child',
                '.name',
                '.person-name',
                '.result-name',
                'a[href*="person"]'
            ],
            'no_results_indicators': [
                'text="No records found"',
                'text="No results"', 
                'text="No matches found"',
                '.no-results',
                '.empty-results',
                'text="0 results"'
            ]
        }
    
    async def extract_and_validate_results(self, search_name: str) -> Tuple[SearchStatistics, List[PersonResult]]:
        """
        Extract results and validate against search name.
        
        Args:
            search_name: The name that was searched for
            
        Returns:
            Tuple of (statistics, results_list)
        """
        start_time = asyncio.get_event_loop().time()
        stats = SearchStatistics()
        results = []
        
        try:
            self.logger.info(f"Extracting and validating results for: {search_name}")
            
            # Wait for page to load completely
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # Check for no results first
            if await self._check_no_results():
                stats.total_results_found = 0
                stats.no_matches = 1
                self.logger.info(f"No results found for '{search_name}'")
                return stats, []
            
            # Extract all results from the page
            raw_results = await self._extract_all_results()
            stats.total_results_found = len(raw_results)
            
            if not raw_results:
                stats.no_matches = 1
                self.logger.warning(f"No results extracted for '{search_name}' despite no 'no results' message")
                return stats, []
            
            # Validate each result against the search name
            validated_results = []
            for raw_result in raw_results:
                person_result = self._create_person_result(raw_result)
                match_type, confidence = self._validate_match(search_name, person_result.name)
                
                person_result.match_type = match_type
                person_result.confidence_score = confidence
                
                validated_results.append(person_result)
                
                # Update statistics
                if match_type == "exact":
                    stats.exact_matches += 1
                elif match_type == "partial":
                    stats.partial_matches += 1
                else:
                    stats.no_matches += 1
            
            results = validated_results
            
            self.logger.info(
                f"Results for '{search_name}': "
                f"{stats.total_results_found} total, "
                f"{stats.exact_matches} exact, "
                f"{stats.partial_matches} partial, "
                f"{stats.no_matches} no match"
            )
            
        except Exception as e:
            stats.error_occurred = True
            stats.error_message = str(e)
            self.logger.error(f"Error extracting results for '{search_name}': {str(e)}")
        
        finally:
            stats.search_time = asyncio.get_event_loop().time() - start_time
        
        return stats, results
    
    async def _check_no_results(self) -> bool:
        """Check if page indicates no results."""
        try:
            for indicator in self.selectors['no_results_indicators']:
                try:
                    element = self.page.locator(indicator).first
                    if await element.is_visible(timeout=2000):
                        self.logger.debug(f"Found no results indicator: {indicator}")
                        return True
                except:
                    continue
            return False
        except Exception:
            return False
    
    async def _extract_all_results(self) -> List[Dict[str, Any]]:
        """Extract all results from the page."""
        results = []
        
        try:
            # Try table-based extraction first (most common for ReadySearch)
            table_results = await self._extract_from_tables()
            if table_results:
                results.extend(table_results)
            
            # If no table results, try div-based extraction
            if not results:
                div_results = await self._extract_from_divs()
                results.extend(div_results)
            
            self.logger.debug(f"Extracted {len(results)} raw results")
            
        except Exception as e:
            self.logger.error(f"Error extracting results: {str(e)}")
        
        return results
    
    async def _extract_from_tables(self) -> List[Dict[str, Any]]:
        """Extract results from table format."""
        results = []
        
        try:
            # Find all tables on the page
            tables = self.page.locator('table')
            table_count = await tables.count()
            
            for i in range(table_count):
                table = tables.nth(i)
                
                # Skip tables that are clearly not results (like navigation)
                table_text = await table.inner_text()
                if len(table_text.strip()) < 10:  # Skip tiny tables
                    continue
                
                # Get all rows
                rows = table.locator('tr')
                row_count = await rows.count()
                
                # Skip header row(s) - assume first row is header if more than 1 row
                start_row = 1 if row_count > 1 else 0
                
                for j in range(start_row, row_count):
                    row = rows.nth(j)
                    
                    try:
                        result = await self._extract_from_row(row)
                        if result and result.get('name'):
                            results.append(result)
                    except Exception as e:
                        self.logger.debug(f"Error extracting from row {j}: {str(e)}")
                        continue
            
        except Exception as e:
            self.logger.debug(f"Table extraction error: {str(e)}")
        
        return results
    
    async def _extract_from_row(self, row) -> Optional[Dict[str, Any]]:
        """Extract person data from a table row."""
        try:
            cells = row.locator('td')
            cell_count = await cells.count()
            
            if cell_count == 0:
                return None
            
            result = {'cells': []}
            
            # Extract all cell contents
            for i in range(cell_count):
                cell_text = await cells.nth(i).inner_text()
                result['cells'].append(cell_text.strip())
            
            # The first cell usually contains the name
            if result['cells']:
                result['name'] = result['cells'][0]
                
                # Additional info from other cells
                if len(result['cells']) > 1:
                    result['location'] = result['cells'][1] if len(result['cells']) > 1 else ""
                    result['additional_info'] = " | ".join(result['cells'][2:]) if len(result['cells']) > 2 else ""
            
            return result if result.get('name') else None
            
        except Exception as e:
            self.logger.debug(f"Row extraction error: {str(e)}")
            return None
    
    async def _extract_from_divs(self) -> List[Dict[str, Any]]:
        """Extract results from div-based layout."""
        results = []
        
        try:
            # Look for result containers
            container_selectors = [
                '[class*="result"]',
                '[class*="person"]',
                '[class*="search"]'
            ]
            
            for selector in container_selectors:
                containers = self.page.locator(selector)
                count = await containers.count()
                
                for i in range(count):
                    container = containers.nth(i)
                    
                    try:
                        result = await self._extract_from_container(container)
                        if result and result.get('name'):
                            results.append(result)
                    except Exception as e:
                        self.logger.debug(f"Container extraction error: {str(e)}")
                        continue
                
                if results:  # Found results with this selector
                    break
            
        except Exception as e:
            self.logger.debug(f"Div extraction error: {str(e)}")
        
        return results
    
    async def _extract_from_container(self, container) -> Optional[Dict[str, Any]]:
        """Extract person data from a div container."""
        try:
            # Get all text from container
            all_text = await container.inner_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            if not lines:
                return None
            
            # Assume first line is name
            name = lines[0]
            
            # Try to find additional info
            location = ""
            additional_info = ""
            
            if len(lines) > 1:
                # Look for location patterns
                for line in lines[1:]:
                    if any(keyword in line.lower() for keyword in ['street', 'road', 'avenue', 'drive', 'nsw', 'vic', 'qld', 'sa', 'wa', 'nt', 'act', 'tas']):
                        location = line
                        break
                
                # Remaining lines as additional info
                additional_info = " | ".join(lines[1:])
            
            return {
                'name': name,
                'location': location,
                'additional_info': additional_info
            }
            
        except Exception as e:
            self.logger.debug(f"Container extraction error: {str(e)}")
            return None
    
    def _create_person_result(self, raw_result: Dict[str, Any]) -> PersonResult:
        """Create a PersonResult from raw extracted data."""
        return PersonResult(
            name=raw_result.get('name', ''),
            location=raw_result.get('location', ''),
            additional_info=raw_result.get('additional_info', ''),
            raw_data=raw_result
        )
    
    def _validate_match(self, search_name: str, result_name: str) -> Tuple[str, float]:
        """
        Validate if result name matches search name.
        
        Args:
            search_name: The name that was searched for
            result_name: The name found in results
            
        Returns:
            Tuple of (match_type, confidence_score)
        """
        if not search_name or not result_name:
            return "none", 0.0
        
        # Normalize both names
        normalized_search = self._normalize_for_matching(search_name)
        normalized_result = self._normalize_for_matching(result_name)
        
        # Exact match check
        if normalized_search == normalized_result:
            return "exact", 1.0
        
        # Check if all search words are present in result
        search_words = set(normalized_search.split())
        result_words = set(normalized_result.split())
        
        if search_words.issubset(result_words):
            # All search words found in result
            confidence = len(search_words) / len(result_words)
            return "exact", confidence
        
        # Check partial match
        matching_words = search_words.intersection(result_words)
        if matching_words:
            confidence = len(matching_words) / len(search_words)
            if confidence >= 0.7:  # At least 70% of words match
                return "partial", confidence
        
        return "none", 0.0
    
    def _normalize_for_matching(self, name: str) -> str:
        """Normalize name for matching purposes."""
        if not name:
            return ""
        
        # Convert to lowercase and normalize whitespace
        normalized = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove common prefixes and suffixes
        titles = ['mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        words = normalized.split()
        filtered_words = []
        
        for word in words:
            clean_word = word.strip('.,')
            if clean_word not in titles + suffixes:
                filtered_words.append(clean_word)
        
        return ' '.join(filtered_words)


class EnhancedNameMatcher:
    """Enhanced name matching with proper validation."""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
    
    def find_exact_matches(self, search_name: str, results: List[PersonResult]) -> Tuple[bool, List[PersonResult]]:
        """
        Find exact matches for a search name.
        
        Args:
            search_name: The name being searched for
            results: List of PersonResult objects
            
        Returns:
            Tuple of (match_found, list_of_exact_matches)
        """
        if not search_name or not results:
            return False, []
        
        exact_matches = []
        
        for result in results:
            if result.match_type == "exact" and result.confidence_score >= 0.8:
                exact_matches.append(result)
        
        self.logger.info(f"Found {len(exact_matches)} exact matches for '{search_name}'")
        return len(exact_matches) > 0, exact_matches
