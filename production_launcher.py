#!/usr/bin/env python3
"""
ReadySearch Production Launcher
===============================

Quick launcher for testing ReadySearch automation with specific names.
Perfect for production testing and validation.
"""

import asyncio
import sys
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_automation import test_name_search
from config import Config

def main():
    """Main launcher interface."""
    print("🚀 ReadySearch Production Launcher")
    print("=" * 50)
    
    # Get name to search
    name = input("Enter name to search (or press Enter for 'Ghafoor Nadery'): ").strip()
    if not name:
        name = "Ghafoor Nadery"
        
    print(f"🔍 Searching for: {name}")
    
    # Load configuration
    config = Config.get_config()
    config['headless'] = False  # Show browser for demonstration
    
    # Run the search
    print("⚡ Starting automation...")
    result = asyncio.run(test_name_search(name, config))
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"📋 Target Name: {name}")
        print(f"📈 Total Results: {result.get('total_results', 0)}")
        print(f"🎯 Exact Matches: {result.get('exact_matches', 0)}")
        
        if result.get('exact_matches', 0) > 0:
            print("✅ MATCH FOUND!")
        else:
            print("❌ No exact matches found")
            
    print("\n🎉 Production test complete!")

if __name__ == "__main__":
    main()
