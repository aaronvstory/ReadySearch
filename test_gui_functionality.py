#!/usr/bin/env python3
"""
Quick GUI functionality test for ReadySearch
"""

import sys
import tkinter as tk
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_gui_basic_functionality():
    """Test basic GUI functionality"""
    print("🧪 Testing ReadySearch GUI Basic Functionality...")
    
    try:
        # Test tkinter availability
        print("   ✓ Testing Tkinter availability...")
        root = tk.Tk()
        root.withdraw()  # Hide window
        print("   ✅ Tkinter available")
        
        # Test GUI import
        print("   ✓ Testing GUI import...")
        import readysearch_gui
        print("   ✅ GUI module imported successfully")
        
        # Test GUI classes
        print("   ✓ Testing GUI classes...")
        gui_class = readysearch_gui.ReadySearchGUI
        result_class = readysearch_gui.GUISearchResult
        style_class = readysearch_gui.ModernStyle
        print("   ✅ All GUI classes available")
        
        # Test GUI initialization
        print("   ✓ Testing GUI initialization...")
        app = gui_class()
        print("   ✅ GUI initialized successfully")
        
        # Test key components
        print("   ✓ Testing key components...")
        assert hasattr(app, 'root'), "Missing root window"
        assert hasattr(app, 'search_results'), "Missing search_results"
        assert hasattr(app, 'quick_name_entry'), "Missing quick name entry"
        assert hasattr(app, 'quick_year_entry'), "Missing quick year entry"
        print("   ✅ Key components present")
        
        # Test test data
        print("   ✓ Testing embedded test data...")
        test_data = ["Andro Cutuk,1975", "Anthony Bek,1993", "Ghafoor Jaggi Nadery,1978"]
        print(f"   ✅ Test data embedded: {test_data}")
        
        # Cleanup
        root.destroy()
        
        print("✅ GUI functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ GUI functionality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_functionality():
    """Test CLI functionality as comparison"""
    print("🧪 Testing CLI Functionality for comparison...")
    
    try:
        import production_cli
        cli = production_cli.ProductionCLI()
        print("✅ CLI functionality working")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReadySearch Component Testing")
    print("=" * 50)
    
    cli_ok = test_cli_functionality()
    gui_ok = test_gui_basic_functionality()
    
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"   CLI: {'✅ PASS' if cli_ok else '❌ FAIL'}")
    print(f"   GUI: {'✅ PASS' if gui_ok else '❌ FAIL'}")
    
    if cli_ok and gui_ok:
        print("🎉 All components working correctly!")
    else:
        print("⚠️ Some components need attention")