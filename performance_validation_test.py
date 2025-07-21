#!/usr/bin/env python3
"""
Comprehensive Performance Validation Test Suite
Tests both current and optimized ReadySearch systems for batch processing
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import statistics

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import both systems for comparison
from enhanced_cli import EnhancedReadySearchCLI
from optimized_batch_cli import OptimizedBatchSearcher, parse_names_input

class PerformanceValidator:
    """Comprehensive performance validation system"""
    
    def __init__(self):
        self.test_results = {
            'current_system': {},
            'optimized_system': {},
            'comparison': {}
        }
    
    def generate_test_datasets(self) -> Dict[str, str]:
        """Generate test datasets of various sizes"""
        
        # Real names for testing (mix of common and uncommon names)
        test_names = [
            "andro cutuk,1977",      # Known working test case
            "john smith,1980",       # Common name
            "jane doe,1985",         # Another common name
            "michael johnson,1975",  # Common name
            "sarah williams,1990",   # Common name
            "david brown,1982",      # Common name
            "lisa davis,1987",       # Common name
            "robert wilson,1979",    # Common name
            "maria garcia,1983",     # Common name with hispanic origin
            "james miller,1981",     # Common name
            "patricia jones,1988",   # Common name
            "christopher taylor,1984", # Long first name
            "mary anderson,1986",    # Common name
            "william thomas,1978",   # Common name
            "elizabeth martin,1989", # Long first name
        ]
        
        # Generate datasets of different sizes
        datasets = {
            'single': test_names[0],  # 1 name
            'small': ';'.join(test_names[:3]),  # 3 names
            'medium': ';'.join(test_names[:8]),  # 8 names
            'large': ';'.join(test_names[:15]),  # 15 names
            'stress': ';'.join(test_names * 7)[:20],  # 20 names (repeat pattern)
        }
        
        return datasets
    
    async def test_current_system(self, dataset_name: str, names_input: str) -> Dict[str, Any]:
        """Test the current enhanced CLI system"""
        print(f"\n🔍 Testing CURRENT system with {dataset_name} dataset...")
        
        try:
            current_cli = EnhancedReadySearchCLI()
            
            start_time = time.time()
            results = await current_cli.perform_search(names_input)
            total_duration = time.time() - start_time
            
            # Analyze results
            successful = len([r for r in results if r.status != 'Error'])
            matches = len([r for r in results if r.matches_found > 0])
            
            test_result = {
                'dataset': dataset_name,
                'total_searches': len(results),
                'successful_searches': successful,
                'matches_found': matches,
                'total_duration': total_duration,
                'avg_duration': total_duration / len(results) if results else 0,
                'throughput': len(results) / (total_duration / 60),  # searches per minute
                'success_rate': (successful / len(results) * 100) if results else 0,
                'match_rate': (matches / len(results) * 100) if results else 0,
                'errors': len(results) - successful
            }
            
            print(f"   ✅ Completed: {len(results)} searches in {total_duration:.2f}s")
            print(f"   📊 Success rate: {test_result['success_rate']:.1f}%")
            print(f"   🎯 Match rate: {test_result['match_rate']:.1f}%")
            
            return test_result
            
        except Exception as e:
            print(f"   ❌ Current system test failed: {str(e)}")
            return {
                'dataset': dataset_name,
                'error': str(e),
                'total_duration': 0,
                'failed': True
            }
    
    async def test_optimized_system(self, dataset_name: str, names_input: str) -> Dict[str, Any]:
        """Test the optimized batch system"""
        print(f"\n⚡ Testing OPTIMIZED system with {dataset_name} dataset...")
        
        try:
            # Parse search records
            search_records = parse_names_input(names_input)
            
            # Configure based on dataset size
            batch_size = len(search_records)
            if batch_size <= 3:
                pool_size, max_concurrent = 2, 2
            elif batch_size <= 8:
                pool_size, max_concurrent = 3, 3
            else:
                pool_size, max_concurrent = 4, 4
            
            # Initialize optimized searcher
            searcher = OptimizedBatchSearcher(pool_size=pool_size, max_concurrent=max_concurrent)
            await searcher.initialize()
            
            try:
                start_time = time.time()
                results = await searcher.batch_search_concurrent(search_records)
                total_duration = time.time() - start_time
                
                # Analyze results
                successful = len([r for r in results if r.status != 'Error'])
                matches = len([r for r in results if r.matches_found > 0])
                
                test_result = {
                    'dataset': dataset_name,
                    'total_searches': len(results),
                    'successful_searches': successful,
                    'matches_found': matches,
                    'total_duration': total_duration,
                    'avg_duration': total_duration / len(results) if results else 0,
                    'throughput': len(results) / (total_duration / 60),  # searches per minute
                    'success_rate': (successful / len(results) * 100) if results else 0,
                    'match_rate': (matches / len(results) * 100) if results else 0,
                    'errors': len(results) - successful,
                    'optimization_settings': {
                        'pool_size': pool_size,
                        'max_concurrent': max_concurrent
                    }
                }
                
                print(f"   ✅ Completed: {len(results)} searches in {total_duration:.2f}s")
                print(f"   📊 Success rate: {test_result['success_rate']:.1f}%")
                print(f"   🎯 Match rate: {test_result['match_rate']:.1f}%")
                
                return test_result
                
            finally:
                await searcher.cleanup()
                
        except Exception as e:
            print(f"   ❌ Optimized system test failed: {str(e)}")
            return {
                'dataset': dataset_name,
                'error': str(e),
                'total_duration': 0,
                'failed': True
            }
    
    def calculate_performance_comparison(self, current_results: Dict, optimized_results: Dict) -> Dict[str, Any]:
        """Calculate performance improvement metrics"""
        
        comparison = {}
        
        for dataset_name in current_results.keys():
            if dataset_name in optimized_results:
                current = current_results[dataset_name]
                optimized = optimized_results[dataset_name]
                
                if not current.get('failed') and not optimized.get('failed'):
                    # Calculate improvements
                    time_improvement = ((current['total_duration'] - optimized['total_duration']) / current['total_duration'] * 100) if current['total_duration'] > 0 else 0
                    throughput_improvement = ((optimized['throughput'] - current['throughput']) / current['throughput'] * 100) if current['throughput'] > 0 else 0
                    
                    comparison[dataset_name] = {
                        'dataset': dataset_name,
                        'current_duration': current['total_duration'],
                        'optimized_duration': optimized['total_duration'],
                        'time_improvement_percent': time_improvement,
                        'current_throughput': current['throughput'],
                        'optimized_throughput': optimized['throughput'],
                        'throughput_improvement_percent': throughput_improvement,
                        'accuracy_maintained': abs(current['success_rate'] - optimized['success_rate']) < 5,  # Within 5%
                        'search_count': current['total_searches']
                    }
        
        return comparison
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        report = {
            'test_metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'test_version': 'Performance Validation Suite v1.0',
                'systems_tested': ['Enhanced CLI (Current)', 'Optimized Batch CLI (New)']
            },
            'current_system_results': self.test_results['current_system'],
            'optimized_system_results': self.test_results['optimized_system'],
            'performance_comparison': self.test_results['comparison'],
            'summary': {}
        }
        
        # Calculate summary statistics
        comparisons = self.test_results['comparison']
        if comparisons:
            time_improvements = [c['time_improvement_percent'] for c in comparisons.values() if 'time_improvement_percent' in c]
            throughput_improvements = [c['throughput_improvement_percent'] for c in comparisons.values() if 'throughput_improvement_percent' in c]
            
            report['summary'] = {
                'datasets_tested': len(comparisons),
                'average_time_improvement': statistics.mean(time_improvements) if time_improvements else 0,
                'max_time_improvement': max(time_improvements) if time_improvements else 0,
                'min_time_improvement': min(time_improvements) if time_improvements else 0,
                'average_throughput_improvement': statistics.mean(throughput_improvements) if throughput_improvements else 0,
                'accuracy_maintained_count': len([c for c in comparisons.values() if c.get('accuracy_maintained', False)]),
                'optimization_successful': statistics.mean(time_improvements) > 30 if time_improvements else False  # 30% improvement threshold
            }
        
        return report
    
    async def run_comprehensive_validation(self):
        """Run complete validation suite"""
        
        print("🧪 COMPREHENSIVE PERFORMANCE VALIDATION SUITE")
        print("="*60)
        print("📊 Testing both current and optimized ReadySearch systems")
        print("🎯 Measuring performance improvements and accuracy maintenance")
        print("⚡ Datasets: Single, Small (3), Medium (8), Large (15), Stress (20)")
        print()
        
        # Generate test datasets
        datasets = self.generate_test_datasets()
        
        print(f"📋 Generated {len(datasets)} test datasets")
        for name, data in datasets.items():
            count = len(data.split(';'))
            print(f"   • {name.title()}: {count} searches")
        
        # Test current system
        print(f"\n{'='*60}")
        print("🔍 TESTING CURRENT SYSTEM")
        print('='*60)
        
        current_results = {}
        for dataset_name, names_input in datasets.items():
            try:
                result = await self.test_current_system(dataset_name, names_input)
                current_results[dataset_name] = result
                
                # Small delay between tests
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                print("⚠️ Current system testing interrupted")
                break
            except Exception as e:
                print(f"❌ Error testing current system with {dataset_name}: {e}")
                current_results[dataset_name] = {'failed': True, 'error': str(e)}
        
        self.test_results['current_system'] = current_results
        
        # Test optimized system
        print(f"\n{'='*60}")
        print("⚡ TESTING OPTIMIZED SYSTEM")
        print('='*60)
        
        optimized_results = {}
        for dataset_name, names_input in datasets.items():
            try:
                result = await self.test_optimized_system(dataset_name, names_input)
                optimized_results[dataset_name] = result
                
                # Small delay between tests
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                print("⚠️ Optimized system testing interrupted")
                break
            except Exception as e:
                print(f"❌ Error testing optimized system with {dataset_name}: {e}")
                optimized_results[dataset_name] = {'failed': True, 'error': str(e)}
        
        self.test_results['optimized_system'] = optimized_results
        
        # Calculate comparisons
        comparison_results = self.calculate_performance_comparison(current_results, optimized_results)
        self.test_results['comparison'] = comparison_results
        
        # Generate and display final report
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE PERFORMANCE REPORT")
        print('='*60)
        
        report = self.generate_comprehensive_report()
        
        # Display summary
        summary = report['summary']
        print(f"📋 Summary:")
        print(f"   Datasets Tested: {summary.get('datasets_tested', 0)}")
        print(f"   Average Time Improvement: {summary.get('average_time_improvement', 0):.1f}%")
        print(f"   Maximum Time Improvement: {summary.get('max_time_improvement', 0):.1f}%")
        print(f"   Average Throughput Gain: {summary.get('average_throughput_improvement', 0):.1f}%")
        print(f"   Accuracy Maintained: {summary.get('accuracy_maintained_count', 0)}/{len(comparison_results)} datasets")
        print(f"   Optimization Success: {'✅ YES' if summary.get('optimization_successful', False) else '❌ NO'}")
        
        # Display detailed comparison
        print(f"\n📈 Detailed Performance Comparison:")
        print(f"{'Dataset':<12} {'Current':<10} {'Optimized':<12} {'Improvement':<12} {'Throughput':<15}")
        print("-" * 65)
        
        for dataset_name, comp in comparison_results.items():
            print(f"{dataset_name:<12} "
                  f"{comp['current_duration']:<10.1f} "
                  f"{comp['optimized_duration']:<12.1f} "
                  f"{comp['time_improvement_percent']:<12.1f}% "
                  f"{comp['throughput_improvement_percent']:<15.1f}%")
        
        # Save detailed report
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        report_filename = f"performance_validation_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_filename}")
        print(f"\n{'='*60}")
        print("🎉 COMPREHENSIVE VALIDATION COMPLETED!")
        
        return report

async def main():
    """Main validation function"""
    
    print("Starting ReadySearch Performance Validation...")
    
    try:
        validator = PerformanceValidator()
        report = await validator.run_comprehensive_validation()
        
        # Return success code based on optimization results
        if report['summary'].get('optimization_successful', False):
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Optimization did not meet performance targets
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())