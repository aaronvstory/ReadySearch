#!/usr/bin/env python3
"""
Test export functionality for all formats
"""

import sys
import json
import csv
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_export_functionality():
    """Test all export formats with sample data"""
    print("🧪 Testing Export Functionality")
    print("=" * 40)
    
    # Import the enhanced CLI class
    try:
        from enhanced_cli import EnhancedReadySearchCLI, SearchResult
        print("✅ Enhanced CLI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Enhanced CLI: {e}")
        return False
    
    # Create sample results
    sample_results = [
        SearchResult(
            name="John Smith",
            status="Match",
            search_duration=6.83,
            matches_found=2,
            exact_matches=2,
            partial_matches=0,
            match_category="EXACT MATCH",
            match_reasoning="Found exact matches",
            detailed_results=[
                {
                    "matched_name": "JOHN SMITH",
                    "date_of_birth": "15/03/1985",
                    "match_type": "EXACT MATCH",
                    "confidence": 1.0
                },
                {
                    "matched_name": "JOHN SMITH",
                    "date_of_birth": "15/03/1985", 
                    "match_type": "EXACT MATCH",
                    "confidence": 1.0
                }
            ],
            timestamp=datetime.now().isoformat(),
            birth_year=1985
        ),
        SearchResult(
            name="Jane Doe",
            status="No Match",
            search_duration=5.21,
            matches_found=0,
            exact_matches=0,
            partial_matches=0,
            match_category="NOT MATCHED",
            match_reasoning="No meaningful matches found",
            detailed_results=[],
            timestamp=datetime.now().isoformat(),
            birth_year=1990
        ),
        SearchResult(
            name="Test Person",
            status="Match",
            search_duration=7.45,
            matches_found=1,
            exact_matches=1,
            partial_matches=0,
            match_category="EXACT MATCH",
            match_reasoning="Found exact match",
            detailed_results=[
                {
                    "matched_name": "TEST PERSON",
                    "date_of_birth": "UNKNOWN",
                    "match_type": "EXACT MATCH",
                    "confidence": 0.95
                }
            ],
            timestamp=datetime.now().isoformat()
        )
    ]
    
    print(f"✅ Created {len(sample_results)} sample results")
    
    # Create CLI instance and add sample results
    cli = EnhancedReadySearchCLI()
    cli.session_results = sample_results
    
    print("✅ CLI instance created with sample data")
    
    # Test JSON export
    print("\n📄 Testing JSON Export...")
    try:
        json_filename = "test_export_results"  # No extension - function adds it
        cli.export_json(json_filename)
        
        # Verify JSON file was created and is valid
        full_filename = f"{json_filename}.json"
        if os.path.exists(full_filename):
            with open(full_filename, 'r') as f:
                data = json.load(f)
            print(f"✅ JSON export successful: {len(data['results'])} results")
            print(f"   Export info: {data['export_info']['tool_version']}")
            os.remove(full_filename)  # Cleanup
        else:
            print("❌ JSON file not created")
            return False
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test CSV export
    print("\n📊 Testing CSV Export...")
    try:
        csv_filename = "test_export_results"  # No extension - function adds it
        cli.export_csv(csv_filename)
        
        # Verify CSV file was created and is valid
        full_filename = f"{csv_filename}.csv"
        if os.path.exists(full_filename):
            with open(full_filename, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            print(f"✅ CSV export successful: {len(rows)-1} data rows (plus header)")
            print(f"   Header columns: {len(rows[0])}")
            os.remove(full_filename)  # Cleanup
        else:
            print("❌ CSV file not created")
            return False
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test TXT export  
    print("\n📝 Testing TXT Export...")
    try:
        txt_filename = "test_export_results"  # No extension - function adds it
        cli.export_txt(txt_filename)
        
        # Verify TXT file was created and has content
        full_filename = f"{txt_filename}.txt"
        if os.path.exists(full_filename):
            with open(full_filename, 'r') as f:
                content = f.read()
            print(f"✅ TXT export successful: {len(content)} characters")
            print(f"   Contains report header: {'READYSEARCH' in content}")
            os.remove(full_filename)  # Cleanup
        else:
            print("❌ TXT file not created")
            return False
    except Exception as e:
        print(f"❌ TXT export failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All export formats working correctly!")
    return True

if __name__ == "__main__":
    success = test_export_functionality()
    if success:
        print("\n✅ Export functionality test PASSED")
    else:
        print("\n❌ Export functionality test FAILED")
    sys.exit(0 if success else 1)