#!/usr/bin/env python3
"""Debug API response to understand result extraction issues."""

import asyncio
import time
import requests
import json

API_BASE_URL = 'http://localhost:5000/api'

async def debug_api_response():
    """Debug the API response for Ghafoor Nadery."""
    print("🔍 Debugging API Response for Ghafoor Nadery")
    print("=" * 60)
    
    # Enable headless mode
    print("⚙️ Setting headless mode...")
    try:
        response = requests.post(f'{API_BASE_URL}/config/browser/headless', 
                               json={'headless': True}, timeout=10)
        print(f"✅ Headless mode: {response.json().get('headless')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Start single search
    print("🚀 Starting single search for Ghafoor Nadery...")
    try:
        response = requests.post(f'{API_BASE_URL}/start-automation', 
                               json={'names': ['Ghafoor Nadery']}, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to start: {response.text}")
            return
        
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"📋 Session ID: {session_id}")
        
        # Monitor progress
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f'{API_BASE_URL}/session/{session_id}/status', timeout=10)
                
                if response.status_code != 200:
                    print("❌ Failed to get status")
                    break
                    
                status_data = response.json()
                status = status_data.get('status')
                
                if status in ['completed', 'error']:
                    print(f"✅ Status: {status}")
                    break
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Status error: {e}")
                break
        
        # Get detailed results
        print("\n📊 Getting detailed results...")
        try:
            response = requests.get(f'{API_BASE_URL}/session/{session_id}/results', timeout=30)
            
            if response.status_code == 200:
                results_data = response.json()
                print(f"✅ Results received: {response.status_code}")
                
                # Save full response for analysis
                with open("ghafoor_api_response.json", "w") as f:
                    json.dump(results_data, f, indent=2)
                print("💾 Saved full API response to ghafoor_api_response.json")
                
                # Analyze results
                search_results = results_data.get('results', [])
                if search_results:
                    result = search_results[0]
                    
                    print(f"\n📋 RESULT ANALYSIS:")
                    print(f"   Name: {result.get('name')}")
                    print(f"   Status: {result.get('status')}")
                    print(f"   Total Results: {result.get('total_results')}")
                    print(f"   Exact Matches: {result.get('exact_matches')}")
                    
                    # Check if there are raw results data
                    if 'raw_results' in result:
                        raw_results = result['raw_results']
                        print(f"   Raw Results Count: {len(raw_results)}")
                        
                        # Show first few raw results
                        for i, raw_result in enumerate(raw_results[:5]):
                            print(f"     {i+1}. {raw_result}")
                    
                    # Check match details
                    match_details = result.get('match_details', [])
                    print(f"   Match Details Count: {len(match_details)}")
                    
                    if match_details:
                        for i, match in enumerate(match_details[:3]):
                            print(f"     {i+1}. {match}")
                    
                    # Check if there's additional debug info
                    if 'debug_info' in result:
                        debug_info = result['debug_info']
                        print(f"   Debug Info: {debug_info}")
                
                else:
                    print("❌ No search results found")
                    
            else:
                print(f"❌ Failed to get results: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting results: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(debug_api_response())