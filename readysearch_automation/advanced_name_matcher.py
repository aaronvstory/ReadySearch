"""
Advanced Name Matching System for ReadySearch
Handles sophisticated matching with detailed reasoning and explanations.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MatchType(Enum):
    """Enhanced match types with detailed categorization."""
    EXACT = "exact"                           # Perfect match
    PARTIAL_MIDDLE = "partial_middle"         # Same core name + middle name(s)
    PARTIAL_VARIATION = "partial_variation"   # Name variations (John→Jonathan)
    PARTIAL_SUBSTRING = "partial_substring"   # Substring matches
    PARTIAL_WORD = "partial_word"            # Word-level partial matches
    NOT_MATCHED = "not_matched"              # No meaningful match

@dataclass
class MatchResult:
    """Detailed match result with reasoning and explanation."""
    match_type: MatchType
    confidence: float
    is_match: bool  # True for exact and all partial types, False for not_matched
    reasoning: str  # Human-readable explanation
    details: Dict[str, Any]  # Technical details for debugging
    
    def get_display_category(self) -> str:
        """Get user-friendly display category."""
        if self.match_type == MatchType.EXACT:
            return "EXACT MATCH"
        elif self.is_match:
            return "PARTIAL MATCH"
        else:
            return "NOT MATCHED"

class AdvancedNameMatcher:
    """
    Advanced name matching system with sophisticated logic and detailed explanations.
    
    Handles the specific requirements:
    1. "JOHN SMITH" vs "JOHN MICHAEL SMITH" → MATCHED (middle name)
    2. "JOHN SMITH" vs "JONATHAN SMITH" → MATCHED (name variation)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common titles and suffixes to filter out
        self.titles = {'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'lady'}
        self.suffixes = {'jr', 'sr', 'ii', 'iii', 'iv', 'v'}
        
        # Common name variations and nicknames
        self.name_variations = {
            # Full name → shorter variations
            'jonathan': ['john', 'jon', 'johnny'],
            'michael': ['mike', 'mick', 'mickey'],
            'william': ['will', 'bill', 'billy', 'liam'],
            'robert': ['rob', 'bob', 'bobby', 'robbie'],
            'richard': ['rick', 'dick', 'richie'],
            'elizabeth': ['liz', 'beth', 'betty', 'eliza'],
            'jennifer': ['jen', 'jenny', 'jenn'],
            'christopher': ['chris', 'kit'],
            'matthew': ['matt', 'matty'],
            'anthony': ['tony', 'ant'],
            'benjamin': ['ben', 'benny'],
            'alexander': ['alex', 'al', 'sandy'],
            'nicholas': ['nick', 'nicky'],
            'catherine': ['kate', 'cathy', 'cat'],
            'margaret': ['mag', 'maggie', 'peggy'],
            'patricia': ['pat', 'patty', 'trish'],
            'stephanie': ['steph', 'steffi'],
            'samantha': ['sam', 'sammy'],
            'amanda': ['mandy', 'amy'],
            'barbara': ['barb', 'bobbie'],
            'deborah': ['deb', 'debbie'],
            'rebecca': ['becca', 'becky'],
            'jacqueline': ['jackie', 'jack'],
            'kimberly': ['kim', 'kimmy'],
            'michelle': ['shelly', 'mitch'],
            'lawrence': ['larry', 'lance'],
            'charles': ['charlie', 'chuck', 'char'],
            'thomas': ['tom', 'tommy', 'thom'],
            'andrew': ['andy', 'drew'],
            'joshua': ['josh'],
            'daniel': ['dan', 'danny'],
            'david': ['dave', 'davey'],
            'james': ['jim', 'jimmy', 'jamie'],
            'joseph': ['joe', 'joey'],
            'edward': ['ed', 'eddie', 'ted'],
            'donald': ['don', 'donny'],
            'kenneth': ['ken', 'kenny'],
            'paul': ['paulie'],
            'mark': ['marky'],
            'steven': ['steve', 'stevie'],
            'kevin': ['kev'],
            'brian': ['bri'],
            'george': ['geo', 'georgie'],
            'harold': ['harry', 'hal'],
            'ronald': ['ron', 'ronny'],
            'timothy': ['tim', 'timmy'],
            'jason': ['jase'],
            'jeffrey': ['jeff', 'jeffery'],
            'ryan': ['ry'],
            'jacob': ['jake', 'coby'],
            'gary': ['gar'],
            'frank': ['frankie'],
            'scott': ['scotty'],
            'eric': ['rick'],
            'gregory': ['greg', 'gregg'],
            'raymond': ['ray'],
            'samuel': ['sam', 'sammy'],
            'patrick': ['pat', 'paddy'],
            'alexander': ['alex', 'xander'],
            'jack': ['jackie'],
            'dennis': ['denny'],
            'jerry': ['gerald'],
            'tyler': ['ty'],
            'aaron': ['ron'],
            'jose': ['joey'],
            'henry': ['hank', 'harry'],
            'adam': ['ad'],
            'douglas': ['doug', 'dougie'],
            'nathan': ['nate', 'natty'],
            'peter': ['pete', 'petey'],
            'zachary': ['zach', 'zack'],
            'kyle': ['ky'],
            'noah': ['no'],
            'alan': ['al'],
            'ralph': ['ralphie'],
            'wayne': ['way'],
            'arthur': ['art', 'artie'],
            'lawrence': ['larry'],
            'sean': ['shawn'],
            'christian': ['chris'],
            'roger': ['rog'],
            'louis': ['lou', 'louie'],
            'walter': ['walt', 'wally'],
            'carl': ['charlie'],
            'harold': ['hal'],
            'willie': ['will'],
            'jordan': ['jordy'],
            'jesse': ['jess'],
            'bryan': ['bry'],
            'lawrence': ['lars'],
            'arthur': ['archie'],
            'eugene': ['gene'],
            'wayne': ['dwayne'],
            'ralph': ['rafe'],
            'bobby': ['robert'],
            'russell': ['russ', 'rusty'],
            'louis': ['lewis'],
            'phillip': ['phil', 'flip'],
            'johnny': ['john']
        }
        
        # Build reverse mapping (nickname → full name)
        self.nickname_to_full = {}
        for full_name, nicknames in self.name_variations.items():
            for nickname in nicknames:
                if nickname not in self.nickname_to_full:
                    self.nickname_to_full[nickname] = []
                self.nickname_to_full[nickname].append(full_name)
        
        # Common suffixes that should be ignored for core matching
        self.suffixes = {
            'jr', 'sr', 'ii', 'iii', 'iv', 'v', 'vi',
            'esq', 'phd', 'md', 'dds', 'jd', 'cpa'
        }
        
        # Common titles to remove
        self.titles = {
            'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'professor',
            'sir', 'lady', 'lord', 'rev', 'reverend', 'father', 'sister'
        }

    def match_names(self, search_name: str, result_name: str) -> MatchResult:
        """
        Advanced name matching with detailed reasoning.
        
        Args:
            search_name: The name being searched for (e.g., "John Smith")
            result_name: The name found in results (e.g., "JOHN MICHAEL SMITH")
            
        Returns:
            MatchResult with detailed match information and reasoning
        """
        if not search_name or not result_name:
            return MatchResult(
                match_type=MatchType.NOT_MATCHED,
                confidence=0.0,
                is_match=False,
                reasoning="Empty name provided",
                details={"search_name": search_name, "result_name": result_name}
            )
        
        # Normalize names for comparison
        norm_search = self._normalize_name(search_name)
        norm_result = self._normalize_name(result_name)
        
        search_words = norm_search.split()
        result_words = norm_result.split()
        
        self.logger.debug(f"Matching '{search_name}' vs '{result_name}'")
        self.logger.debug(f"Normalized: '{norm_search}' vs '{norm_result}'")
        
        # 1. Check for exact match
        if norm_search == norm_result:
            return MatchResult(
                match_type=MatchType.EXACT,
                confidence=1.0,
                is_match=True,
                reasoning=f"Perfect exact match: '{search_name}' = '{result_name}'",
                details={
                    "search_normalized": norm_search,
                    "result_normalized": norm_result,
                    "match_type": "exact_identical"
                }
            )
        
        # 2. Check for exact match with suffixes
        exact_with_suffix = self._check_exact_with_suffix(search_words, result_words)
        if exact_with_suffix:
            return MatchResult(
                match_type=MatchType.EXACT,
                confidence=1.0,
                is_match=True,
                reasoning=f"Exact match with suffix: '{search_name}' matches '{result_name}' (suffix: {exact_with_suffix['suffix']})",
                details=exact_with_suffix
            )
        
        # 3. Check for middle name additions (JOHN SMITH → JOHN MICHAEL SMITH)
        middle_name_match = self._check_middle_name_match(search_words, result_words)
        if middle_name_match:
            return MatchResult(
                match_type=MatchType.PARTIAL_MIDDLE,
                confidence=0.95,
                is_match=True,
                reasoning=f"Core name match with additional middle name(s): '{search_name}' found in '{result_name}' (added: {', '.join(middle_name_match['added_names'])})",
                details=middle_name_match
            )
        
        # 4. Check for name variations (JOHN → JONATHAN)
        variation_match = self._check_name_variations(search_words, result_words)
        if variation_match:
            return MatchResult(
                match_type=MatchType.PARTIAL_VARIATION,
                confidence=variation_match['confidence'],
                is_match=True,
                reasoning=f"Name variation match: {variation_match['explanation']}",
                details=variation_match
            )
        
        # 5. Check for substring matches with context
        substring_match = self._check_intelligent_substring(search_words, result_words)
        if substring_match:
            return MatchResult(
                match_type=MatchType.PARTIAL_SUBSTRING,
                confidence=substring_match['confidence'],
                is_match=True,
                reasoning=f"Substring match: {substring_match['explanation']}",
                details=substring_match
            )
        
        # 6. Check for word-level partial matches
        word_match = self._check_word_level_match(search_words, result_words)
        if word_match:
            return MatchResult(
                match_type=MatchType.PARTIAL_WORD,
                confidence=word_match['confidence'],
                is_match=word_match['confidence'] >= 0.6,  # Only consider match if confidence is high enough
                reasoning=f"Partial word match: {word_match['explanation']}",
                details=word_match
            )
        
        # 7. No meaningful match found
        return MatchResult(
            match_type=MatchType.NOT_MATCHED,
            confidence=0.0,
            is_match=False,
            reasoning=f"No meaningful match found between '{search_name}' and '{result_name}'",
            details={
                "search_words": search_words,
                "result_words": result_words,
                "checked_methods": ["exact", "suffix", "middle_name", "variations", "substring", "word_partial"]
            }
        )

    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ""
        
        # Convert to lowercase and normalize whitespace
        normalized = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Split into words and filter out titles and suffixes
        words = normalized.split()
        filtered_words = []
        
        for word in words:
            if word not in self.titles and word not in self.suffixes:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)

    def _check_exact_with_suffix(self, search_words: List[str], result_words: List[str]) -> Optional[Dict[str, Any]]:
        """Check if result is exact match with additional suffix."""
        if len(result_words) <= len(search_words):
            return None
        
        # Check if search words match exactly at the beginning
        if search_words == result_words[:len(search_words)]:
            additional_words = result_words[len(search_words):]
            
            # Check if all additional words are suffixes
            if all(word in self.suffixes for word in additional_words):
                return {
                    "match_type": "exact_with_suffix",
                    "suffix": " ".join(additional_words),
                    "core_match": " ".join(search_words),
                    "additional_words": additional_words
                }
        
        return None

    def match_names_strict(self, search_name: str, result_name: str, exact_first_name: bool = False) -> MatchResult:
        """
        Strict name matching with user-specified criteria:
        
        EXACT RECORD MATCH CRITERIA:
        - Last Name - Exact Match only
        - First Name - Exact Match only  
        - Middle Name (if present) - Exact Match only
        - Year of Birth - Exact Match only
        
        PARTIAL RECORD MATCH CRITERIA:
        - Last Name - Exact Match only (if last name is off by 1 letter, it's NO MATCH)
        - First Name - Partial Match (if exact_first_name=False)
        - Middle Name - Any (including non-match)
        - Year of Birth - Partial Match
        
        Args:
            search_name: The name being searched for
            result_name: The name found in results
            exact_first_name: If True, requires exact first name match (stricter)
            
        Returns:
            MatchResult with strict matching rules applied
        """
        if not search_name or not result_name:
            return MatchResult(
                match_type=MatchType.NOT_MATCHED,
                confidence=0.0,
                is_match=False,
                reasoning="Empty name provided",
                details={"search_name": search_name, "result_name": result_name}
            )
        
        # Normalize names for comparison
        norm_search = self._normalize_name(search_name)
        norm_result = self._normalize_name(result_name)
        
        search_words = norm_search.split()
        result_words = norm_result.split()
        
        if len(search_words) < 1 or len(result_words) < 1:
            return MatchResult(
                match_type=MatchType.NOT_MATCHED,
                confidence=0.0,
                is_match=False,
                reasoning="Invalid name format",
                details={"search_words": search_words, "result_words": result_words}
            )
        
        self.logger.debug(f"Strict matching '{search_name}' vs '{result_name}' (exact_first_name={exact_first_name})")
        
        # Extract first and last names
        search_first = search_words[0]
        search_last = search_words[-1] if len(search_words) > 1 else search_words[0]
        search_middle = search_words[1:-1] if len(search_words) > 2 else []
        
        result_first = result_words[0]
        result_last = result_words[-1] if len(result_words) > 1 else result_words[0]
        result_middle = result_words[1:-1] if len(result_words) > 2 else []
        
        # CRITICAL: Last name must ALWAYS match exactly
        if search_last != result_last:
            return MatchResult(
                match_type=MatchType.NOT_MATCHED,
                confidence=0.0,
                is_match=False,
                reasoning=f"Last name mismatch: '{search_last}' != '{result_last}' (strict criteria: last name must be exact)",
                details={
                    "search_last": search_last,
                    "result_last": result_last,
                    "rule_violated": "last_name_exact_required"
                }
            )
        
        # Check first name matching
        first_name_exact_match = (search_first == result_first)
        first_name_variation_match = False
        
        if not first_name_exact_match and not exact_first_name:
            # Check for name variations (John -> Jonathan, etc.)
            first_name_variation_match = self._check_name_variation(search_first, result_first)
        
        # Check middle name matching
        middle_names_match = True
        middle_match_type = "exact"
        
        if search_middle and result_middle:
            # If search has middle names, they must all be present in result
            if not all(m in result_middle for m in search_middle):
                middle_names_match = False
                middle_match_type = "mismatch"
        elif search_middle and not result_middle:
            # Search has middle names but result doesn't
            middle_names_match = False
            middle_match_type = "missing_in_result"
        elif not search_middle and result_middle:
            # Result has additional middle names - this is okay for partial matches
            middle_match_type = "additional_in_result"
        
        # Determine match result based on strict criteria
        if first_name_exact_match and middle_names_match and middle_match_type == "exact":
            # EXACT MATCH: all components match exactly
            return MatchResult(
                match_type=MatchType.EXACT,
                confidence=1.0,
                is_match=True,
                reasoning=f"Exact match: all name components match exactly",
                details={
                    "search_parts": {"first": search_first, "middle": search_middle, "last": search_last},
                    "result_parts": {"first": result_first, "middle": result_middle, "last": result_last},
                    "match_quality": "exact_all_components"
                }
            )
        elif first_name_exact_match and middle_match_type in ["additional_in_result", "exact"]:
            # EXACT MATCH: first and last exact, result has additional middle names
            return MatchResult(
                match_type=MatchType.EXACT,
                confidence=0.98,
                is_match=True,
                reasoning=f"Exact match with additional middle names in result",
                details={
                    "search_parts": {"first": search_first, "middle": search_middle, "last": search_last},
                    "result_parts": {"first": result_first, "middle": result_middle, "last": result_last},
                    "match_quality": "exact_with_additional_middle"
                }
            )
        elif first_name_variation_match and not exact_first_name:
            # PARTIAL MATCH: first name variation allowed, last name exact
            return MatchResult(
                match_type=MatchType.PARTIAL_VARIATION,
                confidence=0.85,
                is_match=True,
                reasoning=f"Partial match: first name variation '{search_first}' -> '{result_first}', last name exact",
                details={
                    "search_parts": {"first": search_first, "middle": search_middle, "last": search_last},
                    "result_parts": {"first": result_first, "middle": result_middle, "last": result_last},
                    "match_quality": "partial_first_name_variation",
                    "first_name_variation": True
                }
            )
        else:
            # NO MATCH: criteria not met
            reasons = []
            if not first_name_exact_match and exact_first_name:
                reasons.append(f"first name exact required but '{search_first}' != '{result_first}'")
            elif not first_name_exact_match and not first_name_variation_match:
                reasons.append(f"first name '{search_first}' has no valid variation to '{result_first}'")
            if not middle_names_match:
                reasons.append(f"middle name mismatch: {middle_match_type}")
            
            return MatchResult(
                match_type=MatchType.NOT_MATCHED,
                confidence=0.0,
                is_match=False,
                reasoning=f"No match: {'; '.join(reasons)}",
                details={
                    "search_parts": {"first": search_first, "middle": search_middle, "last": search_last},
                    "result_parts": {"first": result_first, "middle": result_middle, "last": result_last},
                    "failed_criteria": reasons,
                    "exact_first_name_required": exact_first_name
                }
            )
    
    def _check_name_variation(self, search_name: str, result_name: str) -> bool:
        """
        Check if result_name is a valid variation of search_name.
        
        Args:
            search_name: The name being searched for
            result_name: The name found in results
            
        Returns:
            True if result_name is a valid variation of search_name
        """
        search_lower = search_name.lower()
        result_lower = result_name.lower()
        
        # Check direct variations
        if search_lower in self.name_variations:
            if result_lower in self.name_variations[search_lower]:
                return True
        
        # Check reverse variations (Jonathan -> John)
        for full_name, variations in self.name_variations.items():
            if search_lower in variations and result_lower == full_name:
                return True
            if result_lower in variations and search_lower == full_name:
                return True
        
        return False

    def _check_middle_name_match(self, search_words: List[str], result_words: List[str]) -> Optional[Dict[str, Any]]:
        """
        Check if result contains search name with additional middle names.
        e.g., "john smith" vs "john michael smith"
        """
        if len(result_words) <= len(search_words):
            return None
        
        # For middle name detection, we need at least first and last name
        if len(search_words) < 2:
            return None
        
        # Check if first and last names match exactly
        search_first = search_words[0]
        search_last = search_words[-1]
        
        result_first = result_words[0]
        result_last = result_words[-1]
        
        # First and last names must match exactly
        if search_first == result_first and search_last == result_last:
            # Check if middle part of search matches part of result middle
            search_middle = search_words[1:-1] if len(search_words) > 2 else []
            result_middle = result_words[1:-1] if len(result_words) > 2 else []
            
            # If search has no middle names, any result middle names are additions
            if not search_middle:
                return {
                    "match_type": "middle_name_addition",
                    "first_name": search_first,
                    "last_name": search_last,
                    "added_names": result_middle,
                    "confidence": 0.95
                }
            
            # If search has middle names, check if they're all present in result
            if all(m in result_middle for m in search_middle):
                additional_middle = [m for m in result_middle if m not in search_middle]
                return {
                    "match_type": "middle_name_addition",
                    "first_name": search_first,
                    "last_name": search_last,
                    "original_middle": search_middle,
                    "added_names": additional_middle,
                    "confidence": 0.95
                }
        
        return None

    def _check_name_variations(self, search_words: List[str], result_words: List[str]) -> Optional[Dict[str, Any]]:
        """
        Check for name variations (john → jonathan, mike → michael).
        """
        if len(search_words) != len(result_words):
            # For variations, we might have different word counts due to middle names
            # Let's check first and last name variations
            pass
        
        variations_found = []
        matched_positions = []
        
        for i, search_word in enumerate(search_words):
            best_match = None
            best_confidence = 0
            
            for j, result_word in enumerate(result_words):
                # Skip if already matched
                if j in matched_positions:
                    continue
                
                # Check direct variation
                variation_confidence = self._get_variation_confidence(search_word, result_word)
                if variation_confidence > best_confidence:
                    best_match = (j, result_word, variation_confidence)
                    best_confidence = variation_confidence
            
            if best_match and best_confidence >= 0.7:  # High confidence threshold for variations
                matched_positions.append(best_match[0])
                variations_found.append({
                    "search_word": search_word,
                    "result_word": best_match[1],
                    "confidence": best_match[2],
                    "variation_type": self._get_variation_type(search_word, best_match[1])
                })
        
        if variations_found:
            # Calculate overall confidence
            total_confidence = sum(v['confidence'] for v in variations_found) / len(search_words)
            
            if total_confidence >= 0.7:
                explanation_parts = []
                for var in variations_found:
                    explanation_parts.append(f"'{var['search_word']}' → '{var['result_word']}' ({var['variation_type']})")
                
                return {
                    "match_type": "name_variations",
                    "variations": variations_found,
                    "confidence": total_confidence,
                    "explanation": "; ".join(explanation_parts)
                }
        
        return None

    def _get_variation_confidence(self, search_word: str, result_word: str) -> float:
        """Get confidence score for name variation."""
        # Exact match
        if search_word == result_word:
            return 1.0
        
        # Check known variations
        if search_word in self.name_variations:
            if result_word in self.name_variations[search_word]:
                return 0.9  # Known nickname
        
        if result_word in self.name_variations:
            if search_word in self.name_variations[result_word]:
                return 0.9  # Known full name
        
        # Check reverse mapping
        if search_word in self.nickname_to_full:
            if result_word in self.nickname_to_full[search_word]:
                return 0.9
        
        if result_word in self.nickname_to_full:
            if search_word in self.nickname_to_full[result_word]:
                return 0.9
        
        # Check substring relationships
        if len(search_word) >= 3 and len(result_word) >= 3:
            if search_word in result_word:
                return 0.8  # search is substring of result
            if result_word in search_word:
                return 0.8  # result is substring of search
        
        # Check common prefixes (for names like Jon/John, Mike/Michael)
        if len(search_word) >= 3 and len(result_word) >= 3:
            common_prefix = 0
            for i in range(min(len(search_word), len(result_word))):
                if search_word[i] == result_word[i]:
                    common_prefix += 1
                else:
                    break
            
            if common_prefix >= 3:  # At least 3 character prefix match
                return 0.7
        
        return 0.0

    def _get_variation_type(self, search_word: str, result_word: str) -> str:
        """Determine the type of name variation."""
        if search_word in self.name_variations and result_word in self.name_variations[search_word]:
            return "known nickname"
        elif result_word in self.name_variations and search_word in self.name_variations[result_word]:
            return "known full name"
        elif search_word in result_word:
            return "substring extension"
        elif result_word in search_word:
            return "substring contraction"
        else:
            return "phonetic variation"

    def _check_intelligent_substring(self, search_words: List[str], result_words: List[str]) -> Optional[Dict[str, Any]]:
        """Check for intelligent substring matches with context."""
        substring_matches = []
        
        for search_word in search_words:
            for result_word in result_words:
                if len(search_word) >= 3 and len(result_word) >= 3:
                    if search_word in result_word or result_word in search_word:
                        confidence = min(len(search_word), len(result_word)) / max(len(search_word), len(result_word))
                        substring_matches.append({
                            "search_word": search_word,
                            "result_word": result_word,
                            "confidence": confidence,
                            "type": "substring"
                        })
        
        if substring_matches:
            avg_confidence = sum(m['confidence'] for m in substring_matches) / len(substring_matches)
            
            if avg_confidence >= 0.6:
                explanation_parts = [f"'{m['search_word']}' in '{m['result_word']}'" for m in substring_matches]
                
                return {
                    "match_type": "intelligent_substring",
                    "matches": substring_matches,
                    "confidence": avg_confidence,
                    "explanation": "; ".join(explanation_parts)
                }
        
        return None

    def _check_word_level_match(self, search_words: List[str], result_words: List[str]) -> Optional[Dict[str, Any]]:
        """Check for word-level partial matches."""
        exact_word_matches = []
        
        for search_word in search_words:
            if search_word in result_words:
                exact_word_matches.append(search_word)
        
        if exact_word_matches:
            confidence = len(exact_word_matches) / len(search_words)
            
            return {
                "match_type": "word_level_partial",
                "matched_words": exact_word_matches,
                "total_search_words": len(search_words),
                "confidence": confidence,
                "explanation": f"{len(exact_word_matches)}/{len(search_words)} words match exactly: {', '.join(exact_word_matches)}"
            }
        
        return None