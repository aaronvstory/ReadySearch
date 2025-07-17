"""Name matching and comparison module."""

import re
import logging
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class NameMatcher:
    """Handles exact name matching and comparison logic."""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        
    def find_exact_matches(self, search_name: str, results: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Find exact matches for a search name in results.
        
        Args:
            search_name: The name being searched for
            results: List of search results
            
        Returns:
            Tuple of (match_found, list_of_matches)
        """
        if not search_name or not results:
            return False, []
            
        # Normalize the search name
        normalized_search = self._normalize_for_comparison(search_name)
        
        matches = []
        
        for result in results:
            result_name = result.get('name', '')
            if not result_name:
                continue
                
            # Normalize result name
            normalized_result = self._normalize_for_comparison(result_name)
            
            # Check for exact match
            if self._is_exact_match(normalized_search, normalized_result):
                match_info = {
                    'original_search': search_name,
                    'matched_result': result_name,
                    'normalized_search': normalized_search,
                    'normalized_result': normalized_result,
                    'match_type': 'exact',
                    'confidence': 1.0,
                    'result_data': result
                }
                matches.append(match_info)
                
        match_found = len(matches) > 0
        
        if match_found:
            logger.info(f"Found {len(matches)} exact match(es) for '{search_name}'")
        else:
            logger.info(f"No exact matches found for '{search_name}'")
            
        return match_found, matches
        
    def _normalize_for_comparison(self, name: str) -> str:
        """
        Normalize name for comparison.
        
        Args:
            name: Raw name string
            
        Returns:
            Normalized name string
        """
        if not name:
            return ""
            
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common prefixes and suffixes
        normalized = self._remove_titles_and_suffixes(normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove punctuation except hyphens and apostrophes
        normalized = re.sub(r'[^\w\s\'-]', '', normalized)
        
        # Handle common name variations
        normalized = self._handle_name_variations(normalized)
        
        return normalized
        
    def _remove_titles_and_suffixes(self, name: str) -> str:
        """Remove common titles and suffixes from name."""
        # Common prefixes (titles)
        prefixes = [
            'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'professor',
            'rev', 'reverend', 'father', 'sister', 'brother',
            'sir', 'dame', 'lord', 'lady'
        ]
        
        # Common suffixes
        suffixes = [
            'jr', 'junior', 'sr', 'senior', 'ii', 'iii', 'iv',
            'phd', 'md', 'esq', 'esquire'
        ]
        
        words = name.split()
        
        # Remove prefixes
        while words and words[0].rstrip('.') in prefixes:
            words = words[1:]
            
        # Remove suffixes
        while words and words[-1].rstrip('.') in suffixes:
            words = words[:-1]
            
        return ' '.join(words)
        
    def _handle_name_variations(self, name: str) -> str:
        """Handle common name variations and abbreviations."""
        # Common nickname mappings
        nickname_map = {
            'bill': 'william',
            'bob': 'robert',
            'dick': 'richard',
            'jim': 'james',
            'joe': 'joseph',
            'mike': 'michael',
            'tom': 'thomas',
            'tony': 'anthony',
            'dave': 'david',
            'steve': 'stephen',
            'chris': 'christopher',
            'matt': 'matthew',
            'dan': 'daniel',
            'ben': 'benjamin',
            'sam': 'samuel',
            'alex': 'alexander',
            'nick': 'nicholas',
            'andy': 'andrew',
            'pat': 'patrick',
            'rick': 'richard'
        }
        
        words = name.split()
        normalized_words = []
        
        for word in words:
            # Check if word is a known nickname
            if word in nickname_map:
                normalized_words.append(nickname_map[word])
            else:
                # Check reverse mapping
                reverse_found = False
                for nickname, full_name in nickname_map.items():
                    if word == full_name:
                        # Keep the full name, but note that nickname would also match
                        normalized_words.append(word)
                        reverse_found = True
                        break
                if not reverse_found:
                    normalized_words.append(word)
                    
        return ' '.join(normalized_words)
        
    def _is_exact_match(self, name1: str, name2: str) -> bool:
        """
        Check if two normalized names are an exact match.
        
        Args:
            name1: First normalized name
            name2: Second normalized name
            
        Returns:
            True if names match exactly
        """
        if not name1 or not name2:
            return False
            
        # Direct string comparison
        if name1 == name2:
            return True
            
        # Split into words for more flexible matching
        words1 = name1.split()
        words2 = name2.split()
        
        # Must have same number of words for exact match
        if len(words1) != len(words2):
            return False
            
        # Check if all words match (order matters for exact match)
        for w1, w2 in zip(words1, words2):
            if w1 != w2:
                return False
                
        return True
        
    def get_similarity_score(self, name1: str, name2: str) -> float:
        """
        Get similarity score between two names (0.0 to 1.0).
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score
        """
        if not name1 or not name2:
            return 0.0
            
        # Normalize both names
        norm1 = self._normalize_for_comparison(name1)
        norm2 = self._normalize_for_comparison(name2)
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        return similarity
        
    def find_fuzzy_matches(self, search_name: str, results: List[Dict[str, Any]], 
                          threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find fuzzy matches above a similarity threshold.
        
        Args:
            search_name: The name being searched for
            results: List of search results
            threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of fuzzy matches with similarity scores
        """
        if not search_name or not results:
            return []
            
        fuzzy_matches = []
        
        for result in results:
            result_name = result.get('name', '')
            if not result_name:
                continue
                
            similarity = self.get_similarity_score(search_name, result_name)
            
            if similarity >= threshold:
                match_info = {
                    'original_search': search_name,
                    'matched_result': result_name,
                    'match_type': 'fuzzy',
                    'confidence': similarity,
                    'result_data': result
                }
                fuzzy_matches.append(match_info)
                
        # Sort by confidence (highest first)
        fuzzy_matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"Found {len(fuzzy_matches)} fuzzy matches for '{search_name}' (threshold: {threshold})")
        
        return fuzzy_matches
        
    def analyze_name_components(self, name: str) -> Dict[str, Any]:
        """
        Analyze components of a name for debugging.
        
        Args:
            name: Name to analyze
            
        Returns:
            Dictionary with name analysis
        """
        analysis = {
            'original': name,
            'normalized': self._normalize_for_comparison(name),
            'words': [],
            'word_count': 0,
            'has_titles': False,
            'has_suffixes': False,
            'potential_nicknames': []
        }
        
        if not name:
            return analysis
            
        # Analyze words
        words = name.lower().split()
        analysis['words'] = words
        analysis['word_count'] = len(words)
        
        # Check for titles
        titles = ['mr', 'mrs', 'ms', 'dr', 'prof']
        analysis['has_titles'] = any(word.rstrip('.') in titles for word in words)
        
        # Check for suffixes
        suffixes = ['jr', 'sr', 'ii', 'iii', 'phd', 'md']
        analysis['has_suffixes'] = any(word.rstrip('.') in suffixes for word in words)
        
        # Check for potential nicknames
        nickname_map = {
            'bill': 'william', 'bob': 'robert', 'dick': 'richard',
            'jim': 'james', 'joe': 'joseph', 'mike': 'michael'
        }
        
        for word in words:
            if word in nickname_map:
                analysis['potential_nicknames'].append({
                    'nickname': word,
                    'full_name': nickname_map[word]
                })
                
        return analysis