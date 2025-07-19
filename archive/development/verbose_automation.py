#!/usr/bin/env python3
"""
ULTRA-VERBOSE ReadySearch Automation with detailed emoji logging for every action
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

class VerboseLogger:
    """Ultra-verbose logger with emoji indicators for every action"""
    
    def __init__(self, name="VerboseAutomation"):
        self.logger = logging.getLogger(name)
        self.start_time = time.time()
        
    def log_action(self, emoji, action, details="", level="INFO"):
        """Log action with timestamp, emoji, and details"""
        elapsed = time.time() - self.start_time
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        message = f"{emoji} [{elapsed:06.2f}s] {timestamp} | {action}"
        if details:
            message += f" | {details}"
        
        print(message)
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
            
    def log_timing(self, emoji, action, start_time, details=""):
        """Log action with timing information"""
        duration = time.time() - start_time
        self.log_action(emoji, f"{action} (took {duration:.2f}s)", details)

# Set up ultra-verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultra_verbose.log', mode='w'),
        logging.StreamHandler()
    ]
)

async def ultra_verbose_automation_test(names_input: str):
    """
    Ultra-verbose automation test with detailed logging
    
    Args:
        names_input: Semicolon-separated names with optional birth years
                    Examples: "John Smith;Jane Doe,1990;Bob Jones"
    """
    vlog = VerboseLogger()
    
    vlog.log_action("🚀", "ULTRA-VERBOSE AUTOMATION STARTING")
    vlog.log_action("📝", f"Input received: {names_input}")
    
    try:
        # Parse names
        vlog.log_action("🔍", "Parsing semicolon-separated names...")
        search_records = []
        names = names_input.split(';')
        
        for i, name_entry in enumerate(names):
            vlog.log_action("📋", f"Processing name {i+1}: '{name_entry.strip()}'")
            name_entry = name_entry.strip()
            
            if ',' in name_entry:
                parts = name_entry.split(',', 1)
                name = parts[0].strip()
                try:
                    birth_year = int(parts[1].strip())
                    search_records.append(SearchRecord(name=name, birth_year=birth_year))
                    vlog.log_action("✅", f"Parsed with birth year: {name} (born {birth_year})")
                except ValueError:
                    search_records.append(SearchRecord(name=name_entry))
                    vlog.log_action("⚠️", f"Invalid birth year, using name only: {name_entry}")
            else:
                search_records.append(SearchRecord(name=name_entry))
                vlog.log_action("✅", f"Parsed name only: {name_entry}")
        
        vlog.log_action("📊", f"Total names parsed: {len(search_records)}")
        
        # Configuration with aggressive timeouts for speed
        vlog.log_action("⚙️", "Setting up SPEED-OPTIMIZED configuration...")
        config = Config.get_config()
        config.update({
            'headless': True,  # SPEED: No browser window
            'delay': 0.8,  # SPEED: Minimal delay
            'page_timeout': 15000,  # SPEED: 15s max per action
            'element_timeout': 2000,  # SPEED: 2s max per element
            'max_retries': 1,  # SPEED: Only 1 retry
            'log_level': 'DEBUG',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'ultra_verbose.log',
            'output_file': 'ultra_verbose_results'
        })
        
        vlog.log_action("🎯", f"Config: headless={config['headless']}, delay={config['delay']}s")
        vlog.log_action("⏱️", f"Timeouts: page={config['page_timeout']}ms, element={config['element_timeout']}ms")
        
        # Create automation instance
        vlog.log_action("🏗️", "Creating ReadySearch automation instance...")
        automation_start = time.time()
        automation = ReadySearchAutomation(config)
        vlog.log_timing("✅", "Automation instance created", automation_start)
        
        # Process each name with detailed logging
        all_results = []
        
        for i, search_record in enumerate(search_records):
            vlog.log_action("🎯", f"=== PROCESSING NAME {i+1}/{len(search_records)}: {search_record.name} ===")
            
            # Individual search timing
            search_start = time.time()
            
            vlog.log_action("🔄", f"Starting automation for: {search_record.name}")
            if search_record.birth_year:
                vlog.log_action("📅", f"Birth year: {search_record.birth_year}")
            
            # Run automation
            vlog.log_action("🚀", "Calling automation.run_automation()...")
            success = await automation.run_automation([search_record])
            
            search_duration = time.time() - search_start
            vlog.log_action("📊", f"Automation completed: success={success}, duration={search_duration:.2f}s")
            
            # Check results
            vlog.log_action("🔍", "Checking reporter for results...")
            reporter_results = automation.reporter.get_results()
            vlog.log_action("📋", f"Reporter has {len(reporter_results)} results")
            
            if reporter_results:
                for j, result in enumerate(reporter_results):
                    vlog.log_action("📄", f"Result {j+1}: {result}")
                    
                # Get the latest result
                latest_result = reporter_results[-1]
                result_summary = {
                    'name': search_record.name,
                    'birth_year': search_record.birth_year,
                    'status': latest_result.get('status', 'Unknown'),
                    'search_duration': search_duration,
                    'matches_found': latest_result.get('matches_found', 0),
                    'automation_success': success,
                    'raw_result': latest_result
                }
                
                vlog.log_action("📈", f"Result summary: {latest_result.get('status', 'Unknown')} - {latest_result.get('matches_found', 0)} matches")
            else:
                vlog.log_action("❌", "NO RESULTS FOUND IN REPORTER!")
                result_summary = {
                    'name': search_record.name,
                    'birth_year': search_record.birth_year,
                    'status': 'Error',
                    'search_duration': search_duration,
                    'matches_found': 0,
                    'automation_success': success,
                    'error': 'No results in reporter'
                }
            
            all_results.append(result_summary)
            vlog.log_action("✅", f"Completed {search_record.name} in {search_duration:.2f}s")
            
            # Performance check
            if search_duration > 30:
                vlog.log_action("🚨", f"PERFORMANCE WARNING: {search_duration:.2f}s > 30s target!", level="WARNING")
            else:
                vlog.log_action("⚡", f"PERFORMANCE OK: {search_duration:.2f}s <= 30s target")
        
        # Generate comprehensive report
        vlog.log_action("📊", "=== GENERATING COMPREHENSIVE REPORT ===")
        
        total_searches = len(all_results)
        matches = [r for r in all_results if r['matches_found'] > 0]
        no_matches = [r for r in all_results if r['matches_found'] == 0 and r['status'] != 'Error']
        errors = [r for r in all_results if r['status'] == 'Error']
        
        vlog.log_action("📈", f"SUMMARY: {len(matches)} matches, {len(no_matches)} no-matches, {len(errors)} errors")
        
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE AUTOMATION REPORT")
        print("="*80)
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Searches: {total_searches}")
        print(f"   ✅ Found Matches: {len(matches)}")
        print(f"   ⭕ No Matches: {len(no_matches)}")
        print(f"   ❌ Errors: {len(errors)}")
        print(f"   🎯 Success Rate: {((len(matches) + len(no_matches))/total_searches*100):.1f}%")
        
        print(f"\n⏱️ PERFORMANCE ANALYSIS:")
        avg_duration = sum(r['search_duration'] for r in all_results) / len(all_results)
        max_duration = max(r['search_duration'] for r in all_results)
        min_duration = min(r['search_duration'] for r in all_results)
        print(f"   Average Duration: {avg_duration:.2f}s")
        print(f"   Maximum Duration: {max_duration:.2f}s")
        print(f"   Minimum Duration: {min_duration:.2f}s")
        print(f"   Performance Target: {'✅ MET' if max_duration <= 30 else '❌ FAILED'} (30s max)")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(all_results):
            status_emoji = "✅" if result['matches_found'] > 0 else "⭕" if result['status'] != 'Error' else "❌"
            birth_info = f" (born {result['birth_year']})" if result['birth_year'] else ""
            print(f"   {i+1}. {status_emoji} {result['name']}{birth_info}")
            print(f"      Status: {result['status']}")
            print(f"      Matches: {result['matches_found']}")
            print(f"      Duration: {result['search_duration']:.2f}s")
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        print("\n" + "="*80)
        
        return all_results
        
    except Exception as e:
        vlog.log_action("💥", f"CRITICAL ERROR: {str(e)}", level="ERROR")
        import traceback
        vlog.log_action("🔍", f"Traceback: {traceback.format_exc()}", level="ERROR")
        return []

if __name__ == "__main__":
    print("🎯 ULTRA-VERBOSE READYSEARCH AUTOMATION")
    print("📝 Enter names separated by semicolons")
    print("💡 Examples: 'John Smith;Jane Doe,1990;Bob Jones'")
    print("💡 With birth years: 'Name,YYYY' or without: 'Name'")
    print("")
    
    # Get input from user
    names_input = input("🔤 Enter names (semicolon-separated): ").strip()
    
    if not names_input:
        print("❌ No names provided. Exiting.")
        sys.exit(1)
    
    print(f"\n🚀 Starting automation for: {names_input}")
    print("📊 Watch for detailed emoji-coded progress below...\n")
    
    # Run the automation
    results = asyncio.run(ultra_verbose_automation_test(names_input))
    
    print(f"\n🎉 AUTOMATION COMPLETED!")
    print(f"📊 Processed {len(results)} names")
    print(f"📄 Detailed logs saved to: ultra_verbose.log")