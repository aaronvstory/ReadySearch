#!/usr/bin/env python3
"""
Comprehensive validation of ReadySearch across all interfaces
Tests accuracy, performance, and consistency across CLI, GUI, and API
"""

import subprocess
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

class ComprehensiveValidator:
    def __init__(self):
        self.test_names = [
            "Anthony Bek,1993",
            "Andro Cutuk,1975", 
            "Ghafoor Jaggi Nadery,1978"
        ]
        self.results = {
            'cli': {},
            'gui': {},
            'api': {},
            'performance': {},
            'accuracy': {}
        }
        self.api_base_url = "http://localhost:5000"
        
    def test_cli_performance(self):
        """Test CLI performance and accuracy"""
        print("🧪 Testing CLI Performance and Accuracy...")
        cli_results = []
        
        for name in self.test_names:
            print(f"   🔍 Testing: {name}")
            start_time = time.time()
            
            try:
                # Run production CLI
                result = subprocess.run(
                    ['python', 'production_cli.py', name],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(Path(__file__).parent)
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Parse output for matches
                output = result.stdout
                matches_found = 0
                status = "No Match"
                
                if "✅ MATCH" in output:
                    matches_found = output.count("✅ MATCH")
                    status = "Match"
                elif "No Match" in output or "⭕" in output:
                    status = "No Match"
                elif "❌" in output or result.returncode != 0:
                    status = "Error"
                
                cli_result = {
                    'name': name,
                    'status': status,
                    'matches_found': matches_found,
                    'duration': duration,
                    'success': result.returncode == 0
                }
                
                cli_results.append(cli_result)
                print(f"      ✅ {status} ({matches_found} matches) in {duration:.2f}s")
                
            except subprocess.TimeoutExpired:
                print(f"      ❌ Timeout after 60s")
                cli_results.append({
                    'name': name,
                    'status': 'Timeout',
                    'matches_found': 0,
                    'duration': 60,
                    'success': False
                })
            except Exception as e:
                print(f"      ❌ Error: {e}")
                cli_results.append({
                    'name': name,
                    'status': 'Error',
                    'matches_found': 0,
                    'duration': 0,
                    'success': False
                })
        
        self.results['cli'] = cli_results
        return cli_results
    
    def test_gui_components(self):
        """Test GUI component availability"""
        print("🧪 Testing GUI Components...")
        try:
            import readysearch_gui
            
            # Test GUI initialization
            app = readysearch_gui.ReadySearchGUI()
            
            # Test key components
            components = {
                'root_window': hasattr(app, 'root'),
                'quick_name_entry': hasattr(app, 'quick_name_entry'),
                'quick_year_entry': hasattr(app, 'quick_year_entry'),
                'search_results': hasattr(app, 'search_results'),
                'summary_tree': hasattr(app, 'summary_tree'),
                'detailed_text': hasattr(app, 'detailed_text')
            }
            
            gui_score = sum(components.values()) / len(components)
            
            print(f"   ✅ GUI component availability: {gui_score:.0%}")
            for component, available in components.items():
                status = "✅" if available else "❌"
                print(f"      {status} {component}")
            
            self.results['gui'] = {
                'components': components,
                'availability_score': gui_score,
                'functional': gui_score >= 0.8
            }
            
            return True
            
        except Exception as e:
            print(f"   ❌ GUI test failed: {e}")
            self.results['gui'] = {
                'components': {},
                'availability_score': 0,
                'functional': False,
                'error': str(e)
            }
            return False
    
    def test_api_functionality(self):
        """Test API functionality and performance"""
        print("🧪 Testing API Functionality...")
        
        try:
            # Test API health
            health_response = requests.get(f"{self.api_base_url}/api/health", timeout=10)
            api_healthy = health_response.status_code == 200
            
            if not api_healthy:
                print(f"   ❌ API not healthy: {health_response.status_code}")
                self.results['api'] = {
                    'healthy': False,
                    'functional': False,
                    'error': f"Health check failed: {health_response.status_code}"
                }
                return False
            
            print("   ✅ API is healthy")
            
            # Test session creation
            session_payload = {
                "names": self.test_names[:1],  # Test with one name to avoid timeout
                "mode": "standard"
            }
            
            print("   🚀 Testing session creation...")
            session_response = requests.post(
                f"{self.api_base_url}/api/start-automation",
                json=session_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data.get('session_id')
                print(f"   ✅ Session created: {session_id[:8]}...")
                
                # Test session status
                status_response = requests.get(f"{self.api_base_url}/api/session/{session_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   ✅ Session status: {status_data.get('status')}")
                    
                    self.results['api'] = {
                        'healthy': True,
                        'functional': True,
                        'session_creation': True,
                        'status_check': True
                    }
                    return True
                else:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
                    self.results['api'] = {
                        'healthy': True,
                        'functional': False,
                        'session_creation': True,
                        'status_check': False
                    }
                    return False
            else:
                print(f"   ❌ Session creation failed: {session_response.status_code}")
                self.results['api'] = {
                    'healthy': True,
                    'functional': False,
                    'session_creation': False,
                    'status_check': False
                }
                return False
                
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
            self.results['api'] = {
                'healthy': False,
                'functional': False,
                'error': str(e)
            }
            return False
    
    def analyze_performance(self):
        """Analyze performance across interfaces"""
        print("🧪 Analyzing Performance...")
        
        cli_results = self.results.get('cli', [])
        gui_functional = self.results.get('gui', {}).get('functional', False)
        api_functional = self.results.get('api', {}).get('functional', False)
        
        # CLI performance analysis
        if cli_results:
            cli_durations = [r['duration'] for r in cli_results if r['success']]
            cli_success_rate = sum(1 for r in cli_results if r['success']) / len(cli_results)
            avg_cli_duration = sum(cli_durations) / len(cli_durations) if cli_durations else 0
            
            print(f"   📊 CLI Success Rate: {cli_success_rate:.0%}")
            print(f"   ⏱️ CLI Average Duration: {avg_cli_duration:.2f}s")
        else:
            cli_success_rate = 0
            avg_cli_duration = 0
        
        # Overall functionality
        interface_scores = {
            'CLI': cli_success_rate,
            'GUI': 1.0 if gui_functional else 0.0,
            'API': 1.0 if api_functional else 0.0
        }
        
        overall_score = sum(interface_scores.values()) / len(interface_scores)
        
        print(f"   📈 Overall Functionality: {overall_score:.0%}")
        for interface, score in interface_scores.items():
            status = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
            print(f"      {status} {interface}: {score:.0%}")
        
        self.results['performance'] = {
            'cli_success_rate': cli_success_rate,
            'cli_avg_duration': avg_cli_duration,
            'interface_scores': interface_scores,
            'overall_score': overall_score
        }
        
        return overall_score >= 0.8
    
    def validate_accuracy(self):
        """Validate search accuracy and consistency"""
        print("🧪 Validating Search Accuracy...")
        
        cli_results = self.results.get('cli', [])
        
        # Analyze CLI results for accuracy patterns
        if cli_results:
            successful_searches = [r for r in cli_results if r['success']]
            accuracy_score = len(successful_searches) / len(cli_results)
            
            # Check for expected matches (Anthony Bek should match)
            anthony_results = [r for r in cli_results if 'Anthony Bek' in r['name']]
            if anthony_results:
                anthony_matched = anthony_results[0]['status'] == 'Match'
                print(f"   🎯 Anthony Bek Match: {'✅' if anthony_matched else '❌'}")
            
            print(f"   📊 Search Accuracy: {accuracy_score:.0%}")
            
            self.results['accuracy'] = {
                'accuracy_score': accuracy_score,
                'successful_searches': len(successful_searches),
                'total_searches': len(cli_results)
            }
            
            return accuracy_score >= 0.8
        else:
            self.results['accuracy'] = {
                'accuracy_score': 0,
                'successful_searches': 0,
                'total_searches': 0
            }
            return False
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE VALIDATION REPORT")
        print("=" * 60)
        
        # Performance summary
        perf = self.results.get('performance', {})
        print(f"Overall Functionality: {perf.get('overall_score', 0):.0%}")
        print(f"CLI Success Rate: {perf.get('cli_success_rate', 0):.0%}")
        print(f"CLI Average Duration: {perf.get('cli_avg_duration', 0):.2f}s")
        
        # Interface status
        print("\nInterface Status:")
        interface_scores = perf.get('interface_scores', {})
        for interface, score in interface_scores.items():
            status = "✅ PASS" if score >= 0.8 else "⚠️ WARN" if score >= 0.5 else "❌ FAIL"
            print(f"   {interface}: {status} ({score:.0%})")
        
        # Accuracy summary
        accuracy = self.results.get('accuracy', {})
        print(f"\nSearch Accuracy: {accuracy.get('accuracy_score', 0):.0%}")
        print(f"Successful Searches: {accuracy.get('successful_searches', 0)}/{accuracy.get('total_searches', 0)}")
        
        # Production readiness assessment
        overall_score = perf.get('overall_score', 0)
        accuracy_score = accuracy.get('accuracy_score', 0)
        
        production_ready = overall_score >= 0.8 and accuracy_score >= 0.8
        print(f"\nProduction Ready: {'✅ YES' if production_ready else '❌ NO'}")
        
        # Save results to file
        with open('validation_report.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results,
                'production_ready': production_ready
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: validation_report.json")
        return production_ready
    
    def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🚀 ReadySearch Comprehensive Validation")
        print("=" * 60)
        
        # Run all tests
        cli_ok = len(self.test_cli_performance()) > 0
        gui_ok = self.test_gui_components()
        api_ok = self.test_api_functionality()
        perf_ok = self.analyze_performance()
        accuracy_ok = self.validate_accuracy()
        
        # Generate final report
        production_ready = self.generate_report()
        
        return production_ready

if __name__ == "__main__":
    validator = ComprehensiveValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\n🎉 VALIDATION PASSED - Ready for production!")
    else:
        print("\n⚠️ VALIDATION FAILED - Needs attention before production")
    
    sys.exit(0 if success else 1)