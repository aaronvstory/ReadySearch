#!/usr/bin/env python3
"""
ReadySearch Advanced GUI - Beautiful Tkinter interface with modern styling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import asyncio
import threading
import json
import csv
from datetime import datetime
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import webbrowser

# Custom styling and modern widgets
try:
    from tkinter import font
    import tkinter.messagebox as msgbox
except ImportError:
    pass

# Import existing functionality
sys.path.append(str(Path(__file__).parent))
from config import Config
from readysearch_automation.input_loader import SearchRecord
from production_cli import ProductionCLI

@dataclass
class GUISearchResult:
    """GUI-specific search result"""
    name: str
    status: str
    search_duration: float
    matches_found: int
    exact_matches: int
    partial_matches: int
    match_category: str
    match_reasoning: str
    detailed_results: List[Dict[str, Any]]
    timestamp: str
    birth_year: Optional[int] = None
    error: Optional[str] = None

class ModernStyle:
    """Professional modern styling configuration for the GUI with better contrast"""
    
    # Improved color palette with better contrast and readability
    COLORS = {
        # Primary colors with better contrast
        'primary': '#1E40AF',        # Deep blue for primary actions
        'primary_light': '#3B82F6',  # Bright blue for hover states
        'primary_dark': '#1E3A8A',   # Darker blue for pressed states
        'secondary': '#059669',      # Emerald for secondary actions
        'secondary_light': '#10B981', # Light emerald for hover
        'success': '#16A34A',        # Success green with better contrast
        'success_light': '#22C55E',  # Light success green for hover
        'warning': '#DC2626',        # Better contrast warning red
        'warning_light': '#EF4444',  # Light warning for hover
        'danger': '#B91C1C',         # Deep red for danger/delete actions
        'danger_light': '#DC2626',   # Light red for hover
        
        # Background colors with better contrast
        'background': '#F9FAFB',     # Very light gray background (main)
        'surface': '#FFFFFF',        # Pure white surface for cards
        'surface_alt': '#F3F4F6',    # Light gray for alternating surfaces
        'surface_hover': '#E5E7EB',  # Hover surface
        'surface_dark': '#E5E7EB',   # Darker surface for headers
        
        # Border colors
        'border': '#D1D5DB',         # Medium gray border
        'border_focus': '#3B82F6',   # Bright blue focus border
        'border_dark': '#9CA3AF',    # Darker border for emphasis
        
        # Text colors with maximum contrast
        'text_primary': '#111827',   # Almost black text (maximum contrast)
        'text_secondary': '#374151', # Dark gray text
        'text_muted': '#6B7280',     # Medium gray text for labels
        'text_light': '#9CA3AF',     # Light gray text
        'text_white': '#FFFFFF',     # White text for dark backgrounds
        
        # Input colors
        'input_bg': '#FFFFFF',       # Pure white input background
        'input_border': '#D1D5DB',   # Medium gray input border
        'input_focus_bg': '#F9FAFB', # Slight gray on focus
        
        # Special colors
        'accent': '#8B5CF6',         # Purple accent
        'accent_light': '#A78BFA',   # Light purple for hover
        'header_bg': '#1F2937',      # Dark gray-blue for header
        'header_text': '#FFFFFF',    # White text for header
        'treeview_alt': '#F9FAFB',   # Alternating row color
        'scrollbar': '#D1D5DB',      # Scrollbar color
        'scrollbar_hover': '#9CA3AF', # Scrollbar hover color
        'hover': '#E5E7EB',          # General hover state
        'active': '#D1D5DB'          # Active/pressed state
    }
    
    # Enhanced fonts with better hierarchy and readability
    FONTS = {
        'title': ('Segoe UI', 20, 'bold'),      # Larger title
        'subtitle': ('Segoe UI', 14),           # Normal weight subtitle
        'heading': ('Segoe UI', 13, 'bold'),    # Section headings
        'body': ('Segoe UI', 11),               # Standard body text
        'body_large': ('Segoe UI', 12),         # Large body text
        'small': ('Segoe UI', 10),              # Small text
        'tiny': ('Segoe UI', 9),                # Tiny text
        'code': ('Consolas', 11),               # Code/monospace
        'button': ('Segoe UI', 11, 'bold'),     # Button text
        'label': ('Segoe UI', 11)               # Label text
    }
    
    @classmethod
    def configure_ttk_styles(cls, root):
        """Configure modern TTK styles with enhanced visual appeal"""
        style = ttk.Style()
        
        # Set theme base
        style.theme_use('clam')
        
        # Configure enhanced button styles with better contrast
        style.configure(
            'Primary.TButton',
            background=cls.COLORS['primary'],
            foreground='white',
            borderwidth=2,
            focuscolor='none',
            padding=(12, 8),
            font=cls.FONTS['button'],
            relief='flat'
        )
        style.map('Primary.TButton',
            background=[('active', cls.COLORS['primary_light']),
                       ('pressed', cls.COLORS['primary_dark'])],
            relief=[('pressed', 'sunken')]
        )
        
        style.configure(
            'Success.TButton',
            background=cls.COLORS['success'],
            foreground='white',
            borderwidth=1,
            focuscolor='none',
            padding=(15, 8),
            font=cls.FONTS['button']
        )
        style.map('Success.TButton',
            background=[('active', cls.COLORS['success_light']),
                       ('pressed', cls.COLORS['success'])]
        )
        
        style.configure(
            'Warning.TButton',
            background=cls.COLORS['warning'],
            foreground='white',
            borderwidth=1,
            focuscolor='none',
            padding=(15, 8),
            font=cls.FONTS['button']
        )
        style.map('Warning.TButton',
            background=[('active', cls.COLORS['warning_light']),
                       ('pressed', cls.COLORS['warning'])]
        )
        
        style.configure(
            'Danger.TButton',
            background=cls.COLORS['danger'],
            foreground='white',
            borderwidth=1,
            focuscolor='none',
            padding=(15, 8),
            font=cls.FONTS['button']
        )
        style.map('Danger.TButton',
            background=[('active', cls.COLORS['danger_light']),
                       ('pressed', cls.COLORS['danger'])]
        )
        
        style.configure(
            'Secondary.TButton',
            background=cls.COLORS['secondary'],
            foreground='white',
            borderwidth=1,
            focuscolor='none',
            padding=(12, 6),
            font=cls.FONTS['body']
        )
        style.map('Secondary.TButton',
            background=[('active', cls.COLORS['secondary_light']),
                       ('pressed', cls.COLORS['secondary'])]
        )
        
        # Configure enhanced frame styles
        style.configure(
            'Card.TFrame',
            background=cls.COLORS['surface'],
            borderwidth=1,
            relief='solid',
            bordercolor=cls.COLORS['border']
        )
        
        style.configure(
            'Sidebar.TFrame',
            background=cls.COLORS['surface_alt'],
            borderwidth=1,
            relief='solid',
            bordercolor=cls.COLORS['border']
        )
        
        style.configure(
            'Header.TFrame',
            background=cls.COLORS['primary'],
            borderwidth=0
        )
        
        # Configure enhanced label styles
        style.configure(
            'Title.TLabel',
            background=cls.COLORS['header_bg'],
            foreground=cls.COLORS['text_white'],
            font=cls.FONTS['title'],
            padding=(10, 10)
        )
        
        style.configure(
            'Subtitle.TLabel',
            background=cls.COLORS['header_bg'],
            foreground=cls.COLORS['text_white'],
            font=cls.FONTS['subtitle'],
            padding=(10, 5)
        )
        
        style.configure(
            'Heading.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['heading'],
            padding=(5, 5)
        )
        
        style.configure(
            'Body.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_secondary'],
            font=cls.FONTS['body']
        )
        
        style.configure(
            'Muted.TLabel',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_muted'],
            font=cls.FONTS['small']
        )
        
        # Configure entry styles for better visibility
        style.configure(
            'Modern.TEntry',
            fieldbackground=cls.COLORS['input_bg'],
            background=cls.COLORS['input_bg'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=2,
            bordercolor=cls.COLORS['border'],
            focuscolor=cls.COLORS['border_focus'],
            insertcolor=cls.COLORS['text_primary'],
            padding=(10, 8),
            font=cls.FONTS['body'],
            relief='solid'
        )
        style.map('Modern.TEntry',
            bordercolor=[('focus', cls.COLORS['border_focus'])],
            fieldbackground=[('focus', cls.COLORS['input_focus_bg'])]
        )
        
        # Configure checkbutton styles for dark mode
        style.configure(
            'Modern.TCheckbutton',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            focuscolor='none',
            font=cls.FONTS['body']
        )
        style.map('Modern.TCheckbutton',
            background=[('active', cls.COLORS['surface_hover']),
                       ('pressed', cls.COLORS['surface_alt'])],
            foreground=[('active', cls.COLORS['text_primary'])]
        )
        
        # Configure notebook styles
        style.configure(
            'Modern.TNotebook',
            background=cls.COLORS['surface'],
            borderwidth=1,
            bordercolor=cls.COLORS['border']
        )
        
        style.configure(
            'Modern.TNotebook.Tab',
            background=cls.COLORS['surface_alt'],
            foreground=cls.COLORS['text_secondary'],
            padding=(15, 8),
            font=cls.FONTS['body']
        )
        style.map('Modern.TNotebook.Tab',
            background=[('selected', cls.COLORS['primary']),
                       ('active', cls.COLORS['hover'])],
            foreground=[('selected', 'white'),
                       ('active', cls.COLORS['text_primary'])]
        )
        
        # Configure treeview styles
        style.configure(
            'Modern.Treeview',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['surface'],
            borderwidth=1,
            bordercolor=cls.COLORS['border'],
            font=cls.FONTS['body']
        )
        style.configure(
            'Modern.Treeview.Heading',
            background=cls.COLORS['surface_alt'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=1,
            bordercolor=cls.COLORS['border'],
            font=cls.FONTS['heading']
        )
        
        # Configure labelframe styles
        style.configure(
            'Modern.TLabelframe',
            background=cls.COLORS['surface'],
            borderwidth=1,
            bordercolor=cls.COLORS['border'],
            relief='solid'
        )
        style.configure(
            'Modern.TLabelframe.Label',
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            font=cls.FONTS['heading']
        )
    
    @classmethod
    def configure_tk_widgets(cls, root):
        """Configure regular tk widgets for dark mode"""
        # Configure root window
        root.configure(bg=cls.COLORS['background'])
        
        # Default text widget configuration for dark mode
        root.option_add('*Text.background', cls.COLORS['input_bg'])
        root.option_add('*Text.foreground', cls.COLORS['text_primary'])
        root.option_add('*Text.insertBackground', cls.COLORS['text_primary'])
        root.option_add('*Text.selectBackground', cls.COLORS['primary'])
        root.option_add('*Text.selectForeground', 'white')
        root.option_add('*Text.font', 'Consolas 10')
        
        # Entry widget configuration for dark mode
        root.option_add('*Entry.background', cls.COLORS['input_bg'])
        root.option_add('*Entry.foreground', cls.COLORS['text_primary'])
        root.option_add('*Entry.insertBackground', cls.COLORS['text_primary'])
        root.option_add('*Entry.selectBackground', cls.COLORS['primary'])
        root.option_add('*Entry.selectForeground', 'white')
        
        # Scrollbar configuration for dark mode
        root.option_add('*Scrollbar.background', cls.COLORS['surface_alt'])
        root.option_add('*Scrollbar.troughColor', cls.COLORS['surface'])
        root.option_add('*Scrollbar.activeBackground', cls.COLORS['primary'])
        
        # Listbox configuration for dark mode
        root.option_add('*Listbox.background', cls.COLORS['input_bg'])
        root.option_add('*Listbox.foreground', cls.COLORS['text_primary'])
        root.option_add('*Listbox.selectBackground', cls.COLORS['primary'])
        root.option_add('*Listbox.selectForeground', 'white')
        
        return {
            'bg': cls.COLORS['background'],
            'text_bg': cls.COLORS['input_bg'],
            'text_fg': cls.COLORS['text_primary'],
            'select_bg': cls.COLORS['primary'],
            'select_fg': 'white',
            'border': cls.COLORS['border'],
            'insert_bg': cls.COLORS['text_primary']
        }

class SearchProgressWindow:
    """Enhanced progress window for search operations with modern styling"""
    
    def __init__(self, parent, total_searches):
        self.window = tk.Toplevel(parent)
        self.window.title("ReadySearch - Search in Progress")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.configure(bg=ModernStyle.COLORS['background'])
        
        # Center the window
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))
        
        # Make window non-resizable for cleaner appearance
        self.window.resizable(False, False)
        
        self.total_searches = total_searches
        self.current_search = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup enhanced progress window UI with modern styling"""
        # Main container with modern styling
        main_frame = ttk.Frame(self.window, style='Card.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced title with modern header
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🔍 ReadySearch - Processing Searches",
            style='Title.TLabel'
        )
        title_label.pack(pady=15)
        
        # Progress section with better visual hierarchy
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Enhanced progress bar with custom styling
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 15))
        
        # Enhanced status information
        self.status_label = ttk.Label(
            progress_frame,
            text="⏳ Preparing search automation...",
            style='Heading.TLabel'
        )
        self.status_label.pack(pady=(0, 10))
        
        # Current search info with better styling
        self.search_info_label = ttk.Label(
            progress_frame,
            text="",
            style='Body.TLabel'
        )
        self.search_info_label.pack(pady=(0, 15))
        
        # Enhanced results section
        results_label = ttk.Label(
            main_frame,
            text="📊 Live Search Results:",
            style='Heading.TLabel'
        )
        results_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Enhanced results text area with modern styling
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            width=70,
            font=ModernStyle.FONTS['code'],
            borderwidth=1,
            relief='solid',
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_primary'],
            selectbackground=ModernStyle.COLORS['primary_light'],
            selectforeground='white'
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def update_progress(self, current, total, current_name="", status=""):
        """Update enhanced progress display with visual feedback"""
        self.current_search = current
        progress_percent = (current / total) * 100
        self.progress_var.set(progress_percent)
        
        # Enhanced status with emoji and better formatting
        enhanced_status = f"🔍 {status}" if status else "🔍 Processing..."
        self.status_label.config(text=enhanced_status)
        
        # Enhanced search info with better visual hierarchy
        search_info = f"📋 Search {current} of {total}: 👤 {current_name}" if current_name else f"📋 Search {current} of {total}"
        self.search_info_label.config(text=search_info)
        
        self.window.update()
    
    def add_result_text(self, text):
        """Add text to results area"""
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.window.update()
    
    def close(self):
        """Close the progress window"""
        self.window.destroy()

class ReadySearchGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.production_cli = ProductionCLI()
        self.search_results: List[GUISearchResult] = []
        self.config = Config.get_config()
        
        self.setup_main_window()
        self.setup_styles()
        self.create_widgets()
        
    def setup_main_window(self):
        """Setup main window configuration with responsive sizing"""
        self.root.title("ReadySearch Advanced GUI v2.0")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive window size (90% of screen, max 1400x900)
        window_width = min(int(screen_width * 0.9), 1400)
        window_height = min(int(screen_height * 0.85), 900)
        
        # Set minimum size to ensure usability
        self.root.minsize(1000, 700)
        
        # Center window on screen with responsive sizing
        self.root.update_idletasks()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2) - 20  # Slightly higher
        
        # Ensure window doesn't go off-screen
        x = max(10, min(x, screen_width - window_width - 10))
        y = max(10, min(y, screen_height - window_height - 40))
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window resizable with proper constraints
        self.root.resizable(True, True)
        
        # Configure grid weight for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_styles(self):
        """Setup enhanced styling"""
        # Configure TTK styles
        ModernStyle.configure_ttk_styles(self.root)
        
        # Configure regular tk widgets
        ModernStyle.configure_tk_widgets(self.root)
    
    def create_widgets(self):
        """Create main GUI widgets"""
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
    
    def create_header(self):
        """Create modern header section with enhanced styling"""
        # Header with dark background for better contrast
        header_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['header_bg'], height=120)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Inner frame for centering content
        inner_frame = tk.Frame(header_frame, bg=ModernStyle.COLORS['header_bg'])
        inner_frame.pack(expand=True)
        
        # Title with larger font and better spacing
        title_label = tk.Label(
            inner_frame,
            text="🔍 ReadySearch Advanced GUI v2.0",
            font=ModernStyle.FONTS['title'],
            bg=ModernStyle.COLORS['header_bg'],
            fg=ModernStyle.COLORS['text_white']
        )
        title_label.pack(pady=(25, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            inner_frame,
            text="Professional Name Search Tool with Enhanced Export Capabilities",
            font=ModernStyle.FONTS['subtitle'],
            bg=ModernStyle.COLORS['header_bg'],
            fg=ModernStyle.COLORS['text_white']
        )
        subtitle_label.pack(pady=(0, 25))
    
    def create_main_content(self):
        """Create enhanced main content area with modern styling"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=ModernStyle.COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create paned window for resizable sections
        self.paned_window = tk.PanedWindow(
            main_container, 
            orient=tk.HORIZONTAL,
            bg=ModernStyle.COLORS['background'],
            sashwidth=8,
            sashrelief='flat',
            borderwidth=0
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Search input (narrower)
        self.create_search_panel(self.paned_window)
        
        # Right panel - Results display (wider)
        self.create_results_panel(self.paned_window)
    
    def create_search_panel(self, parent):
        """Create enhanced search input panel with modern styling"""
        # Create frame for search panel
        search_frame = tk.Frame(parent, bg=ModernStyle.COLORS['surface'], relief='solid', borderwidth=1)
        parent.add(search_frame, width=450, minsize=400)
        
        # Search section title
        search_title = tk.Label(
            search_frame,
            text="🔍 Search Configuration",
            font=ModernStyle.FONTS['heading'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_primary']
        )
        search_title.pack(pady=(15, 10), padx=20)
        
        # Scrollable frame for search content
        canvas = tk.Canvas(search_frame, bg=ModernStyle.COLORS['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(search_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernStyle.COLORS['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        
        # Quick add section
        quick_add_frame = ttk.LabelFrame(
            scrollable_frame, 
            text="✨ Quick Add Names", 
            padding="15",
            style='Modern.TLabelframe'
        )
        quick_add_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Name input
        ttk.Label(quick_add_frame, text="Name:", style='Body.TLabel').pack(anchor=tk.W)
        self.quick_name_entry = ttk.Entry(
            quick_add_frame, 
            font=ModernStyle.FONTS['body_large'],
            style='Modern.TEntry'
        )
        self.quick_name_entry.pack(fill=tk.X, pady=(3, 8))
        
        # Birth year input
        year_frame = ttk.Frame(quick_add_frame)
        year_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(year_frame, text="Birth Year (optional):", style='Body.TLabel').pack(side=tk.LEFT)
        self.quick_year_entry = ttk.Entry(
            year_frame,
            width=10,
            font=ModernStyle.FONTS['body_large'],
            style='Modern.TEntry'
        )
        self.quick_year_entry.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Buttons in a row
        btn_frame = ttk.Frame(quick_add_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        add_btn = ttk.Button(
            btn_frame,
            text="➕ Add to List",
            style='Secondary.TButton',
            command=self.add_name_to_list
        )
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        test_data_btn = ttk.Button(
            btn_frame,
            text="📝 Load Test Data",
            style='Warning.TButton',
            command=self.load_test_data
        )
        test_data_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Search options section
        options_frame = ttk.LabelFrame(
            scrollable_frame,
            text="🎯 Search Options",
            padding="15",
            style='Modern.TLabelframe'
        )
        options_frame.pack(fill=tk.X, pady=(0, 15))

        # Exact matching checkbox
        self.exact_matching_var = tk.BooleanVar(value=False)
        exact_matching_checkbox = ttk.Checkbutton(
            options_frame,
            text="Require EXACT matching for first names",
            variable=self.exact_matching_var,
            style='Modern.TCheckbutton'
        )
        exact_matching_checkbox.pack(anchor=tk.W, pady=(0, 5))

        # Explanation label
        explanation_label = ttk.Label(
            options_frame,
            text="(Recommended: OFF for better results)",
            style='Muted.TLabel',
            font=ModernStyle.FONTS['small']
        )
        explanation_label.pack(anchor=tk.W)
        
        # Batch search section
        batch_frame = ttk.LabelFrame(
            scrollable_frame, 
            text="📁 Batch Search", 
            padding="15",
            style='Modern.TLabelframe'
        )
        batch_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Instructions
        instructions_label = ttk.Label(
            batch_frame, 
            text="Enter names (one per line or semicolon-separated):",
            style='Body.TLabel'
        )
        instructions_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Batch input text area
        text_frame = tk.Frame(batch_frame, bg=ModernStyle.COLORS['surface'])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Text widget with scrollbar
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.batch_text = tk.Text(
            text_frame,
            height=8,
            font=ModernStyle.FONTS['body'],
            borderwidth=2,
            relief='solid',
            bg=ModernStyle.COLORS['input_bg'],
            fg=ModernStyle.COLORS['text_primary'],
            insertbackground=ModernStyle.COLORS['text_primary'],
            selectbackground=ModernStyle.COLORS['primary_light'],
            selectforeground='white',
            yscrollcommand=text_scroll.set
        )
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.batch_text.yview)
        
        # Prepopulate with test data
        test_data = ("Andro Cutuk,1975\n"
                    "Anthony Bek,1993\n"
                    "Ghafoor Jaggi Nadery,1978")
        self.batch_text.insert(tk.END, test_data)
        
        # Batch search buttons
        batch_btn_frame = ttk.Frame(batch_frame)
        batch_btn_frame.pack(fill=tk.X)
        
        # Main search button
        batch_search_btn = ttk.Button(
            batch_btn_frame,
            text="🚀 Start Batch Search",
            style='Primary.TButton',
            command=self.batch_search
        )
        batch_search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        clear_btn = ttk.Button(
            batch_btn_frame,
            text="🗑️ Clear",
            style='Secondary.TButton',
            command=self.clear_batch_input
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Load file button
        load_file_btn = ttk.Button(
            batch_btn_frame,
            text="📁 Load File",
            style='Secondary.TButton',
            command=self.load_names_file
        )
        load_file_btn.pack(side=tk.LEFT)
    
    def create_results_panel(self, parent):
        """Create enhanced results display panel with modern styling"""
        # Create frame for results panel
        results_frame = tk.Frame(parent, bg=ModernStyle.COLORS['surface'], relief='solid', borderwidth=1)
        parent.add(results_frame, width=800, minsize=600)
        
        # Results section title
        results_title = tk.Label(
            results_frame,
            text="📊 Search Results & Export",
            font=ModernStyle.FONTS['heading'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_primary']
        )
        results_title.pack(pady=(15, 10), padx=20)
        
        # Controls frame
        controls_frame = tk.Frame(results_frame, bg=ModernStyle.COLORS['surface'])
        controls_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Export section
        export_label = tk.Label(
            controls_frame,
            text="📤 Export Options:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_primary']
        )
        export_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Export buttons frame
        export_frame = ttk.Frame(controls_frame)
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export buttons
        export_json_btn = ttk.Button(
            export_frame,
            text="📄 JSON (Full Data)",
            style='Success.TButton',
            command=lambda: self.export_results('json')
        )
        export_json_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_csv_btn = ttk.Button(
            export_frame,
            text="📊 CSV (Spreadsheet)",
            style='Success.TButton',
            command=lambda: self.export_results('csv')
        )
        export_csv_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_txt_btn = ttk.Button(
            export_frame,
            text="📝 TXT (Report)",
            style='Success.TButton',
            command=lambda: self.export_results('txt')
        )
        export_txt_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button on the right
        clear_results_btn = ttk.Button(
            export_frame,
            text="🗑️ Clear All Results",
            style='Danger.TButton',
            command=self.clear_results
        )
        clear_results_btn.pack(side=tk.RIGHT)
        
        # Results display
        self.create_results_display(results_frame)
    
    def create_results_display(self, parent):
        """Create enhanced results display widget with modern styling"""
        # Create notebook for different views
        self.results_notebook = ttk.Notebook(parent, style='Modern.TNotebook')
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Summary tab
        self.create_summary_tab()
        
        # Detailed results tab
        self.create_detailed_tab()
    
    def create_summary_tab(self):
        """Create enhanced summary results tab with modern styling"""
        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="📈 Summary")
        
        # Create tree container with proper layout
        tree_container = tk.Frame(summary_frame, bg=ModernStyle.COLORS['surface'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollbars first
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        # Summary tree view
        columns = ('Name', 'Status', 'Matches', 'Duration', 'Category', 'Details')
        self.summary_tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show='headings', 
            height=20,
            style='Modern.Treeview',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Configure scrollbars
        vsb.config(command=self.summary_tree.yview)
        hsb.config(command=self.summary_tree.xview)
        
        # Configure columns with better sizing
        self.summary_tree.heading('Name', text='👤 Name')
        self.summary_tree.heading('Status', text='📊 Status')
        self.summary_tree.heading('Matches', text='🔍 Matches')
        self.summary_tree.heading('Duration', text='⏱️ Duration')
        self.summary_tree.heading('Category', text='📋 Category')
        self.summary_tree.heading('Details', text='📄 Details')
        
        # Column widths
        self.summary_tree.column('Name', width=200, minwidth=150)
        self.summary_tree.column('Status', width=120, minwidth=80)
        self.summary_tree.column('Matches', width=100, minwidth=60)
        self.summary_tree.column('Duration', width=100, minwidth=80)
        self.summary_tree.column('Category', width=150, minwidth=100)
        self.summary_tree.column('Details', width=180, minwidth=120)
        
        # Layout using grid for better control
        self.summary_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
    
    def create_detailed_tab(self):
        """Create enhanced detailed results tab with modern styling"""
        detailed_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(detailed_frame, text="🔍 Detailed")
        
        # Text widget with scrollbar
        text_frame = tk.Frame(detailed_frame, bg=ModernStyle.COLORS['surface'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Detailed results text area
        self.detailed_text = tk.Text(
            text_frame,
            font=ModernStyle.FONTS['code'],
            wrap=tk.WORD,
            borderwidth=2,
            relief='solid',
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_primary'],
            selectbackground=ModernStyle.COLORS['primary_light'],
            selectforeground='white',
            yscrollcommand=text_scroll.set
        )
        self.detailed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.detailed_text.yview)
    
    def create_status_bar(self):
        """Create enhanced status bar with modern styling"""
        status_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['surface_alt'], height=40, relief='solid', borderwidth=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Ready for searches")
        
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface_alt'],
            fg=ModernStyle.COLORS['text_primary']
        )
        status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Results count
        self.results_count_var = tk.StringVar()
        self.results_count_var.set("📊 Results: 0")
        
        results_count_label = tk.Label(
            status_frame,
            textvariable=self.results_count_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface_alt'],
            fg=ModernStyle.COLORS['text_primary']
        )
        results_count_label.pack(side=tk.RIGHT, padx=15, pady=8)
    
    def add_name_to_list(self):
        """Add name from quick input to batch list (NEW functionality)"""
        name = self.quick_name_entry.get().strip()
        year = self.quick_year_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Input Required", "Please enter a name to add.")
            return
        
        # Format the entry
        if year:
            try:
                year_int = int(year)
                entry = f"{name},{year_int}"
            except ValueError:
                messagebox.showerror("Invalid Year", "Birth year must be a number.")
                return
        else:
            entry = name
        
        # Add to batch text area
        current_text = self.batch_text.get("1.0", tk.END).strip()
        if current_text:
            self.batch_text.insert(tk.END, f"\n{entry}")
        else:
            self.batch_text.insert(tk.END, entry)
        
        # Clear quick input fields
        self.quick_name_entry.delete(0, tk.END)
        self.quick_year_entry.delete(0, tk.END)
        
        # Show success message
        messagebox.showinfo("Added", f"Added '{entry}' to search list.")
    
    def load_test_data(self):
        """Load the specific test data requested by user"""
        test_data = ("Andro Cutuk,1975\n"
                    "Anthony Bek,1993\n"  
                    "Ghafoor Jaggi Nadery,1978")
        
        # Clear existing content and load test data
        self.batch_text.delete("1.0", tk.END)
        self.batch_text.insert(tk.END, test_data)
        
        messagebox.showinfo("Test Data Loaded", "Test data has been loaded successfully!")
    
    def quick_search(self):
        """Perform quick search using the quick add inputs"""
        name = self.quick_name_entry.get().strip()
        birth_year_str = self.quick_year_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a name to search.")
            return
        
        # Parse birth year
        birth_year = None
        if birth_year_str:
            try:
                birth_year = int(birth_year_str)
            except ValueError:
                messagebox.showerror("Error", "Birth year must be a number.")
                return
        
        # Create search record with exact matching preference
        search_record = SearchRecord(name=name, birth_year=birth_year)
        search_record.exact_matching = self.exact_matching_var.get()
        
        # Perform search in thread
        self.perform_search_threaded([search_record])
        
        # Clear the input fields after search
        self.quick_name_entry.delete(0, tk.END)
        self.quick_year_entry.delete(0, tk.END)
    
    def batch_search(self):
        """Perform batch search"""
        batch_text = self.batch_text.get("1.0", tk.END).strip()
        
        if not batch_text:
            messagebox.showerror("Error", "Please enter names to search.")
            return
        
        # Parse names
        search_records = self.parse_batch_input(batch_text)
        
        if not search_records:
            messagebox.showerror("Error", "No valid names found in input.")
            return
        
        # Apply exact matching preference to all records
        exact_matching = self.exact_matching_var.get()
        for record in search_records:
            record.exact_matching = exact_matching
        
        # Confirm batch search
        if len(search_records) > 5:
            if not messagebox.askyesno(
                "Confirm Batch Search",
                f"This will search for {len(search_records)} names. Continue?"
            ):
                return
        
        # Perform search in thread
        self.perform_search_threaded(search_records)
    
    def parse_batch_input(self, text: str) -> List[SearchRecord]:
        """Parse batch input text into search records"""
        search_records = []
        
        # Split by lines and semicolons
        lines = text.replace(';', '\n').split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Example'):
                continue
            
            if ',' in line:
                parts = line.split(',', 1)
                name = parts[0].strip()
                try:
                    birth_year = int(parts[1].strip())
                    search_records.append(SearchRecord(name=name, birth_year=birth_year))
                except ValueError:
                    search_records.append(SearchRecord(name=line))
            else:
                search_records.append(SearchRecord(name=line))
        
        return search_records
    
    def perform_search_threaded(self, search_records: List[SearchRecord]):
        """Perform search in a separate thread"""
        def search_thread():
            try:
                # Show progress window
                progress_window = SearchProgressWindow(self.root, len(search_records))
                
                # Update status with enhanced visual feedback
                self.status_var.set("🔍 Searching in progress...")
                self.root.update()
                
                # Perform searches
                results = []
                for i, search_record in enumerate(search_records):
                    progress_window.update_progress(
                        i + 1, len(search_records),
                        search_record.name,
                        f"Searching for {search_record.name}..."
                    )
                    
                    # Run async search
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    search_result = loop.run_until_complete(
                        self.production_cli.search_person(search_record)
                    )
                    loop.close()
                    
                    # Convert to GUI result
                    gui_result = GUISearchResult(
                        name=search_record.name,
                        status=search_result['status'],
                        search_duration=search_result['search_duration'],
                        matches_found=search_result['matches_found'],
                        exact_matches=search_result['exact_matches'],
                        partial_matches=search_result['partial_matches'],
                        match_category=search_result['match_category'],
                        match_reasoning=search_result['match_reasoning'],
                        detailed_results=search_result['detailed_results'],
                        timestamp=datetime.now().isoformat(),
                        birth_year=search_record.birth_year,
                        error=search_result.get('error')
                    )
                    
                    results.append(gui_result)
                    
                    # Update progress window
                    status_icon = "✅" if gui_result.matches_found > 0 else "⭕" if gui_result.status != 'Error' else "❌"
                    progress_window.add_result_text(
                        f"{status_icon} {gui_result.name}: {gui_result.status} "
                        f"({gui_result.matches_found} matches, {gui_result.search_duration:.2f}s)"
                    )
                
                progress_window.close()
                
                # Update results in main thread
                self.root.after(0, lambda: self.update_results_display(results))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Search Error", str(e)))
                self.root.after(0, lambda: self.status_var.set("❌ Search failed - Ready for new search"))
        
        # Start search thread
        threading.Thread(target=search_thread, daemon=True).start()
    
    def update_results_display(self, new_results: List[GUISearchResult]):
        """Update results display with new results"""
        # Add to results list
        self.search_results.extend(new_results)
        
        # Update enhanced summary tree with additional details column
        for result in new_results:
            # Format details column (fixed: show only exact if exact matches exist)
            if result.exact_matches > 0:
                details = f"{result.exact_matches} exact"
            elif result.partial_matches > 0:
                details = f"{result.partial_matches} partial"
            else:
                details = "No matches"
            
            self.summary_tree.insert('', tk.END, values=(
                result.name,
                result.status,
                result.matches_found,
                f"{result.search_duration:.2f}",
                result.match_category,
                details
            ))
        
        # Update detailed view
        self.update_detailed_view()
        
        # Update status with enhanced visual feedback
        self.status_var.set("✅ Search completed successfully")
        self.results_count_var.set(f"📊 Results: {len(self.search_results)}")
        
        # Show completion message
        matches = len([r for r in new_results if r.matches_found > 0])
        messagebox.showinfo(
            "Search Complete",
            f"Completed {len(new_results)} searches.\n"
            f"Found matches: {matches}\n"
            f"No matches: {len(new_results) - matches}"
        )
    
    def update_detailed_view(self):
        """Update detailed results view"""
        self.detailed_text.delete("1.0", tk.END)
        
        if not self.search_results:
            self.detailed_text.insert(tk.END, "No search results available.\n")
            return
        
        # Summary statistics
        total_searches = len(self.search_results)
        matches = [r for r in self.search_results if r.matches_found > 0]
        no_matches = [r for r in self.search_results if r.matches_found == 0 and r.status != 'Error']
        errors = [r for r in self.search_results if r.status == 'Error']
        avg_duration = sum(r.search_duration for r in self.search_results) / total_searches
        
        self.detailed_text.insert(tk.END, "READYSEARCH GUI - SESSION SUMMARY\n")
        self.detailed_text.insert(tk.END, "=" * 50 + "\n\n")
        
        self.detailed_text.insert(tk.END, f"Total Searches: {total_searches}\n")
        self.detailed_text.insert(tk.END, f"Found Matches: {len(matches)}\n")
        self.detailed_text.insert(tk.END, f"No Matches: {len(no_matches)}\n")
        self.detailed_text.insert(tk.END, f"Errors: {len(errors)}\n")
        self.detailed_text.insert(tk.END, f"Success Rate: {((len(matches) + len(no_matches))/total_searches*100):.1f}%\n")
        self.detailed_text.insert(tk.END, f"Average Duration: {avg_duration:.2f}s\n\n")
        
        # Detailed results
        self.detailed_text.insert(tk.END, "DETAILED RESULTS:\n")
        self.detailed_text.insert(tk.END, "-" * 30 + "\n\n")
        
        for i, result in enumerate(self.search_results, 1):
            status_icon = "✅" if result.matches_found > 0 else "⭕" if result.status != 'Error' else "❌"
            
            self.detailed_text.insert(tk.END, f"{i}. {status_icon} {result.name}\n")
            self.detailed_text.insert(tk.END, f"   Status: {result.status}\n")
            self.detailed_text.insert(tk.END, f"   Duration: {result.search_duration:.2f}s\n")
            self.detailed_text.insert(tk.END, f"   Matches: {result.matches_found}\n")
            self.detailed_text.insert(tk.END, f"   Category: {result.match_category}\n")
            
            if result.birth_year:
                self.detailed_text.insert(tk.END, f"   Birth Year: {result.birth_year}\n")
            
            if result.detailed_results:
                self.detailed_text.insert(tk.END, "   Detailed Matches:\n")
                for match in result.detailed_results[:5]:  # Show first 5
                    self.detailed_text.insert(tk.END, f"     • {match['matched_name']} ({match['match_type']})\n")
                if len(result.detailed_results) > 5:
                    self.detailed_text.insert(tk.END, f"     ... and {len(result.detailed_results) - 5} more\n")
            
            if result.error:
                self.detailed_text.insert(tk.END, f"   Error: {result.error}\n")
            
            self.detailed_text.insert(tk.END, "\n")
    
    def export_results(self, format_type: str):
        """Export results in specified format"""
        if not self.search_results:
            messagebox.showwarning("No Data", "No search results to export.")
            return
        
        # Get filename from user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"readysearch_results_{timestamp}"
        
        if format_type == 'json':
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialvalue=f"{default_filename}.json"
            )
        elif format_type == 'csv':
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"{default_filename}.csv"
            )
        elif format_type == 'txt':
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=f"{default_filename}.txt"
            )
        else:
            messagebox.showerror("Error", f"Unsupported format: {format_type}")
            return
        
        if not filename:
            return
        
        try:
            if format_type == 'json':
                self.export_json(filename)
            elif format_type == 'csv':
                self.export_csv(filename)
            elif format_type == 'txt':
                self.export_txt(filename)
            
            messagebox.showinfo("Export Complete", f"Results exported successfully to:\n{filename}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Would you like to open the exported file?"):
                webbrowser.open(filename)
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def export_json(self, filename: str):
        """Export comprehensive results as JSON with detailed match information"""
        # Calculate summary statistics
        total_searches = len(self.search_results)
        total_matches = sum(r.matches_found for r in self.search_results)
        exact_matches = sum(r.exact_matches for r in self.search_results)
        partial_matches = sum(r.partial_matches for r in self.search_results)
        successful_searches = len([r for r in self.search_results if r.status != 'Error'])
        
        data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'tool_version': 'ReadySearch Advanced GUI v2.0 Enhanced',
                'export_type': 'Comprehensive Search Results with Location Data',
                'total_searches': total_searches,
                'successful_searches': successful_searches,
                'total_matches_found': total_matches,
                'exact_matches_total': exact_matches,
                'partial_matches_total': partial_matches,
                'success_rate': f"{(successful_searches/total_searches*100):.1f}%" if total_searches > 0 else "0%"
            },
            'comprehensive_results': []
        }
        
        for r in self.search_results:
            # Enhanced result structure with comprehensive details
            result_data = {
                'search_info': {
                    'name': r.name,
                    'birth_year': r.birth_year,
                    'search_timestamp': r.timestamp,
                    'search_duration_seconds': r.search_duration
                },
                'match_summary': {
                    'status': r.status,
                    'total_results_found': r.matches_found,
                    'exact_matches': r.exact_matches,
                    'partial_matches': r.partial_matches,
                    'match_category': r.match_category,
                    'match_reasoning': r.match_reasoning,
                    'has_location_data': any('location' in str(match).lower() or 'address' in str(match).lower() 
                                           for match in r.detailed_results) if r.detailed_results else False
                },
                'detailed_matches': [],
                'error_info': r.error if r.error else None
            }
            
            # Process detailed results with location extraction
            if r.detailed_results:
                for i, match in enumerate(r.detailed_results, 1):
                    detailed_match = {
                        'match_number': i,
                        'matched_name': match.get('matched_name', 'Unknown'),
                        'match_type': match.get('match_type', 'Unknown'),
                        'confidence': match.get('confidence', 0.0),
                        'date_of_birth': match.get('date_of_birth', 'Unknown'),
                        'additional_details': {}
                    }
                    
                    # Extract location data if available
                    location_fields = ['address', 'location', 'city', 'state', 'postcode', 'suburb', 'street']
                    for field in location_fields:
                        if field in match:
                            detailed_match['additional_details'][field] = match[field]
                    
                    # Include any other fields that might contain location or additional info
                    for key, value in match.items():
                        if key not in ['matched_name', 'match_type', 'confidence', 'date_of_birth'] and key not in location_fields:
                            detailed_match['additional_details'][key] = value
                    
                    result_data['detailed_matches'].append(detailed_match)
            
            data['comprehensive_results'].append(result_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_csv(self, filename: str):
        """Export comprehensive results as CSV with detailed match information and location data"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Enhanced header with comprehensive information
            writer.writerow([
                'Search_Name', 'Birth_Year', 'Status', 'Search_Duration_Seconds', 
                'Total_Results_Found', 'Exact_Matches', 'Partial_Matches', 
                'Match_Category', 'Match_Reasoning', 'Search_Timestamp',
                'Match_Number', 'Matched_Name', 'Match_Type', 'Match_Confidence',
                'Date_of_Birth', 'Location_Address', 'Location_City', 'Location_State',
                'Location_Postcode', 'Additional_Details', 'Error_Info'
            ])
            
            # Enhanced data rows with detailed match information
            for result in self.search_results:
                if result.detailed_results:
                    # Write one row per detailed match
                    for i, match in enumerate(result.detailed_results, 1):
                        # Extract location data
                        location_address = match.get('address', match.get('location', ''))
                        location_city = match.get('city', match.get('suburb', ''))
                        location_state = match.get('state', '')
                        location_postcode = match.get('postcode', '')
                        
                        # Collect additional details (excluding already captured fields)
                        additional_details = {}
                        excluded_fields = {'matched_name', 'match_type', 'confidence', 'date_of_birth', 
                                         'address', 'location', 'city', 'suburb', 'state', 'postcode'}
                        
                        for key, value in match.items():
                            if key not in excluded_fields:
                                additional_details[key] = value
                        
                        additional_details_str = '; '.join([f"{k}: {v}" for k, v in additional_details.items()]) if additional_details else ''
                        
                        writer.writerow([
                            result.name,
                            result.birth_year or '',
                            result.status,
                            result.search_duration,
                            result.matches_found,
                            result.exact_matches,
                            result.partial_matches,
                            result.match_category,
                            result.match_reasoning,
                            result.timestamp,
                            i,
                            match.get('matched_name', ''),
                            match.get('match_type', ''),
                            match.get('confidence', ''),
                            match.get('date_of_birth', ''),
                            location_address,
                            location_city,
                            location_state,
                            location_postcode,
                            additional_details_str,
                            result.error or ''
                        ])
                else:
                    # Write one row for searches with no detailed results
                    writer.writerow([
                        result.name,
                        result.birth_year or '',
                        result.status,
                        result.search_duration,
                        result.matches_found,
                        result.exact_matches,
                        result.partial_matches,
                        result.match_category,
                        result.match_reasoning,
                        result.timestamp,
                        '',  # Match_Number
                        '',  # Matched_Name
                        '',  # Match_Type
                        '',  # Match_Confidence
                        '',  # Date_of_Birth
                        '',  # Location_Address
                        '',  # Location_City
                        '',  # Location_State
                        '',  # Location_Postcode
                        '',  # Additional_Details
                        result.error or ''
                    ])
    
    def export_txt(self, filename: str):
        """Export comprehensive results as formatted text with detailed match information and location data"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Enhanced header
            f.write("READYSEARCH ADVANCED GUI v2.0 - COMPREHENSIVE SEARCH RESULTS REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tool Version: ReadySearch Advanced GUI v2.0 Enhanced\n")
            f.write(f"Report Type: Comprehensive Results with Location Data\n\n")
            
            # Summary statistics
            total_searches = len(self.search_results)
            total_matches = sum(r.matches_found for r in self.search_results)
            exact_matches = sum(r.exact_matches for r in self.search_results)
            partial_matches = sum(r.partial_matches for r in self.search_results)
            successful_searches = len([r for r in self.search_results if r.status != 'Error'])
            
            f.write("📊 SUMMARY STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Searches Performed: {total_searches}\n")
            f.write(f"Successful Searches: {successful_searches}\n")
            f.write(f"Total Matches Found: {total_matches}\n")
            f.write(f"Exact Matches: {exact_matches}\n")
            f.write(f"Partial Matches: {partial_matches}\n")
            f.write(f"Success Rate: {(successful_searches/total_searches*100):.1f}%\n" if total_searches > 0 else "Success Rate: 0%\n")
            f.write("\n")
            
            # Detailed results
            f.write("🔍 DETAILED SEARCH RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            for i, result in enumerate(self.search_results, 1):
                f.write(f"{i}. 👤 {result.name}\n")
                f.write("=" * 60 + "\n")
                
                # Basic search information
                f.write("📋 SEARCH INFORMATION:\n")
                f.write(f"   Name Searched: {result.name}\n")
                if result.birth_year:
                    f.write(f"   Birth Year: {result.birth_year}\n")
                f.write(f"   Search Duration: {result.search_duration:.2f} seconds\n")
                f.write(f"   Search Timestamp: {result.timestamp}\n")
                f.write("\n")
                
                # Match summary
                f.write("📊 MATCH SUMMARY:\n")
                f.write(f"   Status: {result.status}\n")
                f.write(f"   Total Results Found: {result.matches_found}\n")
                f.write(f"   Exact Matches: {result.exact_matches}\n")
                f.write(f"   Partial Matches: {result.partial_matches}\n")
                f.write(f"   Match Category: {result.match_category}\n")
                f.write(f"   Match Reasoning: {result.match_reasoning}\n")
                f.write("\n")
                
                # Detailed matches with location data
                if result.detailed_results:
                    f.write("🗂️ DETAILED MATCH INFORMATION:\n")
                    for j, match in enumerate(result.detailed_results, 1):
                        f.write(f"   Match #{j}:\n")
                        f.write(f"      Name: {match.get('matched_name', 'Unknown')}\n")
                        f.write(f"      Match Type: {match.get('match_type', 'Unknown')}\n")
                        f.write(f"      Confidence: {match.get('confidence', 'Unknown')}\n")
                        f.write(f"      Date of Birth: {match.get('date_of_birth', 'Unknown')}\n")
                        
                        # Location information
                        location_data = []
                        location_fields = ['address', 'location', 'city', 'suburb', 'state', 'postcode']
                        for field in location_fields:
                            if field in match and match[field]:
                                location_data.append(f"{field.title()}: {match[field]}")
                        
                        if location_data:
                            f.write("      📍 Location Information:\n")
                            for location_item in location_data:
                                f.write(f"         {location_item}\n")
                        
                        # Additional details
                        additional_details = {}
                        excluded_fields = {'matched_name', 'match_type', 'confidence', 'date_of_birth'} | set(location_fields)
                        for key, value in match.items():
                            if key not in excluded_fields:
                                additional_details[key] = value
                        
                        if additional_details:
                            f.write("      ℹ️ Additional Details:\n")
                            for key, value in additional_details.items():
                                f.write(f"         {key.replace('_', ' ').title()}: {value}\n")
                        
                        f.write("\n")
                else:
                    f.write("   No detailed match information available.\n\n")
                
                # Error information
                if result.error:
                    f.write(f"❌ ERROR INFORMATION:\n")
                    f.write(f"   Error: {result.error}\n\n")
                
                f.write("-" * 60 + "\n\n")
            
            # Footer
            f.write("📄 END OF REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Report generated by ReadySearch Advanced GUI v2.0 Enhanced\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    
    def clear_results(self):
        """Clear all search results"""
        if not self.search_results:
            messagebox.showinfo("No Data", "No results to clear.")
            return
        
        if messagebox.askyesno("Clear Results", "Are you sure you want to clear all results?"):
            self.search_results.clear()
            
            # Clear displays
            for item in self.summary_tree.get_children():
                self.summary_tree.delete(item)
            
            self.detailed_text.delete("1.0", tk.END)
            self.detailed_text.insert(tk.END, "No search results available.\n")
            
            # Update status with enhanced visual feedback
            self.results_count_var.set("📊 Results: 0")
            messagebox.showinfo("✅ Cleared", "All results have been cleared successfully.")
    
    def clear_batch_input(self):
        """Clear batch input text and reload test data"""
        self.batch_text.delete("1.0", tk.END)
        # Reload the test data as default
        test_data = ("Andro Cutuk,1975\n"
                    "Anthony Bek,1993\n"
                    "Ghafoor Jaggi Nadery,1978")
        self.batch_text.insert(tk.END, test_data)
        messagebox.showinfo("Cleared", "Batch input cleared and test data reloaded.")
    
    def load_names_file(self):
        """Load names from a file"""
        filename = filedialog.askopenfilename(
            title="Load Names File",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clear current content and insert loaded content
            self.batch_text.delete("1.0", tk.END)
            self.batch_text.insert(tk.END, content)
            
            messagebox.showinfo("File Loaded", f"Names loaded from:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file:\n{str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = ReadySearchGUI()
    app.run()

if __name__ == "__main__":
    main()