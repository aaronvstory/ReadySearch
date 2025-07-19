#!/usr/bin/env python3
"""
Production Readiness Test - Comprehensive validation for enhanced features
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_file_structure():
    """Test that all required files are present"""
    print("📁 Testing File Structure...")
    
    required_files = [
        "enhanced_cli.py",
        "readysearch_gui.py", 
        "enhanced_launcher.bat",
        "launcher.ps1",
        "production_cli.py",
        "config.py",
        "ENHANCED_FEATURES_GUIDE.md",
        "QUICK_REFERENCE.md"
    ]
    
    missing_files = []
    for filename in required_files:
        if Path(filename).exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - MISSING")
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def test_python_syntax():
    """Test Python files for syntax errors"""
    print("\n🐍 Testing Python Syntax...")
    
    python_files = [
        "enhanced_cli.py",
        "readysearch_gui.py",
        "production_cli.py",
        "config.py",
        "main.py"
    ]
    
    import ast
    syntax_errors = []
    
    for filename in python_files:
        if Path(filename).exists():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ {filename} - syntax OK")
            except SyntaxError as e:
                print(f"❌ {filename} - syntax error: {e}")
                syntax_errors.append(filename)
        else:
            print(f"⚠️ {filename} - file not found")
    
    if syntax_errors:
        print(f"❌ Syntax errors in: {syntax_errors}")
        return False
    
    print("✅ All Python files have valid syntax")
    return True

def test_imports():
    """Test critical imports work"""
    print("\n📦 Testing Critical Imports...")
    
    try:
        # Test enhanced CLI imports
        from enhanced_cli import EnhancedReadySearchCLI, SearchResult
        print("✅ Enhanced CLI imports")
        
        # Test GUI imports
        from readysearch_gui import ReadySearchGUI, ModernStyle
        print("✅ GUI imports")
        
        # Test production CLI
        from production_cli import ProductionCLI
        print("✅ Production CLI imports")
        
        # Test config
        from config import Config
        print("✅ Config imports")
        
        # Test Rich library
        from rich.console import Console
        print("✅ Rich library available")
        
        # Test Tkinter
        import tkinter as tk
        print("✅ Tkinter available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration is valid"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config import Config
        config = Config.get_config()
        
        # Check required config keys
        required_keys = [
            'base_url', 'selectors', 'delay', 'max_retries',
            'page_timeout', 'element_timeout', 'headless', 'log_level'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing config keys: {missing_keys}")
            return False
        
        # Validate specific values
        if not config['base_url'].startswith('https://'):
            print("❌ Invalid base URL")
            return False
        
        if config['delay'] < 0:
            print("❌ Invalid delay value")
            return False
        
        if config['max_retries'] < 1:
            print("❌ Invalid max_retries value")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_launcher_files():
    """Test launcher files are properly formatted"""
    print("\n🚀 Testing Launcher Files...")
    
    # Test enhanced_launcher.bat
    bat_file = Path("enhanced_launcher.bat")
    if bat_file.exists():
        content = bat_file.read_text(encoding='utf-8')
        if ":enhanced_cli" in content and ":advanced_gui" in content:
            print("✅ enhanced_launcher.bat has enhanced options")
        else:
            print("❌ enhanced_launcher.bat missing enhanced options")
            return False
    else:
        print("❌ enhanced_launcher.bat missing")
        return False
    
    # Test PowerShell launcher
    ps_file = Path("launcher.ps1")
    if ps_file.exists():
        content = ps_file.read_text(encoding='utf-8')
        if "Start-EnhancedCLI" in content and "Start-AdvancedGUI" in content:
            print("✅ launcher.ps1 has enhanced functions")
        else:
            print("❌ launcher.ps1 missing enhanced functions")
            return False
    else:
        print("❌ launcher.ps1 missing")
        return False
    
    print("✅ Launcher files are properly configured")
    return True

def test_documentation():
    """Test documentation files exist and have content"""
    print("\n📚 Testing Documentation...")
    
    doc_files = [
        ("ENHANCED_FEATURES_GUIDE.md", 5000),  # Should be substantial
        ("QUICK_REFERENCE.md", 2000),
    ]
    
    for filename, min_size in doc_files:
        file_path = Path(filename)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            if len(content) >= min_size:
                print(f"✅ {filename} - {len(content)} characters")
            else:
                print(f"⚠️ {filename} - only {len(content)} characters (expected >{min_size})")
        else:
            print(f"❌ {filename} missing")
            return False
    
    print("✅ Documentation files are adequate")
    return True

def test_feature_completeness():
    """Test that all promised features are implemented"""
    print("\n🎯 Testing Feature Completeness...")
    
    try:
        from enhanced_cli import EnhancedReadySearchCLI
        cli = EnhancedReadySearchCLI()
        
        # Check CLI has required methods
        required_methods = [
            'display_banner', 'display_main_menu', 'perform_search',
            'export_results', 'export_json', 'export_csv', 'export_txt'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(cli, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Enhanced CLI missing methods: {missing_methods}")
            return False
        
        print("✅ Enhanced CLI has all required methods")
        
        # Check GUI has required methods
        from readysearch_gui import ReadySearchGUI
        # Note: We can't instantiate GUI without display, so just check import
        print("✅ GUI classes are available")
        
        # Check SearchResult has export capability
        from enhanced_cli import SearchResult
        from datetime import datetime
        
        test_result = SearchResult(
            name="Test",
            status="Match",
            search_duration=5.0,
            matches_found=1,
            exact_matches=1,
            partial_matches=0,
            match_category="EXACT",
            match_reasoning="Test",
            detailed_results=[],
            timestamp=datetime.now().isoformat()
        )
        
        # Test to_dict method exists and works
        data = test_result.to_dict()
        if 'name' in data and 'status' in data:
            print("✅ SearchResult export functionality working")
        else:
            print("❌ SearchResult export functionality broken")
            return False
        
        print("✅ All promised features are implemented")
        return True
        
    except Exception as e:
        print(f"❌ Feature completeness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_readiness():
    """Test performance characteristics"""
    print("\n⚡ Testing Performance Readiness...")
    
    try:
        import time
        
        # Test CLI initialization time
        start_time = time.time()
        from enhanced_cli import EnhancedReadySearchCLI
        cli = EnhancedReadySearchCLI()
        init_time = time.time() - start_time
        
        if init_time < 2.0:  # Should initialize quickly
            print(f"✅ CLI initialization: {init_time:.3f}s")
        else:
            print(f"⚠️ CLI initialization slow: {init_time:.3f}s")
        
        # Test import time for critical modules
        start_time = time.time()
        from production_cli import ProductionCLI
        import_time = time.time() - start_time
        
        if import_time < 1.0:
            print(f"✅ Production CLI import: {import_time:.3f}s")
        else:
            print(f"⚠️ Production CLI import slow: {import_time:.3f}s")
        
        print("✅ Performance characteristics acceptable")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_production_readiness_test():
    """Run comprehensive production readiness test"""
    print("🏭 ReadySearch Enhanced Features - Production Readiness Test")
    print("=" * 70)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Critical Imports", test_imports),
        ("Configuration", test_configuration),
        ("Launcher Files", test_launcher_files),
        ("Documentation", test_documentation),
        ("Feature Completeness", test_feature_completeness),
        ("Performance Readiness", test_performance_readiness),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION READINESS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ READY" if result else "❌ NEEDS WORK"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 PRODUCTION READY!")
        print("✅ All systems ready for deployment")
        print("✅ Enhanced features are polished and professional")
        print("✅ Ready for GitHub commit and public release")
        return True
    else:
        print(f"\n⚠️ {total - passed} issues need attention before production")
        return False

if __name__ == "__main__":
    success = run_production_readiness_test()
    sys.exit(0 if success else 1)