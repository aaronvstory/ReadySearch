"""Configuration settings for ReadySearch automation."""

from typing import Dict, Any


class Config:
    """Configuration class for automation settings."""
    
    # Site configuration
    BASE_URL = "https://readysearch.com.au/products?person"
    
    # Birth year range configuration
    DEFAULT_BIRTH_YEAR_START = 1900
    DEFAULT_BIRTH_YEAR_END = 2025
    
    # Timing configuration (in seconds)
    DELAY_BETWEEN_SEARCHES = 2.5
    PAGE_TIMEOUT = 30000  # milliseconds
    ELEMENT_TIMEOUT = 10000  # milliseconds
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    
    # Browser configuration
    HEADLESS = True
    BROWSER_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
    ]
    
    # User agent for realistic requests
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
    
    # Browser selectors for ReadySearch page elements
    SELECTORS = {
        # Search form selectors
        'name_input': 'input[name="name"], input[placeholder*="name"], #name',
        'first_name_input': 'input[name="first_name"], input[placeholder*="first"], #first_name',
        'last_name_input': 'input[name="last_name"], input[placeholder*="last"], #last_name',
        'birth_year_start': 'select[name="birth_year_start"], select[name="start_year"], #start_year',
        'birth_year_end': 'select[name="birth_year_end"], select[name="end_year"], #end_year',
        'search_button': '.sch_but, button[type="submit"], input[type="submit"]',
        
        # Results page selectors
        'results_table': 'table, .results-table, #results',
        'result_rows': 'tr, .result-row',
        'result_checkboxes': 'input[type="checkbox"]',
        'continue_button': 'button:contains("Continue"), input[value*="Continue"]',
        
        # Popup and modal selectors
        'popup_modal': '.modal, .popup, .alert',
        'popup_ok_button': 'button:contains("OK"), input[value="OK"], .ok-button',
        'popup_close_button': '.close, .modal-close, button:contains("Close")',
        'alert_message': '.alert-message, .popup-message',
        
        # Common page elements
        'loading_indicator': '.loading, .spinner, .progress',
        'error_message': '.error, .alert-danger, .error-message'
    }
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File paths
    INPUT_FILE = "input_names.csv"
    OUTPUT_FILE = "search_results.csv"
    LOG_FILE = "automation.log"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            'base_url': cls.BASE_URL,
            'birth_year_start': cls.DEFAULT_BIRTH_YEAR_START,
            'birth_year_end': cls.DEFAULT_BIRTH_YEAR_END,
            'delay': cls.DELAY_BETWEEN_SEARCHES,
            'page_timeout': cls.PAGE_TIMEOUT,
            'element_timeout': cls.ELEMENT_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'headless': cls.HEADLESS,
            'browser_args': cls.BROWSER_ARGS,
            'user_agent': cls.USER_AGENT,
            'selectors': cls.SELECTORS,
            'log_level': cls.LOG_LEVEL,
            'log_format': cls.LOG_FORMAT,
            'input_file': cls.INPUT_FILE,
            'output_file': cls.OUTPUT_FILE,
            'log_file': cls.LOG_FILE
        }