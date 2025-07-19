#!/usr/bin/env python3
"""
FAST CLI TEST - Quick test with all optimizations and result verification
"""

import asyncio
import sys
import logging
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import ReadySearchAutomation
from config import Config
from readysearch_automation.input_loader import SearchRecord

async def fast_cli_test(names_input: str = "Andro Cutuk,1975"):
    """Fast CLI test with all optimizations"""
    
    print("⚡ FAST CLI TEST WITH ALL OPTIMIZATIONS")
    print(f"🎯 Testing: {names_input}")
    print("")
    
    try:
        # Parse names
        search_records = []
        names = names_input.split(';')
        
        for name_entry in names:
            name_entry = name_entry.strip()
            if ',' in name_entry:
                parts = name_entry.split(',', 1)
                name = parts[0].strip()
                try:
                    birth_year = int(parts[1].strip())
                    search_records.append(SearchRecord(name=name, birth_year=birth_year))
                    print(f"📋 Parsed: {name} (born {birth_year})")
                except ValueError:
                    search_records.append(SearchRecord(name=name_entry))
                    print(f"📋 Parsed: {name_entry} (no birth year)")
            else:
                search_records.append(SearchRecord(name=name_entry))
                print(f"📋 Parsed: {name_entry} (no birth year)")
        
        print(f"✅ Total names: {len(search_records)}")
        
        # ULTRA-FAST configuration
        config = Config.get_config()
        config.update({
            'headless': True,  # SPEED: No browser window
            'delay': 0.3,  # SPEED: Ultra-minimal delay
            'page_timeout': 10000,  # SPEED: 10s max per action
            'element_timeout': 1500,  # SPEED: 1.5s max per element
            'max_retries': 1,  # SPEED: Only 1 retry
            'log_level': 'ERROR',  # SPEED: Minimal logging
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'fast_test.log',
            'output_file': 'fast_test_results'
        })
        
        print(f"⚙️ ULTRA-FAST CONFIG: delay={config['delay']}s, timeouts={config['page_timeout']}ms/{config['element_timeout']}ms")
        
        # Process each name with timing
        all_results = []
        total_start = time.time()
        
        for i, search_record in enumerate(search_records):
            print(f"\n🎯 === NAME {i+1}/{len(search_records)}: {search_record.name} ===")
            
            search_start = time.time()
            
            # Create fresh automation instance for each search
            automation = ReadySearchAutomation(config)
            
            # Run automation
            print(f"🚀 Starting automation...")
            success = await automation.run_automation([search_record])
            
            search_duration = time.time() - search_start
            print(f"📊 Completed in {search_duration:.2f}s (success: {success})")
            
            # Check results
            reporter_results = automation.reporter.get_results()
            print(f"📋 Reporter has {len(reporter_results)} results")
            
            if reporter_results:
                latest_result = reporter_results[-1]
                print(f"📄 Latest result: {latest_result.get('status', 'Unknown')} - {latest_result.get('matches_found', 0)} matches")
                
                # Check for actual match data
                if 'match_details' in latest_result and latest_result['match_details']:
                    print(f"✅ FOUND MATCH DETAILS: {len(latest_result['match_details'])} entries")
                    for j, detail in enumerate(latest_result['match_details'][:3]):  # Show first 3
                        print(f"   Match {j+1}: {detail.get('matched_name', 'N/A')} - {detail.get('date_of_birth', 'N/A')}")
                
                result_summary = {
                    'name': search_record.name,
                    'birth_year': search_record.birth_year,
                    'status': latest_result.get('status', 'Unknown'),
                    'search_duration': search_duration,
                    'matches_found': latest_result.get('matches_found', 0),
                    'automation_success': success,
                    'has_match_details': bool(latest_result.get('match_details')),
                    'raw_result': latest_result
                }
            else:
                print(f"❌ NO RESULTS from reporter")
                result_summary = {
                    'name': search_record.name,
                    'birth_year': search_record.birth_year,
                    'status': 'Error',
                    'search_duration': search_duration,
                    'matches_found': 0,
                    'automation_success': success,
                    'has_match_details': False,
                    'error': 'No results in reporter'
                }
            
            all_results.append(result_summary)
            
            # Performance check
            performance_status = "✅ EXCELLENT" if search_duration <= 30 else "⚠️ SLOW" if search_duration <= 60 else "❌ FAILED"
            print(f"⏱️ Performance: {performance_status} ({search_duration:.2f}s)")
        
        total_duration = time.time() - total_start
        
        # Generate report
        print("\n" + "="*60)
        print("🎯 FAST CLI TEST REPORT")
        print("="*60)
        
        print(f"📊 PERFORMANCE SUMMARY:")
        print(f"   Total Time: {total_duration:.2f}s")
        print(f"   Average per Search: {total_duration/len(all_results):.2f}s")
        print(f"   Target: ≤30s per search")
        
        performance_met = all(r['search_duration'] <= 30 for r in all_results)
        print(f"   Performance Target: {'✅ MET' if performance_met else '❌ NOT MET'}")
        
        print(f"\n📋 RESULTS BREAKDOWN:")
        matches = [r for r in all_results if r['matches_found'] > 0]
        no_matches = [r for r in all_results if r['matches_found'] == 0 and r['status'] != 'Error']
        errors = [r for r in all_results if r['status'] == 'Error']
        
        print(f"   ✅ Found Matches: {len(matches)}")
        print(f"   ⭕ No Matches: {len(no_matches)}")
        print(f"   ❌ Errors: {len(errors)}")
        
        print(f"\n📄 DETAILED RESULTS:")
        for i, result in enumerate(all_results):
            status_emoji = "✅" if result['matches_found'] > 0 else "⭕" if result['status'] != 'Error' else "❌"
            birth_info = f" (born {result['birth_year']})" if result['birth_year'] else ""
            match_details = f" [{result['matches_found']} matches]" if result['matches_found'] > 0 else ""
            has_details = "📋" if result['has_match_details'] else "🚫"
            
            print(f"   {i+1}. {status_emoji} {result['name']}{birth_info}{match_details}")
            print(f"      Duration: {result['search_duration']:.2f}s | Details: {has_details}")
        
        print("="*60)
        
        return all_results
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return []

if __name__ == "__main__":
    print("⚡ FAST CLI TEST - ReadySearch Automation")
    print("🎯 Optimized for maximum speed and accurate results")
    print("")
    
    # Test with sample names
    test_cases = [
        "Andro Cutuk,1975",
        "Anthony Bek,1993", 
        "Ghafoor Jaggi Nadery,1978"
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 TESTING: {test_case}")
        results = asyncio.run(fast_cli_test(test_case))
        
        if results:
            result = results[0]
            if result['search_duration'] <= 30:
                print(f"✅ PASS: {result['search_duration']:.2f}s ≤ 30s")
            else:
                print(f"❌ FAIL: {result['search_duration']:.2f}s > 30s")
        
        print("-" * 40)
    
    print("\n🎉 FAST CLI TEST COMPLETED!")