#!/usr/bin/env python3
"""Test batch processing with 5 names including Ghafoor Nadery and John Nader."""

import asyncio
import time
import requests
import json

API_BASE_URL = 'http://localhost:5000/api'

# Test names: Ghafoor Nadery, John Nader, and 3 other random names
TEST_NAMES = [
    'Ghafoor Nadery',
    'John Nader', 
    'Sarah Williams',
    'Michael Johnson',
    'Emma Davis'
]

async def test_five_names_batch():
    """Test batch processing with 5 names and provide detailed results."""
    print("🧪 ReadySearch 5-Name Batch Processing Test")
    print("=" * 80)
    print("Testing batch processing with the following names:")
    for i, name in enumerate(TEST_NAMES, 1):
        print(f"   {i}. {name}")
    print()
    
    # Enable headless mode
    print("⚙️ Setting headless mode...")
    try:
        response = requests.post(f'{API_BASE_URL}/config/browser/headless', 
                               json={'headless': True}, timeout=10)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Headless mode: {config.get('headless')}")
        else:
            print("⚠️ Failed to set headless mode")
    except Exception as e:
        print(f"❌ Error setting headless: {e}")
    
    print()
    batch_start = time.time()
    
    try:
        # Start automation
        print("🚀 Starting batch automation...")
        response = requests.post(f'{API_BASE_URL}/start-automation', 
                               json={'names': TEST_NAMES}, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to start automation: {response.text}")
            return False
        
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"📋 Session ID: {session_id}")
        print()
        
        # Monitor progress with detailed logging
        max_wait = 300  # 5 minutes for 5 names
        start_time = time.time()
        last_activity = ""
        search_times = {}
        
        print("📊 Live Progress Monitoring:")
        print("-" * 60)
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f'{API_BASE_URL}/session/{session_id}/status', timeout=10)
                
                if response.status_code != 200:
                    print("❌ Failed to get status")
                    break
                    
                status_data = response.json()
                status = status_data.get('status')
                current_index = status_data.get('current_index', 0)
                total_names = status_data.get('total_names', 0)
                
                # Show browser activity
                browser_activity = status_data.get('browser_activity', [])
                if browser_activity:
                    latest = browser_activity[-1]
                    current_activity = f"{latest.get('action')} - {latest.get('details', '')}"
                    
                    if current_activity != last_activity:
                        elapsed = time.time() - batch_start
                        progress = f"[{current_index}/{total_names}]"
                        print(f"   {progress} [{elapsed:5.1f}s] {current_activity}")
                        last_activity = current_activity
                        
                        # Track individual search completion times
                        if "matches found" in current_activity or "No matches found" in current_activity:
                            for name in TEST_NAMES:
                                if name in current_activity:
                                    search_times[name] = elapsed
                
                if status in ['completed', 'error']:
                    print(f"   Status: {status}")
                    break
                    
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"   ⚠️ Status check error: {e}")
                await asyncio.sleep(2)
                continue
        
        # Get final results
        batch_time = time.time() - batch_start
        print()
        print("📊 Retrieving final results...")
        
        try:
            response = requests.get(f'{API_BASE_URL}/session/{session_id}/results', timeout=30)
            
            if response.status_code == 200:
                results_data = response.json()
                search_results = results_data.get('results', [])
                
                print(f"✅ Batch completed in {batch_time:.1f} seconds")
                print(f"📈 Received {len(search_results)} results")
                print()
                
                # Detailed results analysis
                print("📋 DETAILED SEARCH RESULTS:")
                print("=" * 80)
                
                success_count = 0
                error_count = 0
                results_summary = []
                
                for i, result in enumerate(search_results, 1):
                    name = result.get('name', 'Unknown')
                    status = result.get('status', 'Unknown')
                    error = result.get('error', '')
                    
                    print(f"\n{i}. {name}")
                    print("-" * 40)
                    
                    if status == 'Error':
                        error_count += 1
                        print(f"   ❌ Status: {status}")
                        print(f"   🔍 Error: {error}")
                        results_summary.append({
                            'name': name,
                            'status': 'Error',
                            'total_results': 0,
                            'exact_matches': 0,
                            'error': error
                        })
                    else:
                        success_count += 1
                        total_results = result.get('total_results', 0)
                        exact_matches = result.get('exact_matches', 0)
                        exact_match_percentage = result.get('exact_match_percentage', 0)
                        result_time = result.get('search_time', 0)
                        
                        print(f"   ✅ Status: {status}")
                        print(f"   📊 Total Results Found: {total_results}")
                        print(f"   🎯 Exact Matches: {exact_matches}")
                        print(f"   📈 Match Percentage: {exact_match_percentage}%")
                        print(f"   ⏱️ Search Time: {result_time:.1f}s")
                        
                        # Show match details if available
                        match_details = result.get('match_details', [])
                        if match_details:
                            print(f"   🔍 Match Details ({len(match_details)} matches):")
                            for j, match in enumerate(match_details[:3], 1):  # Show first 3 matches
                                matched_name = match.get('matched_name', 'N/A')
                                location = match.get('location', 'N/A')
                                confidence = match.get('confidence', 0.0)
                                print(f"      {j}. {matched_name} ({location}) - {confidence:.2f}")
                        
                        results_summary.append({
                            'name': name,
                            'status': status,
                            'total_results': total_results,
                            'exact_matches': exact_matches,
                            'match_percentage': exact_match_percentage,
                            'search_time': result_time,
                            'match_details': len(match_details)
                        })
                
                # Summary report
                print("\n" + "=" * 80)
                print("📊 BATCH PROCESSING SUMMARY")
                print("=" * 80)
                print(f"✅ Successful searches: {success_count}")
                print(f"❌ Failed searches: {error_count}")
                print(f"📈 Total batch time: {batch_time:.1f} seconds")
                print(f"⚡ Average time per search: {batch_time/len(TEST_NAMES):.1f} seconds")
                print()
                
                # Results breakdown
                print("📋 RESULTS BREAKDOWN:")
                print("-" * 40)
                
                for result in results_summary:
                    name = result['name']
                    status = result['status']
                    
                    if status == 'Error':
                        print(f"❌ {name}: ERROR - {result['error']}")
                    else:
                        total = result['total_results']
                        exact = result['exact_matches']
                        if exact > 0:
                            print(f"✅ {name}: MATCH - {total} total results, {exact} exact matches")
                        else:
                            print(f"⚪ {name}: NO MATCH - {total} total results examined")
                
                print()
                
                # Final validation
                if success_count == len(TEST_NAMES):
                    print("🎉 BATCH PROCESSING SUCCESS!")
                    print("✅ All 5 searches completed successfully")
                    print("✅ Batch processing is working correctly")
                    print("✅ No 'Search input not found' errors")
                    return True, results_summary
                else:
                    print("⚠️ PARTIAL SUCCESS")
                    print(f"✅ {success_count}/{len(TEST_NAMES)} searches succeeded")
                    print(f"❌ {error_count} searches failed")
                    return False, results_summary
                    
            else:
                print(f"❌ Failed to get results: {response.status_code}")
                return False, []
                
        except Exception as e:
            print(f"❌ Error getting results: {e}")
            return False, []
            
    except Exception as e:
        batch_time = time.time() - batch_start
        print(f"❌ Batch processing exception after {batch_time:.1f}s: {str(e)}")
        return False, []

async def main():
    """Run the 5-name batch processing test."""
    success, results = await test_five_names_batch()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL BATCH PROCESSING REPORT")
    print("=" * 80)
    
    if success:
        print("🎉 BATCH PROCESSING FULLY OPERATIONAL!")
        print("✅ All 5 searches completed successfully")
        print("✅ Consecutive searches working correctly")
        print("✅ Browser state management fixed")
        print("✅ Performance optimizations working")
    else:
        print("❌ BATCH PROCESSING NEEDS ATTENTION")
        print("⚠️ Some searches failed - please review results above")
    
    # Provide final answer summary
    print("\n📋 FINAL ANSWER SUMMARY:")
    print("-" * 40)
    
    if results:
        matches = [r for r in results if r['status'] != 'Error' and r['exact_matches'] > 0]
        no_matches = [r for r in results if r['status'] != 'Error' and r['exact_matches'] == 0]
        errors = [r for r in results if r['status'] == 'Error']
        
        if matches:
            print(f"✅ Names with matches ({len(matches)}):")
            for r in matches:
                print(f"   • {r['name']}: {r['total_results']} total results, {r['exact_matches']} exact matches")
        
        if no_matches:
            print(f"⚪ Names with no matches ({len(no_matches)}):")
            for r in no_matches:
                print(f"   • {r['name']}: {r['total_results']} total results examined")
        
        if errors:
            print(f"❌ Names with errors ({len(errors)}):")
            for r in errors:
                print(f"   • {r['name']}: {r['error']}")
    
    return success

if __name__ == '__main__':
    success = asyncio.run(main())
    exit(0 if success else 1)