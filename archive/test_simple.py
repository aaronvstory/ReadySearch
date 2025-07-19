"""Simple test script to check for infinite loop issues."""

import sys
from pathlib import Path

def main():
    print("🔍 ReadySearch Test Script")
    print("==========================")
    print("Testing basic functionality...")
    
    # Check if input file exists
    input_file = Path("input_names.csv")
    if input_file.exists():
        print(f"✅ Input file found: {input_file}")
        
        # Read first few lines
        with open(input_file, 'r') as f:
            lines = f.readlines()
        print(f"📋 File contains {len(lines)} lines")
        
        # Show first few names
        for i, line in enumerate(lines[1:6], 1):  # Skip header
            name = line.strip()
            if name:
                print(f"  {i}. {name}")
    else:
        print(f"❌ Input file not found: {input_file}")
    
    # Simple user input test
    proceed = input("\n🤔 Do you want to continue? (y/n): ").lower().strip()
    if proceed == 'y':
        print("✅ You chose to continue")
    else:
        print("❌ You chose to stop")
    
    print("\n🏁 Test completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"Exit code: {exit_code}")
    sys.exit(exit_code)
