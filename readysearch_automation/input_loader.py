"""Input data loading and validation module."""

import pandas as pd
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class InputLoader:
    """Handles loading and validation of input data."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        
    def load_names(self) -> List[str]:
        """
        Load names from CSV file.
        
        Returns:
            List of names to search
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file format is invalid
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.file_path}")
            
        try:
            # Try to read CSV file
            df = pd.read_csv(self.file_path)
            
            # Check if 'name' column exists
            if 'name' not in df.columns:
                # If no 'name' column, assume first column contains names
                if len(df.columns) > 0:
                    names_column = df.columns[0]
                    logger.warning(f"No 'name' column found. Using '{names_column}' column.")
                    names = df[names_column].tolist()
                else:
                    raise ValueError("CSV file appears to be empty or invalid")
            else:
                names = df['name'].tolist()
                
            # Clean and validate names
            cleaned_names = self._clean_names(names)
            
            logger.info(f"Loaded {len(cleaned_names)} names from {self.file_path}")
            return cleaned_names
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
            
    def _clean_names(self, names: List[str]) -> List[str]:
        """
        Clean and validate name list.
        
        Args:
            names: Raw list of names
            
        Returns:
            Cleaned list of valid names
        """
        cleaned = []
        
        for i, name in enumerate(names):
            if pd.isna(name) or not str(name).strip():
                logger.warning(f"Skipping empty name at row {i + 1}")
                continue
                
            # Convert to string and strip whitespace
            clean_name = str(name).strip()
            
            # Basic validation
            if len(clean_name) < 2:
                logger.warning(f"Skipping too short name: '{clean_name}'")
                continue
                
            if len(clean_name) > 100:
                logger.warning(f"Truncating long name: '{clean_name[:50]}...'")
                clean_name = clean_name[:100]
                
            cleaned.append(clean_name)
            
        if not cleaned:
            raise ValueError("No valid names found in input file")
            
        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in cleaned:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)
                
        if len(unique_names) != len(cleaned):
            logger.info(f"Removed {len(cleaned) - len(unique_names)} duplicate names")
            
        return unique_names
        
    @staticmethod
    def create_sample_input(file_path: str, sample_names: Optional[List[str]] = None):
        """
        Create a sample input CSV file.
        
        Args:
            file_path: Path where to create the sample file
            sample_names: Optional list of names to use
        """
        if sample_names is None:
            sample_names = [
                "John Smith",
                "Jane Doe", 
                "Robert Johnson",
                "Mary Williams",
                "David Brown",
                "Sarah Davis",
                "Michael Wilson",
                "Lisa Anderson"
            ]
            
        df = pd.DataFrame({'name': sample_names})
        df.to_csv(file_path, index=False)
        logger.info(f"Created sample input file: {file_path}")