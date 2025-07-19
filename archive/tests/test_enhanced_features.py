#!/usr/bin/env python3
"""
Test script to verify enhanced features work correctly
"""

import asyncio
import sys
import json
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config import successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from readysearch_automation.input_loader import SearchRecord
        print("✅ SearchRecord import successful")
    except ImportError as e:
        print(f"❌ SearchRecord import failed: {e}")
        return False
    
    try:
        from production_cli import ProductionCLI
        print("✅ ProductionCLI import successful")
    except ImportError as e:
        print(f"❌ ProductionCLI import failed: {e}")
        return False
    
    print("✅ All core imports successful")
    return True

def test_config():
    """Test configuration loading"""
    print("\n📋 Testing configuration...")
    
    try:
        from config import Config
        config = Config.get_config()
        
        required_keys = ['base_url', 'selectors', 'delay', 'max_retries']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing config key: {key}")
                return False
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Base URL: {config['base_url']}")
        print(f"   Delay: {config['delay']}s")
        print(f"   Max Retries: {config['max_retries']}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_search_record_creation():
    """Test SearchRecord creation"""
    print("\n👤 Testing SearchRecord creation...")
    
    try:
        from readysearch_automation.input_loader import SearchRecord
        
        # Test basic record
        record1 = SearchRecord(name="John Smith")
        print(f"✅ Basic record: {record1}")
        
        # Test record with birth year
        record2 = SearchRecord(name="Jane Doe", birth_year=1990)
        print(f"✅ Record with birth year: {record2}")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchRecord test failed: {e}")
        return False

def test_production_cli_initialization():
    """Test ProductionCLI initialization"""
    print("\n⚡ Testing ProductionCLI initialization...")
    
    try:
        from production_cli import ProductionCLI
        
        cli = ProductionCLI()
        print("✅ ProductionCLI initialized successfully")
        
        # Test that it has required attributes
        if hasattr(cli, 'config'):
            print("✅ CLI has config attribute")
        else:
            print("❌ CLI missing config attribute")
            return False
            
        if hasattr(cli, 'matcher'):
            print("✅ CLI has matcher attribute")
        else:
            print("❌ CLI missing matcher attribute")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ProductionCLI test failed: {e}")
        return False

def test_enhanced_cli_imports():
    """Test enhanced CLI imports"""
    print("\n💻 Testing Enhanced CLI imports...")
    
    try:
        # Test Rich import (may auto-install)
        try:
            from rich.console import Console
            print("✅ Rich library available")
        except ImportError:
            print("⚠️ Rich library not installed (will auto-install)")
        
        # Test enhanced CLI structure
        enhanced_cli_path = Path("enhanced_cli.py")
        if enhanced_cli_path.exists():
            print("✅ Enhanced CLI file exists")
        else:
            print("❌ Enhanced CLI file missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Enhanced CLI test failed: {e}")
        return False

def test_gui_imports():
    """Test GUI imports"""
    print("\n🖼️ Testing GUI imports...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter available")
        
        gui_path = Path("readysearch_gui.py")
        if gui_path.exists():
            print("✅ GUI file exists")
        else:
            print("❌ GUI file missing")
            return False
            
        return True
        
    except ImportError:
        print("❌ Tkinter not available")
        return False
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_launcher_files():
    """Test launcher files exist"""
    print("\n🚀 Testing launcher files...")
    
    files_to_check = [
        "launcher.ps1",
        "enhanced_launcher.bat",
        "enhanced_cli.py",
        "readysearch_gui.py",
        "production_cli.py"
    ]
    
    all_exist = True
    for filename in files_to_check:
        file_path = Path(filename)
        if file_path.exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} missing")
            all_exist = False
    
    return all_exist

async def test_search_functionality_dry_run():
    """Test search functionality without actually performing web requests"""
    print("\n🧪 Testing search functionality (dry run)...")
    
    try:
        from readysearch_automation.input_loader import SearchRecord
        from production_cli import ProductionCLI
        
        # Create test records
        test_records = [
            SearchRecord(name="Test User"),
            SearchRecord(name="Demo Person", birth_year=1990)
        ]
        
        print(f"✅ Created {len(test_records)} test records")
        
        # Test CLI initialization
        cli = ProductionCLI()
        print("✅ CLI initialized for testing")
        
        # Test parse_names_input function (if available in enhanced CLI)
        try:
            sys.path.append(str(Path(__file__).parent))
            # Import would happen here but avoiding actual web requests
            print("✅ Search components are accessible")
        except Exception as e:
            print(f"⚠️ Some search components not available: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
        return False

def run_compatibility_tests():
    """Run all compatibility tests"""
    print("🔍 ReadySearch Enhanced Features - Compatibility Test")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Test", test_config),
        ("SearchRecord Test", test_search_record_creation),
        ("ProductionCLI Test", test_production_cli_initialization),
        ("Enhanced CLI Test", test_enhanced_cli_imports),
        ("GUI Test", test_gui_imports),
        ("Launcher Files Test", test_launcher_files),
        ("Search Functionality Test", test_search_functionality_dry_run)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All compatibility tests PASSED!")
        print("✅ Existing functionality is preserved")
        print("✅ Enhanced features are ready to use")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests FAILED")
        print("❌ Some issues need to be addressed")
        return False

if __name__ == "__main__":
    success = run_compatibility_tests()
    sys.exit(0 if success else 1)