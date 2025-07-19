#!/usr/bin/env python3
"""
Test script for strict matching criteria implementation
Tests the specific case mentioned by user: Ghafoor Jaggi Nadery should be NO MATCH
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

def test_strict_matching():
    """Test the strict matching criteria implementation"""
    print("🧪 TESTING STRICT MATCHING CRITERIA")
    print("=" * 60)
    
    matcher = AdvancedNameMatcher()
    
    # Test cases based on user requirements
    test_cases = [
        # (search_name, result_name, exact_first_name, expected_result, description)
        ("Ghafoor Jaggi Nadery", "GHAFOOR JAGGI NADER", False, "NOT MATCHED", "Last name NADERY vs NADER - should be NO MATCH"),
        ("Ghafoor Jaggi Nadery", "GHAFOOR JAGGI NADERY", False, "EXACT MATCH", "Perfect match"),
        ("Andro Cutuk", "ANDRO CUTUK", False, "EXACT MATCH", "Perfect match"),
        ("Anthony Bek", "ANTHONY BEK", False, "EXACT MATCH", "Perfect match"),
        ("John Smith", "JONATHAN SMITH", False, "PARTIAL MATCH", "First name variation allowed"),
        ("John Smith", "JONATHAN SMITH", True, "NOT MATCHED", "First name variation not allowed with exact_first_name=True"),
        ("John Smith", "JOHN SMITHSON", False, "NOT MATCHED", "Last name SMITH vs SMITHSON - should be NO MATCH"),
        ("John Smith", "JOHN MICHAEL SMITH", False, "EXACT MATCH", "Additional middle name should be exact match"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, (search_name, result_name, exact_first_name, expected, description) in enumerate(test_cases, 1):
        print(f"\n{i}. {description}")
        print(f"   Search: '{search_name}' vs Result: '{result_name}' (exact_first_name={exact_first_name})")
        
        result = matcher.match_names_strict(search_name, result_name, exact_first_name)
        actual_category = result.get_display_category()
        
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual_category}")
        print(f"   Reasoning: {result.reasoning}")
        
        if expected == actual_category:
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED! Strict matching criteria implemented correctly.")
        print("🎉 Ghafoor Jaggi Nadery will now show as NO MATCH for NADER results")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Issues need to be fixed.")
        return False

def test_real_world_cases():
    """Test with real-world examples that user might encounter"""
    print(f"\n" + "=" * 60)
    print("🌍 TESTING REAL-WORLD CASES")
    print("=" * 60)
    
    matcher = AdvancedNameMatcher()
    
    # Real-world cases that should be NO MATCH due to last name differences
    no_match_cases = [
        ("Smith", "Smithson"),
        ("Johnson", "Johnston"), 
        ("Brown", "Browne"),
        ("Wilson", "Williamson"),
        ("Davis", "Davidson"),
        ("Miller", "Mills"),
        ("Garcia", "Garcias"),
        ("Rodriguez", "Rodrigues"),
        ("Anderson", "Andrews"),
        ("Taylor", "Tyler")
    ]
    
    print("Testing last name variations that should be NO MATCH:")
    all_correct = True
    
    for search_last, result_last in no_match_cases:
        search_name = f"John {search_last}"
        result_name = f"JOHN {result_last.upper()}"
        
        result = matcher.match_names_strict(search_name, result_name, False)
        actual_category = result.get_display_category()
        
        print(f"  {search_name} vs {result_name}: {actual_category}")
        
        if actual_category != "NOT MATCHED":
            print(f"    ❌ ERROR: Should be NO MATCH but got {actual_category}")
            all_correct = False
        else:
            print(f"    ✅ Correct: NO MATCH")
    
    return all_correct

if __name__ == "__main__":
    print("🔍 ReadySearch Strict Matching Test Suite")
    print("=" * 60)
    
    basic_tests_passed = test_strict_matching()
    real_world_tests_passed = test_real_world_cases()
    
    print(f"\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if basic_tests_passed and real_world_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Strict matching criteria fully implemented")
        print("✅ Last name exact matching enforced")
        print("✅ Ghafoor Jaggi Nadery case will work correctly")
        print("\n🚀 Ready for production use!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️  Implementation needs fixes before production use")
        sys.exit(1)