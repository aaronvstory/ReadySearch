"""
Test script for the new advanced matching system.
Validates the specific cases mentioned by the user's friend.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

def test_friend_requirements():
    """Test the specific requirements from the user's friend."""
    
    print("🎯 TESTING FRIEND'S SPECIFIC REQUIREMENTS")
    print("=" * 80)
    
    matcher = AdvancedNameMatcher()
    
    # Test cases based on friend's feedback
    test_cases = [
        # Case 1: Middle name additions - should be MATCHED
        {
            "search": "John Smith",
            "result": "JOHN MICHAEL SMITH",
            "expected_match": True,
            "expected_category": "PARTIAL MATCH",
            "description": "Middle name addition - should be MATCHED"
        },
        {
            "search": "John Smith", 
            "result": "JOHN DAVID SMITH",
            "expected_match": True,
            "expected_category": "PARTIAL MATCH",
            "description": "Different middle name addition - should be MATCHED"
        },
        
        # Case 2: Name variations - should be MATCHED
        {
            "search": "John Smith",
            "result": "JONATHAN SMITH", 
            "expected_match": True,
            "expected_category": "PARTIAL MATCH",
            "description": "Name variation (John → Jonathan) - should be MATCHED"
        },
        {
            "search": "Mike Johnson",
            "result": "MICHAEL JOHNSON",
            "expected_match": True,
            "expected_category": "PARTIAL MATCH", 
            "description": "Name variation (Mike → Michael) - should be MATCHED"
        },
        {
            "search": "Bill Williams",
            "result": "WILLIAM WILLIAMS",
            "expected_match": True,
            "expected_category": "PARTIAL MATCH",
            "description": "Name variation (Bill → William) - should be MATCHED"
        },
        
        # Case 3: Exact matches - should remain EXACT
        {
            "search": "John Smith",
            "result": "JOHN SMITH",
            "expected_match": True,
            "expected_category": "EXACT MATCH",
            "description": "Perfect exact match - should be EXACT"
        },
        
        # Case 4: Combinations - middle name + variation
        {
            "search": "John Smith",
            "result": "JONATHAN MICHAEL SMITH",
            "expected_match": True,
            "expected_category": "PARTIAL MATCH",
            "description": "Name variation + middle name - should be MATCHED"
        },
        
        # Case 5: Non-matches - should still be NOT MATCHED
        {
            "search": "John Smith",
            "result": "ANTHONY BAKHOS",
            "expected_match": False,
            "expected_category": "NOT MATCHED",
            "description": "Completely different name - should be NOT MATCHED"
        },
        
        # Case 6: Partial word matches - borderline cases
        {
            "search": "John Smith",
            "result": "JOHN WILLIAMS",
            "expected_match": True,  # Should match because first name matches
            "expected_category": "PARTIAL MATCH",
            "description": "First name match, different last name - should be PARTIAL"
        }
    ]
    
    print(f"Testing {len(test_cases)} cases based on friend's requirements...\n")
    
    all_passed = True
    passed_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        search_name = test_case["search"]
        result_name = test_case["result"]
        expected_match = test_case["expected_match"]
        expected_category = test_case["expected_category"]
        description = test_case["description"]
        
        # Run the matcher
        match_result = matcher.match_names(search_name, result_name)
        
        # Check if results meet expectations
        actual_match = match_result.is_match
        actual_category = match_result.get_display_category()
        
        # Determine if test passed
        match_correct = actual_match == expected_match
        category_correct = actual_category == expected_category
        test_passed = match_correct and category_correct
        
        if test_passed:
            passed_count += 1
            status = "✅ PASS"
        else:
            all_passed = False
            status = "❌ FAIL"
        
        print(f"{i:2d}. {status} | {description}")
        print(f"     Search: '{search_name}' → Result: '{result_name}'")
        print(f"     Expected: {expected_category} (Match: {expected_match})")
        print(f"     Actual:   {actual_category} (Match: {actual_match})")
        print(f"     Confidence: {match_result.confidence:.2f}")
        print(f"     Reasoning: {match_result.reasoning}")
        
        if not test_passed:
            print(f"     🚨 MISMATCH DETAILS:")
            if not match_correct:
                print(f"        - Match status: Expected {expected_match}, got {actual_match}")
            if not category_correct:
                print(f"        - Category: Expected '{expected_category}', got '{actual_category}'")
        
        print()
    
    print("📊 SUMMARY:")
    print(f"   Total test cases: {len(test_cases)}")
    print(f"   Passed: {passed_count}")
    print(f"   Failed: {len(test_cases) - passed_count}")
    print(f"   Success rate: {(passed_count/len(test_cases)*100):.1f}%")
    
    if all_passed:
        print("\n🎉 ALL FRIEND'S REQUIREMENTS PASSED!")
        print("✅ The new matching system correctly handles:")
        print("   - Middle name additions (JOHN SMITH → JOHN MICHAEL SMITH)")
        print("   - Name variations (JOHN → JONATHAN)")
        print("   - Exact matches remain exact")
        print("   - Detailed reasoning for each match")
        return True
    else:
        print(f"\n⚠️  {len(test_cases) - passed_count} tests failed")
        print("🔧 The matching system needs further refinement")
        return False

def test_anthony_bek_with_new_system():
    """Test the Anthony Bek case with the new advanced matching system."""
    
    print("\n🔍 TESTING ANTHONY BEK WITH NEW ADVANCED SYSTEM")
    print("=" * 80)
    
    matcher = AdvancedNameMatcher()
    
    search_name = "Anthony Bek"
    test_results = [
        # Should be EXACT matches
        "ANTHONY BEK",
        "anthony bek", 
        "Anthony Bek",
        
        # Should be PARTIAL matches (previously incorrectly categorized)
        "ANTHONY BAKHOS",
        "ANTHONY CHARLES BAKHOS", 
        "ANTHONY BOUCHAIA",
        "JOHANN ANTON JULES BACH",
        "LIAM ANTHONY BOUKAS",
        
        # Should be NOT MATCHED
        "ROBERT SMITH",
        "MARY JOHNSON"
    ]
    
    print(f"Search: '{search_name}'")
    print(f"Testing against {len(test_results)} result names...\n")
    
    exact_count = 0
    partial_count = 0
    not_matched_count = 0
    
    for i, result_name in enumerate(test_results, 1):
        match_result = matcher.match_names(search_name, result_name)
        
        category = match_result.get_display_category()
        is_match = match_result.is_match
        
        if match_result.match_type == MatchType.EXACT:
            exact_count += 1
            emoji = "✅"
        elif is_match:
            partial_count += 1
            emoji = "🔍"
        else:
            not_matched_count += 1
            emoji = "❌"
        
        print(f"{i:2d}. {emoji} {category} | '{result_name}'")
        print(f"     Confidence: {match_result.confidence:.2f}")
        print(f"     Reasoning: {match_result.reasoning}")
        print()
    
    print("📊 ANTHONY BEK RESULTS BREAKDOWN:")
    print(f"   ✅ EXACT MATCHES: {exact_count}")
    print(f"   🔍 PARTIAL MATCHES: {partial_count}")
    print(f"   ❌ NOT MATCHED: {not_matched_count}")
    
    # Validate against expected results
    expected_exact = 3  # The 3 ANTHONY BEK variations
    expected_partial = 5  # The partial name matches
    expected_not_matched = 2  # The completely unrelated names
    
    print(f"\n🎯 VALIDATION:")
    exact_correct = exact_count == expected_exact
    partial_correct = partial_count == expected_partial
    not_matched_correct = not_matched_count == expected_not_matched
    
    print(f"   Exact matches: {exact_count}/{expected_exact} {'✅' if exact_correct else '❌'}")
    print(f"   Partial matches: {partial_count}/{expected_partial} {'✅' if partial_correct else '❌'}")
    print(f"   Not matched: {not_matched_count}/{expected_not_matched} {'✅' if not_matched_correct else '❌'}")
    
    if exact_correct and partial_correct and not_matched_correct:
        print("\n✅ Anthony Bek test passed with new advanced system!")
        return True
    else:
        print("\n⚠️  Anthony Bek test results don't match expectations")
        return False

def test_name_variations():
    """Test comprehensive name variation detection."""
    
    print("\n🔄 TESTING COMPREHENSIVE NAME VARIATIONS")
    print("=" * 80)
    
    matcher = AdvancedNameMatcher()
    
    variation_tests = [
        ("John", "Jonathan"),
        ("Mike", "Michael"),
        ("Bill", "William"),
        ("Bob", "Robert"),
        ("Dick", "Richard"),
        ("Liz", "Elizabeth"),
        ("Jenny", "Jennifer"),
        ("Chris", "Christopher"),
        ("Matt", "Matthew"),
        ("Tony", "Anthony"),
        ("Ben", "Benjamin"),
        ("Alex", "Alexander"),
        ("Nick", "Nicholas"),
        ("Kate", "Catherine"),
        ("Maggie", "Margaret"),
        ("Pat", "Patricia"),
        ("Steph", "Stephanie"),
        ("Sam", "Samantha")
    ]
    
    print(f"Testing {len(variation_tests)} name variation pairs...\n")
    
    all_passed = True
    for i, (short_name, full_name) in enumerate(variation_tests, 1):
        # Test both directions
        search_name = f"{short_name} Smith"
        result_name = f"{full_name.upper()} SMITH"
        
        match_result = matcher.match_names(search_name, result_name)
        
        if match_result.is_match:
            status = "✅ MATCH"
        else:
            status = "❌ NO MATCH"
            all_passed = False
        
        print(f"{i:2d}. {status} | '{search_name}' → '{result_name}'")
        print(f"     Category: {match_result.get_display_category()}")
        print(f"     Confidence: {match_result.confidence:.2f}")
        print()
    
    if all_passed:
        print("✅ All name variations correctly detected!")
        return True
    else:
        print("⚠️  Some name variations not detected properly")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE ADVANCED MATCHING SYSTEM TEST")
    print("=" * 100)
    print("Testing the new advanced matching system based on friend's requirements")
    print()
    
    # Run all tests
    friend_test_passed = test_friend_requirements()
    anthony_test_passed = test_anthony_bek_with_new_system()
    variation_test_passed = test_name_variations()
    
    print("\n" + "=" * 100)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 100)
    
    print(f"✅ Friend's requirements test: {'PASSED' if friend_test_passed else 'FAILED'}")
    print(f"✅ Anthony Bek case test: {'PASSED' if anthony_test_passed else 'FAILED'}")
    print(f"✅ Name variations test: {'PASSED' if variation_test_passed else 'FAILED'}")
    
    if all([friend_test_passed, anthony_test_passed, variation_test_passed]):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The advanced matching system successfully handles:")
        print("   - Friend's specific requirements (middle names, variations)")
        print("   - Anthony Bek case with proper categorization")
        print("   - Comprehensive name variation detection")
        print("   - Detailed reasoning and explanations")
        print("\n📋 Ready for UI integration and API updates!")
    else:
        print("\n⚠️  Some tests failed - system needs refinement")
    
    total_tests = 3
    passed_tests = sum([friend_test_passed, anthony_test_passed, variation_test_passed])
    print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")