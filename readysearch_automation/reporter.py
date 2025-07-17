"""Results reporting and output generation module."""

import csv
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class Reporter:
    """Handles result reporting and output generation."""
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        self.results: List[Dict[str, Any]] = []
        
    def add_result(self, name: str, status: str, **kwargs):
        """
        Add a search result.
        
        Args:
            name: The searched name
            status: Result status ('Match', 'No Match', 'Error')
            **kwargs: Additional result data
        """
        result = {
            'name': name,
            'status': status,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            **kwargs
        }
        
        self.results.append(result)
        logger.debug(f"Added result: {name} -> {status}")
        
    def save_results_csv(self) -> bool:
        """
        Save results to CSV file.
        
        Returns:
            True if successful
        """
        try:
            if not self.results:
                logger.warning("No results to save")
                return False
                
            # Create output directory if it doesn't exist
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine all possible columns
            all_columns = set()
            for result in self.results:
                all_columns.update(result.keys())
                
            # Ensure standard columns are first
            standard_columns = ['name', 'status', 'timestamp']
            other_columns = sorted(all_columns - set(standard_columns))
            columns = standard_columns + other_columns
            
            # Write CSV
            with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                
                for result in self.results:
                    # Ensure all columns have values
                    row = {col: result.get(col, '') for col in columns}
                    writer.writerow(row)
                    
            logger.info(f"Results saved to CSV: {self.output_file}")
            logger.info(f"Total results: {len(self.results)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV results: {str(e)}")
            return False
            
    def save_results_json(self, json_file: Optional[str] = None) -> bool:
        """
        Save results to JSON file.
        
        Args:
            json_file: Optional JSON file path
            
        Returns:
            True if successful
        """
        try:
            if not self.results:
                logger.warning("No results to save")
                return False
                
            if json_file is None:
                json_file = self.output_file.with_suffix('.json')
            else:
                json_file = Path(json_file)
                
            # Create output directory if it doesn't exist
            json_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for JSON
            output_data = {
                'metadata': {
                    'total_results': len(self.results),
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'matches_found': len([r for r in self.results if r['status'] == 'Match']),
                    'no_matches': len([r for r in self.results if r['status'] == 'No Match']),
                    'errors': len([r for r in self.results if r['status'] == 'Error'])
                },
                'results': self.results
            }
            
            # Write JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Results saved to JSON: {json_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON results: {str(e)}")
            return False
            
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate summary statistics.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {'error': 'No results available'}
            
        total = len(self.results)
        matches = len([r for r in self.results if r['status'] == 'Match'])
        no_matches = len([r for r in self.results if r['status'] == 'No Match'])
        errors = len([r for r in self.results if r['status'] == 'Error'])
        
        summary = {
            'total_searches': total,
            'matches_found': matches,
            'no_matches': no_matches,
            'errors': errors,
            'success_rate': (matches + no_matches) / total * 100 if total > 0 else 0,
            'match_rate': matches / total * 100 if total > 0 else 0,
            'error_rate': errors / total * 100 if total > 0 else 0
        }
        
        # Add timing information if available
        timestamps = [r.get('timestamp') for r in self.results if r.get('timestamp')]
        if timestamps:
            summary['first_result'] = min(timestamps)
            summary['last_result'] = max(timestamps)
            
        # Add error details
        if errors > 0:
            error_details = {}
            for result in self.results:
                if result['status'] == 'Error':
                    error_msg = result.get('error', 'Unknown error')
                    error_details[error_msg] = error_details.get(error_msg, 0) + 1
            summary['error_breakdown'] = error_details
            
        return summary
        
    def print_summary(self):
        """Print summary to console."""
        summary = self.generate_summary_report()
        
        if 'error' in summary:
            print(f"Summary Error: {summary['error']}")
            return
            
        print("\n" + "="*50)
        print("SEARCH RESULTS SUMMARY")
        print("="*50)
        print(f"Total Searches: {summary['total_searches']}")
        print(f"Matches Found: {summary['matches_found']}")
        print(f"No Matches: {summary['no_matches']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Match Rate: {summary['match_rate']:.1f}%")
        
        if summary['errors'] > 0:
            print(f"Error Rate: {summary['error_rate']:.1f}%")
            print("\nError Breakdown:")
            for error, count in summary.get('error_breakdown', {}).items():
                print(f"  - {error}: {count}")
                
        if 'first_result' in summary:
            print(f"\nTime Range: {summary['first_result']} to {summary['last_result']}")
            
        print("="*50)
        
    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get results as pandas DataFrame.
        
        Returns:
            DataFrame with results
        """
        if not self.results:
            return pd.DataFrame()
            
        return pd.DataFrame(self.results)
        
    def export_matches_only(self, matches_file: Optional[str] = None) -> bool:
        """
        Export only the matches to a separate file.
        
        Args:
            matches_file: Optional file path for matches
            
        Returns:
            True if successful
        """
        try:
            matches = [r for r in self.results if r['status'] == 'Match']
            
            if not matches:
                logger.info("No matches to export")
                return True
                
            if matches_file is None:
                matches_file = self.output_file.with_name(
                    self.output_file.stem + '_matches_only' + self.output_file.suffix
                )
            else:
                matches_file = Path(matches_file)
                
            # Create temporary reporter for matches
            temp_reporter = Reporter(str(matches_file))
            temp_reporter.results = matches
            
            success = temp_reporter.save_results_csv()
            
            if success:
                logger.info(f"Matches exported to: {matches_file}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error exporting matches: {str(e)}")
            return False
            
    def get_failed_searches(self) -> List[Dict[str, Any]]:
        """
        Get list of failed searches for retry.
        
        Returns:
            List of failed search results
        """
        return [r for r in self.results if r['status'] == 'Error']
        
    def clear_results(self):
        """Clear all stored results."""
        self.results.clear()
        logger.info("Results cleared")
        
    def get_result_count(self) -> int:
        """Get total number of results."""
        return len(self.results)
        
    def has_results(self) -> bool:
        """Check if there are any results."""
        return len(self.results) > 0