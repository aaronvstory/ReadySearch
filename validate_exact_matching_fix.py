"""
Validation script to confirm the exact matching logic fix is working correctly.
This tests the core logic without requiring browser automation.
"""

import sys
import os
import time
from typing import List, Tuple

# Add the automation modules to the path
sys.path.append(os.path.dirname(__file__))

from readysearch_automation.enhanced_result_parser import EnhancedResultParser, PersonResult, EnhancedNameMatcher

def test_anthony_bek_validation() -> bool:
    """Test the specific Anthony Bek case that was failing."""
    
    print("🎯 TESTING ANTHONY BEK EXACT MATCHING FIX")
    print("=" * 60)
    
    # Create a mock parser for testing the matching logic
    class MockParser(EnhancedResultParser):
        def __init__(self):
            self.logger = type('Logger', (), {'info': print, 'debug': print, 'error': print})()
    
    parser = MockParser()
    
    # The actual results from the user's feedback
    search_name = "Anthony Bek"
    
    # Test cases: (result_name, expected_match_type)
    test_cases = [
        # Should be EXACT matches
        ("ANTHONY BEK", "exact"),
        ("anthony bek", "exact"),
        ("Anthony Bek", "exact"),
        ("ANTHONY BEK JR", "exact"),  # Suffix should be allowed
        
        # Should NOT be exact matches
        ("ANTHONY BAKHOS", "none"),
        ("ANTHONY CHARLES BAKHOS", "none"),
        ("ANTHONY BOUCHAIA", "none"),
        ("JOHANN ANTON JULES BACH", "none"),
        ("LIAM ANTHONY BOUKAS", "none"),
        ("ANTHONY BEK SMITH", "none"),  # Additional non-suffix should not be exact
        ("ANTHONY", "none"),  # Incomplete name
        ("BEK ANTHONY", "none"),  # Wrong order
    ]
    
    print(f"Search Name: '{search_name}'")
    print(f"Testing {len(test_cases)} cases...\n")
    
    all_passed = True
    exact_matches_found = 0
    
    for i, (result_name, expected_type) in enumerate(test_cases, 1):
        match_type, confidence = parser._validate_match(search_name, result_name)
        
        if match_type == expected_type:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            all_passed = False
        
        if match_type == "exact":
            exact_matches_found += 1
        
        print(f"{i:2d}. {status} | '{result_name}' → {match_type} (confidence: {confidence:.2f})")
        print(f"     Expected: {expected_type} | Got: {match_type}")
        if match_type != expected_type:
            print(f"     ⚠️  MISMATCH!")
        print()
    
    print("📊 SUMMARY:")
    print(f"   Test cases: {len(test_cases)}")
    print(f"   Passed: {sum(1 for i, (_, expected) in enumerate(test_cases) if parser._validate_match(search_name, test_cases[i][0])[0] == expected)}")
    print(f"   Failed: {len(test_cases) - sum(1 for i, (_, expected) in enumerate(test_cases) if parser._validate_match(search_name, test_cases[i][0])[0] == expected)}")
    print(f"   Exact matches found: {exact_matches_found}")
    print(f"   Expected exact matches: 4 (ANTHONY BEK variations)")
    
    print(f"\n🎯 RESULT:")
    if all_passed:
        print("✅ ALL TESTS PASSED - Exact matching logic is working correctly!")
        print("✅ Anthony Bek issue has been resolved")
        return True
    else:
        print("❌ Some tests failed - Exact matching logic needs further fixes")
        return False

def test_performance_characteristics():
    """Test performance characteristics of the matching logic."""
    
    print("\n🚀 TESTING PERFORMANCE CHARACTERISTICS")
    print("=" * 60)
    
    class MockParser(EnhancedResultParser):
        def __init__(self):
            self.logger = type('Logger', (), {'info': lambda x: None, 'debug': lambda x: None, 'error': print})()
    
    parser = MockParser()
    
    # Test with larger datasets
    search_names = ["John Smith", "Mary Johnson", "Anthony Bek", "Sarah Wilson"]
    result_names = [
        "JOHN SMITH", "JOHN SMITH JR", "JOHN SMITHSON", "JOHN MICHAEL SMITH",
        "MARY JOHNSON", "MARY JOHNSON-SMITH", "MARY J JOHNSON", "MARIE JOHNSON",
        "ANTHONY BEK", "ANTHONY BAKHOS", "ANTHONY BOUCHAIA", "ANTHONY BEK SR",
        "SARAH WILSON", "SARAH WILLSON", "SARAH ANN WILSON", "SARA WILSON"
    ]
    
    print(f"Testing performance with {len(search_names)} search names against {len(result_names)} results...")
    
    start_time = time.time()
    total_comparisons = 0
    exact_matches = 0
    
    for search_name in search_names:
        for result_name in result_names:
            match_type, confidence = parser._validate_match(search_name, result_name)
            total_comparisons += 1
            if match_type == "exact":
                exact_matches += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"⏱️  Total time: {total_time:.4f} seconds")
    print(f"🔢 Total comparisons: {total_comparisons}")
    print(f"⚡ Comparisons per second: {total_comparisons/total_time:.0f}")
    print(f"🎯 Exact matches found: {exact_matches}")
    print(f"📊 Average time per comparison: {total_time/total_comparisons*1000:.2f} ms")
    
    # Performance requirements
    comparisons_per_second = total_comparisons / total_time
    avg_time_ms = total_time / total_comparisons * 1000
    
    print(f"\n📈 PERFORMANCE VALIDATION:")
    print(f"   ✅ Fast enough for real-time use: {'✅' if comparisons_per_second > 1000 else '❌'}")
    print(f"   ✅ Sub-millisecond comparisons: {'✅' if avg_time_ms < 1.0 else '❌'}")
    
    return comparisons_per_second > 1000 and avg_time_ms < 1.0

def simulate_anthony_bek_real_results():
    """Simulate the Anthony Bek case with the actual results from the user."""
    
    print("\n🔍 SIMULATING REAL ANTHONY BEK RESULTS")
    print("=" * 60)
    
    class MockParser(EnhancedResultParser):
        def __init__(self):
            self.logger = type('Logger', (), {'info': print, 'debug': lambda x: None, 'error': print})()
    
    parser = MockParser()
    
    # The exact results from the user's feedback
    search_name = "Anthony Bek"
    actual_results = [
        "ANTHONY BEK",  # ✅ Should be exact
        "ANTHONY BEK",  # ✅ Should be exact  
        "ANTHONY BEK",  # ✅ Should be exact
        "ANTHONY BAKHOS",  # ❌ Should NOT be exact
        "ANTHONY CHARLES BAKHOS",  # ❌ Should NOT be exact
        "ANTHONY BOUCHAIA",  # ❌ Should NOT be exact
        "ANTHONY BAKHOS GEORGES",  # ❌ Should NOT be exact
        "ANTHONY BAKHOS GEORGES",  # ❌ Should NOT be exact
        "ANTHONY BOUCHAIA",  # ❌ Should NOT be exact
        "ANTHONY BAKHOS",  # ❌ Should NOT be exact
        "ANTHONY BOUCHAIA",  # ❌ Should NOT be exact
        "JOHANN ANTON JULES BACH",  # ❌ Should NOT be exact
        "LIAM ANTHONY BOUKAS",  # ❌ Should NOT be exact
    ]
    
    print(f"Search: '{search_name}'")
    print(f"Total results: {len(actual_results)}")
    print(f"Expected exact matches: 3")
    print()
    
    # Create PersonResult objects and validate
    person_results = []
    for i, result_name in enumerate(actual_results, 1):
        # Mock additional data
        person = PersonResult(
            name=result_name,
            date_of_birth=f"0{i}/11/199{i%10}",
            location=f"SYDNEY NSW"
        )
        
        # Apply validation
        match_type, confidence = parser._validate_match(search_name, person.name)
        person.match_type = match_type
        person.confidence_score = confidence
        
        person_results.append(person)
    
    # Use EnhancedNameMatcher to find exact matches
    matcher = EnhancedNameMatcher(strict_mode=True)
    match_found, exact_matches = matcher.find_exact_matches(search_name, person_results)
    
    print(f"📊 RESULTS:")
    print(f"   Total results processed: {len(person_results)}")
    print(f"   Exact matches found: {len(exact_matches)}")
    print(f"   Expected exact matches: 3")
    print(f"   Match found: {match_found}")
    
    # Detailed breakdown
    exact_count = sum(1 for p in person_results if p.match_type == "exact")
    partial_count = sum(1 for p in person_results if p.match_type == "partial")
    none_count = sum(1 for p in person_results if p.match_type == "none")
    
    print(f"\n📈 BREAKDOWN:")
    print(f"   Exact: {exact_count}")
    print(f"   Partial: {partial_count}")
    print(f"   None: {none_count}")
    
    success = len(exact_matches) == 3
    print(f"\n🎯 VALIDATION:")
    if success:
        print("✅ SUCCESS: Found exactly 3 exact matches as expected!")
        print("✅ The Anthony Bek exact matching issue has been fixed!")
    else:
        print(f"❌ ISSUE: Expected 3 exact matches, found {len(exact_matches)}")
    
    return success

if __name__ == "__main__":
    print("🚀 VALIDATING EXACT MATCHING FIX")
    print("=" * 80)
    print("Testing the corrected exact matching logic without browser automation")
    print()
    
    # Run all tests
    test1_passed = test_anthony_bek_validation()
    test2_passed = test_performance_characteristics()
    test3_passed = simulate_anthony_bek_real_results()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL VALIDATION RESULTS")
    print("=" * 80)
    
    print(f"✅ Anthony Bek validation test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Performance characteristics test: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"✅ Real results simulation test: {'PASSED' if test3_passed else 'FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ The exact matching logic fix is working correctly")
        print("✅ Anthony Bek now returns only exact matches (3 instead of 12)")
        print("✅ Performance is acceptable for real-time use")
        print("📋 Ready for production use with corrected exact matching")
    else:
        print("\n⚠️  Some validation tests failed")
        print("🔧 The exact matching logic may need further refinement")
    
    print(f"\n📊 Overall Success Rate: {sum([test1_passed, test2_passed, test3_passed])}/3 tests passed")