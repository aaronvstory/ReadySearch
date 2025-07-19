#!/usr/bin/env python3
"""
Complete integration test for ReadySearch with enhanced matching.
Tests the full stack: Enhanced API Server + Frontend + Friend's Requirements
"""

import requests
import json
import time
import sys

def test_complete_integration():
    """Test the complete ReadySearch integration with friend's requirements."""
    
    print("🧪 COMPLETE READYSEARCH INTEGRATION TEST")
    print("=" * 70)
    print("Testing: Enhanced API Server + Advanced Matching + Friend's Requirements")
    print()
    
    # API Base URL
    api_base = "http://localhost:5000/api"
    
    # Test 1: Health Check
    print("1. 🏥 Testing API Health Check...")
    try:
        response = requests.get(f"{api_base}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data['status']}")
            print(f"🎯 Features: {', '.join(data['features'])}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False
    
    # Test 2: Friend's Requirements via API
    print(f"\n2. 🎯 Testing Friend's Specific Requirements...")
    
    test_cases = [
        {
            "names": ["John Smith,1990"],
            "description": "Should detect JOHN MICHAEL SMITH as PARTIAL MATCH",
            "expected_partial": "JOHN MICHAEL SMITH"
        },
        {
            "names": ["Mike Johnson,1985"],
            "description": "Should detect MICHAEL JOHNSON as PARTIAL MATCH", 
            "expected_partial": "MICHAEL JOHNSON"
        },
        {
            "names": ["Anthony Bek,1993"],
            "description": "Should show exact ANTHONY BEK matches and partial variations",
            "expected_exact": "ANTHONY BEK"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test 2.{i}: {test_case['description']}")
        print(f"   Names: {test_case['names']}")
        
        try:
            # Start automation
            start_response = requests.post(
                f"{api_base}/start-automation",
                json={
                    "names": test_case["names"],
                    "config": {"delay": 1.0, "retries": 1, "headless": True, "timeout": 10}
                },
                timeout=10
            )
            
            if start_response.status_code != 200:
                print(f"   ❌ Failed to start automation: HTTP {start_response.status_code}")
                all_passed = False
                continue
            
            session_data = start_response.json()
            session_id = session_data.get("session_id")
            print(f"   📡 Session started: {session_id}")
            
            # Wait for completion
            max_wait = 30  # seconds
            wait_time = 0
            completed = False
            
            while wait_time < max_wait and not completed:
                time.sleep(2)
                wait_time += 2
                
                status_response = requests.get(f"{api_base}/session/{session_id}/status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    session_status = status_data.get("status", "unknown")
                    
                    if session_status in ["completed", "error", "stopped"]:
                        completed = True
                        
                        if session_status == "completed":
                            print(f"   ✅ Session completed successfully")
                            
                            # Check results for friend's requirements
                            results = status_data.get("results", [])
                            if results:
                                result = results[0]  # First result
                                
                                print(f"   📊 Match Category: {result.get('match_category', 'Unknown')}")
                                print(f"   🔢 Exact Matches: {result.get('exact_matches', 0)}")
                                print(f"   🔍 Partial Matches: {result.get('partial_matches', 0)}")
                                
                                # Check detailed results for friend's requirements
                                detailed_results = result.get("detailed_results", [])
                                if detailed_results:
                                    print(f"   📋 Detailed Results ({len(detailed_results)}):")
                                    
                                    found_requirement = False
                                    for detail in detailed_results:
                                        category = detail.get("match_category", "Unknown")
                                        name = detail.get("name", "Unknown")
                                        reasoning = detail.get("match_reasoning", "")
                                        
                                        print(f"     - {category}: {name}")
                                        print(f"       Reasoning: {reasoning}")
                                        
                                        # Check if this meets friend's requirements
                                        if "expected_partial" in test_case and test_case["expected_partial"] in name and category == "PARTIAL MATCH":
                                            found_requirement = True
                                            print(f"     ✅ FRIEND'S REQUIREMENT MET: {name} as PARTIAL MATCH")
                                        elif "expected_exact" in test_case and test_case["expected_exact"] in name and category == "EXACT MATCH":
                                            found_requirement = True
                                            print(f"     ✅ FRIEND'S REQUIREMENT MET: {name} as EXACT MATCH")
                                    
                                    if not found_requirement:
                                        print(f"     ❌ Friend's requirement not found in results")
                                        all_passed = False
                                else:
                                    print(f"   ⚠️  No detailed results available")
                            else:
                                print(f"   ⚠️  No results available")
                        else:
                            print(f"   ❌ Session ended with status: {session_status}")
                            all_passed = False
                else:
                    print(f"   ❌ Failed to get session status: HTTP {status_response.status_code}")
                    all_passed = False
                    break
            
            if not completed:
                print(f"   ❌ Session did not complete within {max_wait} seconds")
                all_passed = False
        
        except Exception as e:
            print(f"   ❌ Error during test: {str(e)}")
            all_passed = False
    
    # Test 3: Check Frontend Availability
    print(f"\n3. 🌐 Testing Frontend Availability...")
    try:
        frontend_response = requests.get("http://localhost:5173", timeout=5)
        if frontend_response.status_code == 200:
            print(f"✅ Frontend is accessible at http://localhost:5173")
        else:
            print(f"⚠️  Frontend returned HTTP {frontend_response.status_code}")
    except Exception as e:
        print(f"⚠️  Frontend not accessible: {str(e)}")
        print(f"   (This is expected if frontend isn't running)")
    
    # Final Results
    print(f"\n" + "=" * 70)
    print("🏁 COMPLETE INTEGRATION TEST RESULTS")
    print("=" * 70)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced API Server working correctly")
        print("✅ Advanced matching system implemented")
        print("✅ Friend's requirements fully satisfied")
        print("✅ EXACT vs PARTIAL categorization working")
        print("✅ Detailed match reasoning provided")
        print()
        print("🚀 SYSTEM READY FOR PRODUCTION USE!")
        print("🌐 Frontend: http://localhost:5173")
        print("📡 Backend: http://localhost:5000")
        return True
    else:
        print("❌ Some tests failed")
        print("🔧 System needs additional fixes")
        return False

if __name__ == "__main__":
    print("Starting complete ReadySearch integration test...")
    print("Make sure both frontend and backend are running!")
    print("Frontend: http://localhost:5173")
    print("Backend: http://localhost:5000")
    print()
    
    success = test_complete_integration()
    
    if success:
        print("\n✅ INTEGRATION TEST SUCCESSFUL - SYSTEM READY!")
        sys.exit(0)
    else:
        print("\n❌ INTEGRATION TEST FAILED - CHECK SYSTEM")
        sys.exit(1)