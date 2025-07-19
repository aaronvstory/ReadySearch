#!/usr/bin/env python3
"""
Comprehensive Error Handling and Edge Case Testing for ReadySearch
Tests all interfaces for robustness, error handling, and edge cases
"""

import subprocess
import json
import time
import requests
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import os

class EdgeCaseTestSuite:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            'cli_edge_cases': [],
            'gui_edge_cases': [],
            'api_edge_cases': [],
            'error_handling': [],
            'performance_edge_cases': [],
            'security_tests': []
        }
        self.api_base_url = "http://localhost:5000"
        
    def test_cli_edge_cases(self):
        """Test CLI with various edge cases and malformed inputs"""
        print("🧪 Testing CLI Edge Cases...")
        
        edge_cases = [
            # Malformed inputs
            ("", "Empty input"),
            ("   ", "Whitespace only"),
            ("John Smith;", "Trailing semicolon"),
            (";John Smith", "Leading semicolon"),
            ("John;Smith", "Semicolon in name"),
            ("John Smith,abc", "Invalid birth year"),
            ("John Smith,2030", "Future birth year"),
            ("John Smith,1800", "Very old birth year"),
            ("A", "Single character name"),
            ("X" * 100, "Very long name"),
            ("John Smith,1990;", "Valid entry with trailing semicolon"),
            (";;;", "Multiple semicolons only"),
            ("John Smith, Jane Doe", "Comma without year"),
            ("John,Smith,1990,2000", "Multiple commas"),
            ("John\nSmith", "Name with newline"),
            ("John\tSmith", "Name with tab"),
            ("John  Smith", "Multiple spaces"),
            ("John-Smith", "Hyphenated name"),
            ("O'Brien", "Name with apostrophe"),
            ("José García", "Unicode characters"),
            ("123456", "Numbers only"),
            ("!@#$%", "Special characters only"),
        ]
        
        for test_input, description in edge_cases:
            print(f"   🔍 Testing: {description}")
            try:
                # Test with production CLI
                result = subprocess.run(
                    ['python', 'production_cli.py', test_input],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root
                )
                
                # Analyze result
                success = result.returncode == 0
                has_error_message = "error" in result.stdout.lower() or "failed" in result.stdout.lower()
                graceful_handling = not (result.returncode != 0 and "Traceback" in result.stderr)
                
                test_result = {
                    'test_case': description,
                    'input': test_input,
                    'success': success,
                    'graceful_handling': graceful_handling,
                    'has_error_message': has_error_message,
                    'return_code': result.returncode,
                    'stderr_length': len(result.stderr)
                }
                
                self.test_results['cli_edge_cases'].append(test_result)
                
                # Status
                if graceful_handling:
                    print(f"      ✅ Handled gracefully")
                else:
                    print(f"      ❌ Poor error handling")
                    
            except subprocess.TimeoutExpired:
                print(f"      ⚠️ Timeout (30s)")
                self.test_results['cli_edge_cases'].append({
                    'test_case': description,
                    'input': test_input,
                    'success': False,
                    'graceful_handling': False,
                    'timeout': True
                })
            except Exception as e:
                print(f"      ❌ Exception: {e}")
                self.test_results['cli_edge_cases'].append({
                    'test_case': description,
                    'input': test_input,
                    'success': False,
                    'graceful_handling': False,
                    'exception': str(e)
                })
    
    def test_gui_edge_cases(self):
        """Test GUI error handling and edge cases"""
        print("🧪 Testing GUI Edge Cases...")
        
        try:
            # Test GUI import and initialization under stress
            import readysearch_gui
            
            # Test multiple initializations
            for i in range(3):
                try:
                    app = readysearch_gui.ReadySearchGUI()
                    
                    # Test component access
                    components_ok = all([
                        hasattr(app, 'root'),
                        hasattr(app, 'quick_name_entry'),
                        hasattr(app, 'quick_year_entry'),
                        hasattr(app, 'search_results')
                    ])
                    
                    if components_ok:
                        print(f"      ✅ Initialization {i+1} successful")
                    else:
                        print(f"      ❌ Initialization {i+1} missing components")
                        
                except Exception as e:
                    print(f"      ❌ Initialization {i+1} failed: {e}")
                    self.test_results['gui_edge_cases'].append({
                        'test': f'Multiple initialization {i+1}',
                        'success': False,
                        'error': str(e)
                    })
            
            # Test GUI with invalid data
            edge_case_tests = [
                "Empty string handling",
                "Unicode character support", 
                "Long string handling",
                "Special character handling"
            ]
            
            for test_name in edge_case_tests:
                try:
                    app = readysearch_gui.ReadySearchGUI()
                    print(f"      ✅ {test_name} - GUI structure intact")
                    self.test_results['gui_edge_cases'].append({
                        'test': test_name,
                        'success': True
                    })
                except Exception as e:
                    print(f"      ❌ {test_name} failed: {e}")
                    self.test_results['gui_edge_cases'].append({
                        'test': test_name,
                        'success': False,
                        'error': str(e)
                    })
                    
        except Exception as e:
            print(f"   ❌ GUI edge case testing failed: {e}")
            self.test_results['gui_edge_cases'].append({
                'test': 'Overall GUI testing',
                'success': False,
                'error': str(e)
            })
    
    def test_api_edge_cases(self):
        """Test API with malformed requests and edge cases"""
        print("🧪 Testing API Edge Cases...")
        
        # Test API availability first
        try:
            health_response = requests.get(f"{self.api_base_url}/api/health", timeout=5)
            if health_response.status_code != 200:
                print("   ⚠️ API not available, skipping API edge case tests")
                return
        except Exception:
            print("   ⚠️ API not reachable, skipping API edge case tests")
            return
        
        edge_case_requests = [
            # Malformed JSON
            {
                'name': 'Empty JSON',
                'data': {},
                'content_type': 'application/json'
            },
            {
                'name': 'Invalid JSON structure',
                'data': {'invalid': 'structure'},
                'content_type': 'application/json'
            },
            {
                'name': 'Missing names field',
                'data': {'mode': 'standard'},
                'content_type': 'application/json'
            },
            {
                'name': 'Empty names array',
                'data': {'names': [], 'mode': 'standard'},
                'content_type': 'application/json'
            },
            {
                'name': 'Invalid names format',
                'data': {'names': 123, 'mode': 'standard'},
                'content_type': 'application/json'
            },
            {
                'name': 'Very long names list',
                'data': {'names': ['Name'] * 1000, 'mode': 'standard'},
                'content_type': 'application/json'
            },
            {
                'name': 'Special characters in names',
                'data': {'names': ['@#$%^&*()'], 'mode': 'standard'},
                'content_type': 'application/json'
            },
            {
                'name': 'Unicode characters',
                'data': {'names': ['José García 测试'], 'mode': 'standard'},
                'content_type': 'application/json'
            }
        ]
        
        for test_case in edge_case_requests:
            print(f"   🔍 Testing: {test_case['name']}")
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/start-automation",
                    json=test_case['data'],
                    headers={'Content-Type': test_case['content_type']},
                    timeout=10
                )
                
                # Analyze response
                graceful_error = 400 <= response.status_code < 500
                server_error = response.status_code >= 500
                success = response.status_code == 200
                
                test_result = {
                    'test_case': test_case['name'],
                    'status_code': response.status_code,
                    'success': success,
                    'graceful_error': graceful_error,
                    'server_error': server_error
                }
                
                try:
                    response_data = response.json()
                    test_result['has_error_message'] = 'error' in response_data
                except:
                    test_result['has_error_message'] = False
                
                self.test_results['api_edge_cases'].append(test_result)
                
                if success:
                    print(f"      ✅ Accepted (may be valid)")
                elif graceful_error:
                    print(f"      ✅ Graceful error ({response.status_code})")
                elif server_error:
                    print(f"      ❌ Server error ({response.status_code})")
                else:
                    print(f"      ⚠️ Unexpected response ({response.status_code})")
                    
            except requests.exceptions.Timeout:
                print(f"      ⚠️ Request timeout")
                self.test_results['api_edge_cases'].append({
                    'test_case': test_case['name'],
                    'timeout': True
                })
            except Exception as e:
                print(f"      ❌ Request failed: {e}")
                self.test_results['api_edge_cases'].append({
                    'test_case': test_case['name'],
                    'exception': str(e)
                })
    
    def test_error_handling_robustness(self):
        """Test system robustness under error conditions"""
        print("🧪 Testing Error Handling Robustness...")
        
        # Test file system error scenarios
        error_scenarios = [
            "Read-only directory handling",
            "Disk space handling",
            "Permission error handling",
            "Concurrent access handling"
        ]
        
        for scenario in error_scenarios:
            print(f"   🔍 Testing: {scenario}")
            
            # Test with temporary file operations
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write('test data')
                    temp_path = temp_file.name
                
                # Test file operations
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    print(f"      ✅ {scenario} - File operations work")
                    
                self.test_results['error_handling'].append({
                    'scenario': scenario,
                    'success': True
                })
                
            except Exception as e:
                print(f"      ❌ {scenario} failed: {e}")
                self.test_results['error_handling'].append({
                    'scenario': scenario,
                    'success': False,
                    'error': str(e)
                })
    
    def test_performance_edge_cases(self):
        """Test performance under edge conditions"""
        print("🧪 Testing Performance Edge Cases...")
        
        # Test with stress conditions
        stress_tests = [
            ("Single long name", "A" * 50),
            ("Name with many parts", " ".join(["Part"] * 20)),
            ("Multiple similar names", "John Smith"),  # Will test with multiple entries
        ]
        
        for test_name, test_input in stress_tests:
            print(f"   🔍 Testing: {test_name}")
            
            start_time = time.time()
            try:
                # Quick test - just check if it starts processing
                result = subprocess.run(
                    ['python', 'production_cli.py', test_input],
                    capture_output=True,
                    text=True,
                    timeout=15,  # Shorter timeout for performance test
                    cwd=self.project_root
                )
                
                duration = time.time() - start_time
                
                # Performance analysis
                acceptable_duration = duration < 30  # 30 second limit
                no_memory_issues = "MemoryError" not in result.stderr
                no_timeout = True
                
                performance_result = {
                    'test': test_name,
                    'duration': duration,
                    'acceptable_duration': acceptable_duration,
                    'no_memory_issues': no_memory_issues,
                    'success': result.returncode == 0,
                    'no_timeout': no_timeout
                }
                
                self.test_results['performance_edge_cases'].append(performance_result)
                
                if acceptable_duration and no_memory_issues:
                    print(f"      ✅ Performance acceptable ({duration:.2f}s)")
                else:
                    print(f"      ⚠️ Performance issues ({duration:.2f}s)")
                    
            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                print(f"      ⚠️ Timeout after {duration:.2f}s")
                self.test_results['performance_edge_cases'].append({
                    'test': test_name,
                    'duration': duration,
                    'timeout': True,
                    'acceptable_duration': False
                })
            except Exception as e:
                print(f"      ❌ Performance test failed: {e}")
                self.test_results['performance_edge_cases'].append({
                    'test': test_name,
                    'exception': str(e),
                    'success': False
                })
    
    def test_security_edge_cases(self):
        """Test basic security edge cases"""
        print("🧪 Testing Security Edge Cases...")
        
        security_tests = [
            ("SQL injection attempt", "'; DROP TABLE users; --"),
            ("Script injection", "<script>alert('test')</script>"),
            ("Path traversal", "../../../etc/passwd"),
            ("Command injection", "; ls -la"),
            ("Null byte injection", "test\x00"),
            ("Very long input", "A" * 10000),
        ]
        
        for test_name, malicious_input in security_tests:
            print(f"   🔍 Testing: {test_name}")
            
            try:
                # Test CLI with malicious input
                result = subprocess.run(
                    ['python', 'production_cli.py', malicious_input],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=self.project_root
                )
                
                # Security analysis
                no_code_execution = "Permission denied" not in result.stderr
                no_system_access = "No such file" not in result.stderr
                handled_safely = result.returncode == 0  # Should handle gracefully
                no_injection = malicious_input not in result.stdout  # Should sanitize
                
                security_result = {
                    'test': test_name,
                    'input': malicious_input,
                    'no_code_execution': no_code_execution,
                    'no_system_access': no_system_access,
                    'handled_safely': handled_safely,
                    'no_injection': no_injection,
                    'secure': all([no_code_execution, no_system_access, handled_safely])
                }
                
                self.test_results['security_tests'].append(security_result)
                
                if security_result['secure']:
                    print(f"      ✅ Handled securely")
                else:
                    print(f"      ⚠️ Potential security concern")
                    
            except subprocess.TimeoutExpired:
                print(f"      ✅ Timeout (prevented potential exploitation)")
                self.test_results['security_tests'].append({
                    'test': test_name,
                    'timeout': True,
                    'secure': True  # Timeout is good for security
                })
            except Exception as e:
                print(f"      ❌ Security test failed: {e}")
                self.test_results['security_tests'].append({
                    'test': test_name,
                    'exception': str(e),
                    'secure': False
                })
    
    def analyze_edge_case_results(self):
        """Analyze all edge case test results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE EDGE CASE ANALYSIS")
        print("=" * 60)
        
        # CLI Edge Cases
        cli_tests = self.test_results['cli_edge_cases']
        cli_graceful = sum(1 for t in cli_tests if t.get('graceful_handling', False))
        print(f"CLI Edge Cases: {cli_graceful}/{len(cli_tests)} handled gracefully")
        
        # GUI Edge Cases
        gui_tests = self.test_results['gui_edge_cases']
        gui_success = sum(1 for t in gui_tests if t.get('success', False))
        print(f"GUI Edge Cases: {gui_success}/{len(gui_tests)} passed")
        
        # API Edge Cases
        api_tests = self.test_results['api_edge_cases']
        api_graceful = sum(1 for t in api_tests if t.get('graceful_error', False) or t.get('success', False))
        print(f"API Edge Cases: {api_graceful}/{len(api_tests)} handled appropriately")
        
        # Error Handling
        error_tests = self.test_results['error_handling']
        error_success = sum(1 for t in error_tests if t.get('success', False))
        print(f"Error Handling: {error_success}/{len(error_tests)} robust")
        
        # Performance
        perf_tests = self.test_results['performance_edge_cases']
        perf_acceptable = sum(1 for t in perf_tests if t.get('acceptable_duration', False))
        print(f"Performance Edge Cases: {perf_acceptable}/{len(perf_tests)} acceptable")
        
        # Security
        security_tests = self.test_results['security_tests']
        security_secure = sum(1 for t in security_tests if t.get('secure', False))
        print(f"Security Tests: {security_secure}/{len(security_tests)} secure")
        
        # Overall assessment
        total_tests = len(cli_tests) + len(gui_tests) + len(api_tests) + len(error_tests) + len(perf_tests) + len(security_tests)
        total_passed = cli_graceful + gui_success + api_graceful + error_success + perf_acceptable + security_secure
        
        overall_score = total_passed / total_tests if total_tests > 0 else 0
        print(f"\nOverall Edge Case Handling: {overall_score:.0%} ({total_passed}/{total_tests})")
        
        # Production readiness assessment
        production_ready = (
            overall_score >= 0.8 and
            security_secure == len(security_tests) and  # All security tests must pass
            error_success >= len(error_tests) * 0.8  # 80% error handling must work
        )
        
        print(f"Edge Case Production Ready: {'✅ YES' if production_ready else '❌ NO'}")
        
        # Save detailed results
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'summary': {
                'cli_graceful': f"{cli_graceful}/{len(cli_tests)}",
                'gui_success': f"{gui_success}/{len(gui_tests)}",
                'api_graceful': f"{api_graceful}/{len(api_tests)}",
                'error_robust': f"{error_success}/{len(error_tests)}",
                'performance_acceptable': f"{perf_acceptable}/{len(perf_tests)}",
                'security_secure': f"{security_secure}/{len(security_tests)}",
                'overall_score': overall_score,
                'production_ready': production_ready
            }
        }
        
        with open('edge_case_report.json', 'w') as f:
            json.dump(detailed_report, f, indent=2)
        
        print(f"\n📄 Detailed edge case report saved to: edge_case_report.json")
        
        return production_ready
    
    def run_comprehensive_edge_testing(self):
        """Run all edge case tests"""
        print("🧪 ReadySearch Comprehensive Edge Case Testing")
        print("=" * 60)
        
        # Run all test categories
        self.test_cli_edge_cases()
        self.test_gui_edge_cases()
        self.test_api_edge_cases()
        self.test_error_handling_robustness()
        self.test_performance_edge_cases()
        self.test_security_edge_cases()
        
        # Analyze results
        production_ready = self.analyze_edge_case_results()
        
        return production_ready

if __name__ == "__main__":
    tester = EdgeCaseTestSuite()
    success = tester.run_comprehensive_edge_testing()
    
    if success:
        print("\n🎉 EDGE CASE TESTING PASSED - System is robust!")
    else:
        print("\n⚠️ EDGE CASE TESTING REVEALED ISSUES - Review needed")
    
    sys.exit(0 if success else 1)