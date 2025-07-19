#!/usr/bin/env python3
"""
Test script to verify the strict matching fix for Ghafoor Jaggi Nadery case.
This tests that last names must be EXACT matches to avoid false positives.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType
from readysearch_automation.input_loader import SearchRecord

def test_ghafoor_case():
    """Test the specific Ghafoor Jaggi Nadery case that should be NO MATCH"""
    print("🧪 TESTING STRICT MATCHING FIX - GHAFOOR CASE")
    print("=" * 60)
    
    matcher = AdvancedNameMatcher()
    search_name = "Ghafoor Jaggi Nadery"
    
    # Test various results that should be NO MATCH due to last name differences
    test_cases = [
        ("GHAFOOR JAGGI NADER", "Last name 'NADER' != 'NADERY'"),
        ("GHAFOOR NADER", "Last name 'NADER' != 'NADERY'"),
        ("GHAFOOR JAGGI NADIR", "Last name 'NADIR' != 'NADERY'"),
        ("GHAFOOR NADURA", "Last name 'NADURA' != 'NADERY'"),
        ("GHAFOOR NADERY JAFRI", "Last name 'JAFRI' != 'NADERY'")
    ]
    
    all_passed = True
    
    for result_name, expected_reason in test_cases:
        print(f"\n🔍 Testing: '{search_name}' vs '{result_name}'")
        
        # Test strict matching with fuzzy first names (user default)
        match_result = matcher.match_names_strict(search_name, result_name, exact_first_name=False)
        
        if match_result.match_type == MatchType.NOT_MATCHED:
            print(f"   ✅ CORRECT: NO MATCH - {match_result.reasoning}")
        else:
            print(f"   ❌ WRONG: Got {match_result.get_display_category()} - {match_result.reasoning}")
            print(f"   📋 Expected: NO MATCH because {expected_reason}")
            all_passed = False
    
    return all_passed

def test_valid_matches():
    """Test cases that should still match correctly"""
    print("\n\n🧪 TESTING VALID MATCHES")
    print("=" * 60)
    
    matcher = AdvancedNameMatcher()
    
    # Test cases that should work
    test_cases = [
        ("Andro Cutuk", "ANDRO CUTUK", "EXACT MATCH"),
        ("Andro Cutuk", "ANDRO MICHAEL CUTUK", "EXACT MATCH"),  # Additional middle name
        ("Anthony Bek", "ANTHONY BEK", "EXACT MATCH"),
        ("Anthony Bek", "TONY BEK", "PARTIAL MATCH"),  # Name variation (if fuzzy enabled)
        ("Ghafoor Jaggi Nadery", "GHAFOOR JAGGI NADERY", "EXACT MATCH"),  # Exact match should work
    ]
    
    all_passed = True
    
    for search_name, result_name, expected_category in test_cases:
        print(f"\n🔍 Testing: '{search_name}' vs '{result_name}'")
        
        # Test with fuzzy first names (default)
        match_result = matcher.match_names_strict(search_name, result_name, exact_first_name=False)
        actual_category = match_result.get_display_category()
        
        if actual_category == expected_category:
            print(f"   ✅ CORRECT: {actual_category} - {match_result.reasoning}")
        else:
            print(f"   ❌ WRONG: Got {actual_category}, expected {expected_category}")
            print(f"   📋 Reasoning: {match_result.reasoning}")
            all_passed = False
    
    return all_passed

def test_exact_first_name_option():
    """Test the exact first name checkbox option"""
    print("\n\n🧪 TESTING EXACT FIRST NAME OPTION")
    print("=" * 60)
    
    matcher = AdvancedNameMatcher()
    
    test_cases = [
        ("Anthony Bek", "TONY BEK", False, "PARTIAL MATCH"),  # Fuzzy: should match
        ("Anthony Bek", "TONY BEK", True, "NOT MATCHED"),     # Exact: should not match
        ("John Smith", "JONATHAN SMITH", False, "PARTIAL MATCH"),  # Fuzzy: should match
        ("John Smith", "JONATHAN SMITH", True, "NOT MATCHED"),     # Exact: should not match
    ]
    
    all_passed = True
    
    for search_name, result_name, exact_first_name, expected_category in test_cases:
        mode = "EXACT first names" if exact_first_name else "FUZZY first names"
        print(f"\n🔍 Testing ({mode}): '{search_name}' vs '{result_name}'")
        
        match_result = matcher.match_names_strict(search_name, result_name, exact_first_name=exact_first_name)
        actual_category = match_result.get_display_category()
        
        if actual_category == expected_category:
            print(f"   ✅ CORRECT: {actual_category} - {match_result.reasoning}")
        else:
            print(f"   ❌ WRONG: Got {actual_category}, expected {expected_category}")
            print(f"   📋 Reasoning: {match_result.reasoning}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🚀 STRICT MATCHING VERIFICATION TEST")
    print("=" * 80)
    print("Testing the implementation of strict last name matching criteria:")
    print("✅ Last name must ALWAYS be exact (if off by 1 letter = NO MATCH)")
    print("✅ User can choose exact vs fuzzy first name matching")
    print("✅ Ghafoor Jaggi Nadery case should now show NO MATCH")
    print("=" * 80)
    
    # Run all test suites
    test1_passed = test_ghafoor_case()
    test2_passed = test_valid_matches()
    test3_passed = test_exact_first_name_option()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    
    if test1_passed:
        print("✅ Ghafoor Case Tests: PASSED")
    else:
        print("❌ Ghafoor Case Tests: FAILED")
    
    if test2_passed:
        print("✅ Valid Match Tests: PASSED")
    else:
        print("❌ Valid Match Tests: FAILED")
    
    if test3_passed:
        print("✅ Exact First Name Option Tests: PASSED")
    else:
        print("❌ Exact First Name Option Tests: FAILED")
    
    overall_success = test1_passed and test2_passed and test3_passed
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Strict matching criteria implemented correctly")
        print("✅ Ghafoor Jaggi Nadery will now show NO MATCH")
        print("✅ User can control exact vs fuzzy first name matching")
        print("✅ Ready for production use")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("❌ Review implementation and fix issues")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)