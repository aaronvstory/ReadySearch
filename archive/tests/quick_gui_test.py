#!/usr/bin/env python3
"""
Quick GUI Test - Basic validation
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_basic_imports():
    """Test basic imports work"""
    print("🧪 Testing basic imports...")
    
    try:
        from readysearch_gui import ReadySearchGUI, ModernStyle, GUISearchResult
        from readysearch_automation.input_loader import SearchRecord
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_search_record():
    """Test SearchRecord"""
    print("📋 Testing SearchRecord...")
    
    try:
        from readysearch_automation.input_loader import SearchRecord
        
        record = SearchRecord(name="Andro Cutuk", birth_year=1975)
        assert record.name == "Andro Cutuk"
        assert record.birth_year == 1975
        
        print("✅ SearchRecord working")
        return True
    except Exception as e:
        print(f"❌ SearchRecord failed: {e}")
        return False

def test_gui_result():
    """Test GUISearchResult"""
    print("📊 Testing GUISearchResult...")
    
    try:
        from readysearch_gui import GUISearchResult
        from datetime import datetime
        
        result = GUISearchResult(
            name="Andro Cutuk",
            status="Match",
            search_duration=6.2,
            matches_found=1,
            exact_matches=1,
            partial_matches=0,
            match_category="EXACT MATCH",
            match_reasoning="Found exact match",
            detailed_results=[{"test": "data"}],
            timestamp=datetime.now().isoformat(),
            birth_year=1975
        )
        
        assert result.name == "Andro Cutuk"
        assert result.birth_year == 1975
        
        print("✅ GUISearchResult working")
        return True
    except Exception as e:
        print(f"❌ GUISearchResult failed: {e}")
        return False

def test_modern_style():
    """Test ModernStyle"""
    print("🎨 Testing ModernStyle...")
    
    try:
        from readysearch_gui import ModernStyle
        
        # Test key colors exist
        assert hasattr(ModernStyle, 'COLORS')
        assert 'primary' in ModernStyle.COLORS
        assert 'background' in ModernStyle.COLORS
        
        # Test key fonts exist
        assert hasattr(ModernStyle, 'FONTS')
        assert 'title' in ModernStyle.FONTS
        assert 'body' in ModernStyle.FONTS
        
        print("✅ ModernStyle working")
        return True
    except Exception as e:
        print(f"❌ ModernStyle failed: {e}")
        return False

def run_quick_test():
    """Run quick test suite"""
    print("🧪 ReadySearch GUI - Quick Test")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("SearchRecord", test_search_record),
        ("GUISearchResult", test_gui_result),
        ("ModernStyle", test_modern_style),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 QUICK TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 BASIC FUNCTIONALITY WORKING!")
        return True
    else:
        print(f"\n⚠️ {total - passed} basic tests failed")
        return False

if __name__ == "__main__":
    success = run_quick_test()
    sys.exit(0 if success else 1)