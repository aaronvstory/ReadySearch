"""
Test script to verify the fixed exact matching logic.
This tests the specific Anthony Bek case that was failing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'readysearch_automation'))

from enhanced_result_parser import EnhancedResultParser, PersonResult, EnhancedNameMatcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_anthony_bek_exact_matching():
    """Test the Anthony Bek case with the exact results provided by the user."""
    
    print("=" * 80)
    print("🧪 TESTING FIXED EXACT MATCHING LOGIC - ANTHONY BEK CASE")
    print("=" * 80)
    
    # The actual search results from the user's feedback
    search_name = "Anthony Bek"
    
    # Create mock results based on user's exact data
    mock_results = [
        # These should be EXACT matches (3 total)
        {"name": "ANTHONY BEK", "date_of_birth": "02/11/1993", "location": "SYDNEY NSW"},
        {"name": "ANTHONY BEK", "date_of_birth": "UNKNOWN", "location": ""},
        {"name": "ANTHONY BEK", "date_of_birth": "02/11/1993", "location": "CANTERBURY NSW"},
        
        # These should NOT be exact matches (partial or none)
        {"name": "ANTHONY BAKHOS", "date_of_birth": "14/06/1993", "location": "CAMPSIE NSW"},
        {"name": "ANTHONY CHARLES BAKHOS", "date_of_birth": "17/03/1994", "location": "AUBURN NSW"},
        {"name": "ANTHONY BOUCHAIA", "date_of_birth": "04/05/1992", "location": "CAMPSIE NSW"},
        {"name": "ANTHONY BAKHOS GEORGES", "date_of_birth": "29/04/1992", "location": "DARLINGHURST NSW"},
        {"name": "ANTHONY BAKHOS GEORGES", "date_of_birth": "29/04/1992", "location": "SYDNEY NSW"},
        {"name": "ANTHONY BOUCHAIA", "date_of_birth": "04/05/1992", "location": "CANTERBURY NSW"},
        {"name": "ANTHONY BAKHOS", "date_of_birth": "10/12/1993", "location": "SYDNEY NSW"},
        {"name": "ANTHONY BOUCHAIA", "date_of_birth": "04/05/1992", "location": "SYDNEY NSW"},
        {"name": "JOHANN ANTON JULES BACH", "date_of_birth": "19/09/1992", "location": "MULHOUSE ALSACE FRANCE"},
        {"name": "LIAM ANTHONY BOUKAS", "date_of_birth": "03/07/1992", "location": "BAULKHAM HILLS NSW"},
    ]
    
    # Create a mock parser instance (we don't need a real page for this test)
    class MockParser(EnhancedResultParser):
        def __init__(self):
            self.logger = logging.getLogger(__name__)
    
    parser = MockParser()
    
    # Convert mock results to PersonResult objects and validate matches
    person_results = []
    for mock_result in mock_results:
        person = PersonResult(
            name=mock_result["name"],
            date_of_birth=mock_result["date_of_birth"],
            location=mock_result["location"]
        )
        
        # Apply the fixed validation logic
        match_type, confidence = parser._validate_match(search_name, person.name)
        person.match_type = match_type
        person.confidence_score = confidence
        
        person_results.append(person)
    
    # Test with EnhancedNameMatcher
    matcher = EnhancedNameMatcher(strict_mode=True)
    match_found, exact_matches = matcher.find_exact_matches(search_name, person_results)
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   Search Name: '{search_name}'")
    print(f"   Total Results Found: {len(person_results)}")
    print(f"   Exact Matches Found: {len(exact_matches)}")
    print(f"   Expected Exact Matches: 3")
    
    print(f"\n🔍 DETAILED ANALYSIS:")
    
    exact_count = 0
    partial_count = 0
    none_count = 0
    
    for i, person in enumerate(person_results, 1):
        status_emoji = "✅" if person.match_type == "exact" else "❌" if person.match_type == "partial" else "⭕"
        print(f"   {i:2d}. {status_emoji} {person.name}")
        print(f"       Match Type: {person.match_type.upper()}")
        print(f"       Confidence: {person.confidence_score:.2f}")
        print(f"       DOB: {person.date_of_birth}")
        print(f"       Location: {person.location}")
        
        if person.match_type == "exact":
            exact_count += 1
        elif person.match_type == "partial":
            partial_count += 1
        else:
            none_count += 1
        print()
    
    print(f"📈 MATCH TYPE BREAKDOWN:")
    print(f"   Exact Matches: {exact_count}")
    print(f"   Partial Matches: {partial_count}")
    print(f"   No Matches: {none_count}")
    
    # Validation
    print(f"\n🎯 VALIDATION:")
    if exact_count == 3:
        print(f"   ✅ SUCCESS: Found exactly 3 exact matches as expected!")
        print(f"   ✅ Fixed exact matching logic is working correctly")
        return True
    else:
        print(f"   ❌ FAILURE: Expected 3 exact matches, but found {exact_count}")
        print(f"   ❌ Exact matching logic still needs fixing")
        return False

def test_edge_cases():
    """Test additional edge cases for exact matching."""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING EDGE CASES")
    print("=" * 80)
    
    class MockParser(EnhancedResultParser):
        def __init__(self):
            self.logger = logging.getLogger(__name__)
    
    parser = MockParser()
    
    test_cases = [
        # (search_name, result_name, expected_match_type, description)
        ("John Smith", "JOHN SMITH", "exact", "Basic exact match"),
        ("John Smith", "JOHN SMITH JR", "exact", "Exact match with suffix"),
        ("John Smith", "JOHN MICHAEL SMITH", "none", "Additional middle name - not exact"),
        ("John Smith", "JOHN SMYTH", "none", "Similar but different surname"),
        ("John Smith", "JONATHAN SMITH", "partial", "Partial first name match"),
        ("Anthony Bek", "ANTHONY BEK", "exact", "The corrected Anthony Bek case"),
        ("Anthony Bek", "ANTHONY BAKHOS", "none", "Similar first name, different surname"),
        ("", "JOHN SMITH", "none", "Empty search name"),
        ("JOHN SMITH", "", "none", "Empty result name"),
    ]
    
    print("\n🔍 EDGE CASE TESTING:")
    all_passed = True
    
    for i, (search_name, result_name, expected_type, description) in enumerate(test_cases, 1):
        match_type, confidence = parser._validate_match(search_name, result_name)
        
        status = "✅" if match_type == expected_type else "❌"
        print(f"   {i:2d}. {status} {description}")
        print(f"       Search: '{search_name}' → Result: '{result_name}'")
        print(f"       Expected: {expected_type} | Got: {match_type} (confidence: {confidence:.2f})")
        
        if match_type != expected_type:
            all_passed = False
        print()
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting comprehensive exact matching tests...\n")
    
    # Test the main Anthony Bek case
    anthony_test_passed = test_anthony_bek_exact_matching()
    
    # Test edge cases
    edge_cases_passed = test_edge_cases()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL RESULTS")
    print("=" * 80)
    
    if anthony_test_passed:
        print("✅ Anthony Bek exact matching test: PASSED")
    else:
        print("❌ Anthony Bek exact matching test: FAILED")
    
    if edge_cases_passed:
        print("✅ Edge cases test: PASSED")
    else:
        print("❌ Edge cases test: FAILED")
    
    if anthony_test_passed and edge_cases_passed:
        print("\n🎉 ALL TESTS PASSED! The exact matching logic is now fixed.")
        print("📋 Ready to run comprehensive speed test with corrected matching.")
    else:
        print("\n⚠️  Some tests failed. The exact matching logic needs further fixes.")