"""ReadySearch.com.au automation package."""

from .input_loader import InputLoader
from .browser_controller import BrowserController
from .popup_handler import PopupHandler
from .result_parser import ResultParser, NameMatcher
from .reporter import Reporter

__version__ = "1.0.0"
__author__ = "ReadySearch Automation"

__all__ = [
    'InputLoader',
    'BrowserController', 
    'PopupHandler',
    'ResultParser',
    'NameMatcher',
    'Reporter'
]