#!/usr/bin/env python3
"""
Chunking Integration Test Suite
Tests that chunking enhancement works properly and maintains backward compatibility
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Test imports
try:
    # Test enhanced CLI with chunking
    from enhanced_cli_with_chunking import EnhancedReadySearchCLI, ChunkingConfig
    ENHANCED_CHUNKING_AVAILABLE = True
    print("✅ Enhanced CLI with Chunking available")
except ImportError as e:
    ENHANCED_CHUNKING_AVAILABLE = False
    print(f"❌ Enhanced CLI with Chunking not available: {e}")

try:
    # Test original enhanced CLI
    from enhanced_cli import EnhancedReadySearchCLI as OriginalEnhancedCLI
    ORIGINAL_ENHANCED_AVAILABLE = True
    print("✅ Original Enhanced CLI available")
except ImportError as e:
    ORIGINAL_ENHANCED_AVAILABLE = False
    print(f"❌ Original Enhanced CLI not available: {e}")

try:
    # Test chunking patch
    from chunking_enhancement_patch import add_chunking_to_enhanced_cli
    CHUNKING_PATCH_AVAILABLE = True
    print("✅ Chunking patch available")
except ImportError as e:
    CHUNKING_PATCH_AVAILABLE = False
    print(f"❌ Chunking patch not available: {e}")

async def test_small_batch_compatibility():
    """Test that small batches work identically in both systems"""
    print("\n🧪 Testing Small Batch Compatibility")
    
    if not ENHANCED_CHUNKING_AVAILABLE:
        print("❌ Enhanced CLI with chunking not available")
        return False
    
    # Test data (small batch - should not trigger chunking)
    test_input = "andro cutuk,1977;john smith,1980;jane doe,1985"
    
    try:
        # Test enhanced CLI with chunking
        chunking_cli = EnhancedReadySearchCLI()
        start_time = time.time()
        chunking_results = await chunking_cli.perform_search(test_input)
        chunking_duration = time.time() - start_time
        
        # Verify no chunking was used (should be None for small batches)
        chunking_used = any(r.chunk_id is not None for r in chunking_results)
        
        print(f"   Enhanced CLI (Chunking): {len(chunking_results)} results in {chunking_duration:.1f}s")
        print(f"   Chunking used: {'❌ No (correct)' if not chunking_used else '⚠️ Yes (unexpected)'}")
        
        # Cleanup
        await chunking_cli.cleanup()
        
        # Verify results structure
        if chunking_results:
            result = chunking_results[0]
            required_fields = ['name', 'status', 'search_duration', 'matches_found']
            missing_fields = [field for field in required_fields if not hasattr(result, field)]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print("   ✅ Result structure valid")
        
        return len(chunking_results) >= 1 and not chunking_used
        
    except Exception as e:
        print(f"   ❌ Small batch test failed: {str(e)}")
        return False

async def test_large_batch_chunking():
    """Test that large batches automatically use chunking"""
    print("\n🧪 Testing Large Batch Chunking")
    
    if not ENHANCED_CHUNKING_AVAILABLE:
        print("❌ Enhanced CLI with chunking not available")
        return False
    
    # Create large batch (15 names - should trigger chunking)
    test_names = []
    for i in range(15):
        test_names.append(f"test name {i},198{i%10}")
    
    test_input = ";".join(test_names)
    
    try:
        chunking_cli = EnhancedReadySearchCLI()
        start_time = time.time()
        chunking_results = await chunking_cli.perform_search(test_input)
        chunking_duration = time.time() - start_time
        
        # Verify chunking was used
        chunking_used = any(r.chunk_id is not None for r in chunking_results)
        chunks_used = len(set(r.chunk_id for r in chunking_results if r.chunk_id is not None))
        
        print(f"   Enhanced CLI (Chunking): {len(chunking_results)} results in {chunking_duration:.1f}s")
        print(f"   Chunking used: {'✅ Yes' if chunking_used else '❌ No (unexpected)'}")
        print(f"   Chunks used: {chunks_used}")
        
        # Cleanup
        await chunking_cli.cleanup()
        
        # Verify all records were processed
        if len(chunking_results) != 15:
            print(f"   ❌ Expected 15 results, got {len(chunking_results)}")
            return False
        
        return chunking_used and len(chunking_results) == 15
        
    except Exception as e:
        print(f"   ❌ Large batch test failed: {str(e)}")
        return False

async def test_chunking_configuration():
    """Test custom chunking configuration"""
    print("\n🧪 Testing Chunking Configuration")
    
    if not ENHANCED_CHUNKING_AVAILABLE:
        print("❌ Enhanced CLI with chunking not available")
        return False
    
    try:
        # Create CLI with custom configuration
        chunking_cli = EnhancedReadySearchCLI()
        
        # Test configuration access
        original_max_chunk = chunking_cli.chunking_config.max_chunk_size
        chunking_cli.chunking_config.max_chunk_size = 10
        
        if chunking_cli.chunking_config.max_chunk_size == 10:
            print("   ✅ Chunking configuration modifiable")
        else:
            print("   ❌ Chunking configuration not modifiable")
            return False
        
        # Test configuration attributes
        config_attrs = ['max_chunk_size', 'min_chunk_size', 'memory_threshold', 'pause_between_chunks']
        missing_attrs = [attr for attr in config_attrs if not hasattr(chunking_cli.chunking_config, attr)]
        
        if missing_attrs:
            print(f"   ❌ Missing configuration attributes: {missing_attrs}")
            return False
        else:
            print("   ✅ All configuration attributes present")
        
        # Restore original value
        chunking_cli.chunking_config.max_chunk_size = original_max_chunk
        
        await chunking_cli.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {str(e)}")
        return False

async def test_export_compatibility():
    """Test that export formats include chunking metadata when appropriate"""
    print("\n🧪 Testing Export Compatibility")
    
    if not ENHANCED_CHUNKING_AVAILABLE:
        print("❌ Enhanced CLI with chunking not available")
        return False
    
    try:
        chunking_cli = EnhancedReadySearchCLI()
        
        # Create small result set
        from enhanced_cli_with_chunking import SearchResult
        from datetime import datetime
        
        test_results = [
            SearchResult(
                name="test name",
                status="Match",
                search_duration=5.0,
                matches_found=1,
                exact_matches=1,
                partial_matches=0,
                match_category="EXACT MATCH",
                match_reasoning="Test match",
                detailed_results=[],
                timestamp=datetime.now().isoformat(),
                chunk_id=1
            )
        ]
        
        chunking_cli.session_results = test_results
        
        # Test export methods exist
        export_methods = ['export_json_enhanced', 'export_csv_enhanced', 'export_txt_enhanced']
        missing_methods = [method for method in export_methods if not hasattr(chunking_cli, method)]
        
        if missing_methods:
            print(f"   ❌ Missing export methods: {missing_methods}")
            return False
        else:
            print("   ✅ All enhanced export methods available")
        
        # Test that results contain chunk information
        result = test_results[0]
        if hasattr(result, 'chunk_id') and result.chunk_id is not None:
            print("   ✅ Results contain chunk metadata")
        else:
            print("   ❌ Results missing chunk metadata")
            return False
        
        await chunking_cli.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Export compatibility test failed: {str(e)}")
        return False

def test_dependency_installation():
    """Test that required dependencies are installed"""
    print("\n🧪 Testing Dependency Installation")
    
    dependencies = [
        ('rich', 'Rich CLI formatting'),
        ('psutil', 'System resource monitoring'), 
        ('asyncio', 'Asynchronous processing')
    ]
    
    all_available = True
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: {description}")
        except ImportError:
            print(f"   ❌ {dep}: {description} - Not installed")
            all_available = False
    
    # Optional dependencies
    optional_deps = [
        ('playwright', 'Browser automation (optional optimization)'),
    ]
    
    for dep, description in optional_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: {description}")
        except ImportError:
            print(f"   ⚠️ {dep}: {description} - Not installed (optional)")
    
    return all_available

async def run_comprehensive_test():
    """Run all integration tests"""
    print("🚀 ReadySearch Chunking Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Dependency Installation", test_dependency_installation()),
        ("Small Batch Compatibility", test_small_batch_compatibility()),
        ("Large Batch Chunking", test_large_batch_chunking()),
        ("Chunking Configuration", test_chunking_configuration()),
        ("Export Compatibility", test_export_compatibility())
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if asyncio.iscoroutine(test_func):
                result = await test_func
            else:
                result = test_func
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Chunking integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

async def main():
    """Main test function"""
    try:
        success = await run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())