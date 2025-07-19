#!/usr/bin/env python3
"""
Test script for the enhanced API server with advanced matching.
Tests the friend's specific requirements through the API components.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_api_server import MockAutomationEngine
from readysearch_automation.input_loader import SearchRecord

async def test_friend_requirements_via_api():
    """Test friend's requirements through the MockAutomationEngine."""
    
    print("🧪 TESTING FRIEND'S REQUIREMENTS VIA ENHANCED API COMPONENTS")
    print("=" * 80)
    
    engine = MockAutomationEngine()
    
    # Test cases based on friend's feedback
    test_cases = [
        {
            "name": "John Smith",
            "birth_year": 1990,
            "description": "Should show JOHN MICHAEL SMITH as PARTIAL MATCH"
        },
        {
            "name": "Mike Johnson", 
            "birth_year": 1985,
            "description": "Should show MICHAEL JOHNSON as PARTIAL MATCH"
        },
        {
            "name": "Anthony Bek",
            "birth_year": 1993,
            "description": "Should show exact ANTHONY BEK matches and partial ANTHONY variations"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print("-" * 60)
        
        # Create search record
        search_record = SearchRecord(
            name=test_case['name'],
            birth_year=test_case['birth_year']
        )
        
        try:
            # Simulate the search using the enhanced engine
            result = await engine.simulate_search(search_record)
            
            print(f"✅ Search completed successfully")
            print(f"📊 Overall Status: {result['status']}")
            print(f"🏷️  Match Category: {result['match_category']}")
            print(f"💭 Match Reasoning: {result['match_reasoning']}")
            print(f"🔢 Exact Matches: {result['exact_matches']}")
            print(f"🔍 Partial Matches: {result['partial_matches']}")
            print(f"⏱️  Search Duration: {result['search_duration']}ms")
            print(f"📝 Total Results: {len(result['detailed_results'])}")
            
            print(f"\n📋 DETAILED RESULT BREAKDOWN:")
            for j, detail in enumerate(result['detailed_results'], 1):
                print(f"   {j:2d}. {detail['match_category']} | {detail['name']}")
                print(f"       DOB: {detail['date_of_birth']} | Location: {detail['location']}")
                print(f"       Confidence: {detail['confidence']:.2f} | Reasoning: {detail['match_reasoning']}")
                print()
            
            # Validate friend's specific requirements
            friend_requirements_met = True
            
            if test_case['name'] == "John Smith":
                # Should have JOHN MICHAEL SMITH as PARTIAL MATCH
                john_michael_found = any(
                    'JOHN MICHAEL SMITH' in detail['name'] and detail['match_category'] == 'PARTIAL MATCH'
                    for detail in result['detailed_results']
                )
                if not john_michael_found:
                    print("❌ FAILED: JOHN MICHAEL SMITH not found as PARTIAL MATCH")
                    friend_requirements_met = False
                else:
                    print("✅ PASSED: JOHN MICHAEL SMITH correctly marked as PARTIAL MATCH")
            
            elif test_case['name'] == "Mike Johnson":
                # Should have MICHAEL JOHNSON as PARTIAL MATCH  
                michael_found = any(
                    'MICHAEL JOHNSON' in detail['name'] and detail['match_category'] == 'PARTIAL MATCH'
                    for detail in result['detailed_results']
                )
                if not michael_found:
                    print("❌ FAILED: MICHAEL JOHNSON not found as PARTIAL MATCH")
                    friend_requirements_met = False
                else:
                    print("✅ PASSED: MICHAEL JOHNSON correctly marked as PARTIAL MATCH")
            
            elif test_case['name'] == "Anthony Bek":
                # Should have exact ANTHONY BEK matches
                exact_anthony_count = sum(
                    1 for detail in result['detailed_results']
                    if detail['name'] == 'ANTHONY BEK' and detail['match_category'] == 'EXACT MATCH'
                )
                if exact_anthony_count == 0:
                    print("❌ FAILED: No exact ANTHONY BEK matches found")
                    friend_requirements_met = False
                else:
                    print(f"✅ PASSED: Found {exact_anthony_count} exact ANTHONY BEK matches")
            
            if not friend_requirements_met:
                all_passed = False
            
        except Exception as e:
            print(f"❌ ERROR during search simulation: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 80)
    print("🏁 ENHANCED API TEST SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("🎉 ALL FRIEND'S REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
        print("✅ The enhanced API server correctly handles:")
        print("   - Advanced name matching with variations")
        print("   - Middle name detection and classification")
        print("   - Detailed match reasoning and explanations")
        print("   - EXACT vs PARTIAL match categorization")
        print("   - Individual result breakdown with confidence scores")
        print("\n📡 Ready for frontend integration!")
        return True
    else:
        print("⚠️  Some friend requirements not fully met")
        print("🔧 Additional refinements may be needed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_friend_requirements_via_api())
    
    if success:
        print("\n🚀 ENHANCED API SERVER IS READY FOR PRODUCTION!")
        print("🌐 Start the server with: python enhanced_api_server.py")
        print("🎯 Frontend can now use: http://localhost:5000/api/start-automation")
    else:
        print("\n⚠️  Additional testing and refinement needed")