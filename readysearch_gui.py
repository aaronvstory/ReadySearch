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
    """Modern styling configuration for the GUI"""
    
    # Color palette
    COLORS = {
        'primary': '#2C3E50',      # Dark blue-gray
        'secondary': '#3498DB',    # Blue
        'success': '#27AE60',      # Green
        'warning': '#F39C12',      # Orange
        'danger': '#E74C3C',       # Red
        'light': '#ECF0F1',        # Light gray
        'dark': '#34495E',         # Dark gray
        'white': '#FFFFFF',        # White
        'accent': '#9B59B6',       # Purple
        'info': '#17A2B8'          # Light blue
    }
    
    # Fonts
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'subtitle': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 8),
        'code': ('Consolas', 9)
    }
    
    @classmethod
    def configure_ttk_styles(cls, root):
        """Configure modern TTK styles"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure(
            'Primary.TButton',
            background=cls.COLORS['secondary'],
            foreground=cls.COLORS['white'],
            padding=(10, 5),
            font=cls.FONTS['body']
        )
        
        style.configure(
            'Success.TButton',
            background=cls.COLORS['success'],
            foreground=cls.COLORS['white'],
            padding=(10, 5),
            font=cls.FONTS['body']
        )
        
        style.configure(
            'Danger.TButton',
            background=cls.COLORS['danger'],
            foreground=cls.COLORS['white'],
            padding=(10, 5),
            font=cls.FONTS['body']
        )
        
        # Configure frame styles
        style.configure(
            'Card.TFrame',
            background=cls.COLORS['white'],
            relief='raised',
            borderwidth=1
        )
        
        # Configure label styles
        style.configure(
            'Title.TLabel',
            background=cls.COLORS['white'],
            foreground=cls.COLORS['primary'],
            font=cls.FONTS['title']
        )
        
        style.configure(
            'Subtitle.TLabel',
            background=cls.COLORS['white'],
            foreground=cls.COLORS['dark'],
            font=cls.FONTS['subtitle']
        )

class SearchProgressWindow:
    """Progress window for search operations"""
    
    def __init__(self, parent, total_searches):
        self.window = tk.Toplevel(parent)
        self.window.title("Search in Progress")
        self.window.geometry("500x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.total_searches = total_searches
        self.current_search = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup progress window UI"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔍 Searching in Progress",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Preparing search...",
            font=ModernStyle.FONTS['body']
        )
        self.status_label.pack(pady=(0, 10))
        
        # Current search info
        self.search_info_label = ttk.Label(
            main_frame,
            text="",
            font=ModernStyle.FONTS['small']
        )
        self.search_info_label.pack(pady=(0, 20))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            width=60,
            font=ModernStyle.FONTS['code']
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def update_progress(self, current, total, current_name="", status=""):
        """Update progress display"""
        self.current_search = current
        progress_percent = (current / total) * 100
        self.progress_var.set(progress_percent)
        
        self.status_label.config(text=status)
        self.search_info_label.config(
            text=f"Search {current} of {total}: {current_name}"
        )
        
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
        """Setup main window configuration"""
        self.root.title("ReadySearch Advanced GUI v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Configure icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_styles(self):
        """Setup modern styling"""
        ModernStyle.configure_ttk_styles(self.root)
        
        # Configure root background
        self.root.configure(bg=ModernStyle.COLORS['light'])
    
    def create_widgets(self):
        """Create main GUI widgets"""
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
    
    def create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Title and subtitle
        title_label = ttk.Label(
            header_frame,
            text="🔍 ReadySearch Advanced GUI",
            style='Title.TLabel'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Professional Name Search Tool with Export Capabilities",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 15))
    
    def create_main_content(self):
        """Create main content area"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create paned window for resizable sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Search input
        self.create_search_panel(paned_window)
        
        # Right panel - Results
        self.create_results_panel(paned_window)
    
    def create_search_panel(self, parent):
        """Create search input panel"""
        search_frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(search_frame, weight=1)
        
        # Search section title
        search_title = ttk.Label(
            search_frame,
            text="🔍 Search Configuration",
            style='Subtitle.TLabel'
        )
        search_title.pack(pady=(15, 10), padx=15)
        
        # Search input frame
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Quick search section
        quick_frame = ttk.LabelFrame(input_frame, text="Quick Search", padding="10")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name input
        ttk.Label(quick_frame, text="Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(quick_frame, font=ModernStyle.FONTS['body'])
        self.name_entry.pack(fill=tk.X, pady=(2, 5))
        
        # Birth year input
        ttk.Label(quick_frame, text="Birth Year (optional):").pack(anchor=tk.W)
        self.birth_year_entry = ttk.Entry(quick_frame, font=ModernStyle.FONTS['body'])
        self.birth_year_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Quick search button
        quick_search_btn = ttk.Button(
            quick_frame,
            text="🔍 Quick Search",
            style='Primary.TButton',
            command=self.quick_search
        )
        quick_search_btn.pack(fill=tk.X)
        
        # Batch search section
        batch_frame = ttk.LabelFrame(input_frame, text="Batch Search", padding="10")
        batch_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Batch input text area
        ttk.Label(batch_frame, text="Enter multiple names (one per line or semicolon-separated):").pack(anchor=tk.W)
        
        self.batch_text = scrolledtext.ScrolledText(
            batch_frame,
            height=8,
            font=ModernStyle.FONTS['body']
        )
        self.batch_text.pack(fill=tk.BOTH, expand=True, pady=(2, 10))
        
        # Example text
        example_text = ("Examples:\n"
                       "John Smith\n"
                       "Jane Doe,1985\n"
                       "Bob Jones;Alice Brown,1990")
        self.batch_text.insert(tk.END, example_text)
        
        # Batch search buttons frame
        batch_btn_frame = ttk.Frame(batch_frame)
        batch_btn_frame.pack(fill=tk.X)
        
        batch_search_btn = ttk.Button(
            batch_btn_frame,
            text="🚀 Batch Search",
            style='Primary.TButton',
            command=self.batch_search
        )
        batch_search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(
            batch_btn_frame,
            text="🗑️ Clear",
            command=self.clear_batch_input
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        load_file_btn = ttk.Button(
            batch_btn_frame,
            text="📁 Load File",
            command=self.load_names_file
        )
        load_file_btn.pack(side=tk.LEFT)
    
    def create_results_panel(self, parent):
        """Create results display panel"""
        results_frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(results_frame, weight=2)
        
        # Results section title
        results_title = ttk.Label(
            results_frame,
            text="📊 Search Results",
            style='Subtitle.TLabel'
        )
        results_title.pack(pady=(15, 10), padx=15)
        
        # Results controls frame
        controls_frame = ttk.Frame(results_frame)
        controls_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Export buttons
        export_json_btn = ttk.Button(
            controls_frame,
            text="📄 Export JSON",
            style='Success.TButton',
            command=lambda: self.export_results('json')
        )
        export_json_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_csv_btn = ttk.Button(
            controls_frame,
            text="📊 Export CSV",
            style='Success.TButton',
            command=lambda: self.export_results('csv')
        )
        export_csv_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_txt_btn = ttk.Button(
            controls_frame,
            text="📝 Export TXT",
            style='Success.TButton',
            command=lambda: self.export_results('txt')
        )
        export_txt_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_results_btn = ttk.Button(
            controls_frame,
            text="🗑️ Clear Results",
            style='Danger.TButton',
            command=self.clear_results
        )
        clear_results_btn.pack(side=tk.RIGHT)
        
        # Results display
        self.create_results_display(results_frame)
    
    def create_results_display(self, parent):
        """Create results display widget"""
        # Create notebook for different views
        self.results_notebook = ttk.Notebook(parent)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Summary tab
        self.create_summary_tab()
        
        # Detailed results tab
        self.create_detailed_tab()
    
    def create_summary_tab(self):
        """Create summary results tab"""
        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="📈 Summary")
        
        # Summary tree view
        columns = ('Name', 'Status', 'Matches', 'Duration', 'Category')
        self.summary_tree = ttk.Treeview(summary_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.summary_tree.heading('Name', text='Name')
        self.summary_tree.heading('Status', text='Status')
        self.summary_tree.heading('Matches', text='Matches')
        self.summary_tree.heading('Duration', text='Duration (s)')
        self.summary_tree.heading('Category', text='Category')
        
        self.summary_tree.column('Name', width=200)
        self.summary_tree.column('Status', width=100)
        self.summary_tree.column('Matches', width=80)
        self.summary_tree.column('Duration', width=100)
        self.summary_tree.column('Category', width=150)
        
        # Scrollbars
        summary_scroll_y = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary_tree.yview)
        summary_scroll_x = ttk.Scrollbar(summary_frame, orient=tk.HORIZONTAL, command=self.summary_tree.xview)
        self.summary_tree.configure(yscrollcommand=summary_scroll_y.set, xscrollcommand=summary_scroll_x.set)
        
        # Pack tree and scrollbars
        self.summary_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        summary_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_detailed_tab(self):
        """Create detailed results tab"""
        detailed_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(detailed_frame, text="🔍 Detailed")
        
        # Detailed results text area
        self.detailed_text = scrolledtext.ScrolledText(
            detailed_frame,
            font=ModernStyle.FONTS['code'],
            wrap=tk.WORD
        )
        self.detailed_text.pack(fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=ModernStyle.FONTS['small']
        )
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Results count
        self.results_count_var = tk.StringVar()
        self.results_count_var.set("Results: 0")
        
        results_count_label = ttk.Label(
            status_frame,
            textvariable=self.results_count_var,
            font=ModernStyle.FONTS['small']
        )
        results_count_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def quick_search(self):
        """Perform quick search"""
        name = self.name_entry.get().strip()
        birth_year_str = self.birth_year_entry.get().strip()
        
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
        
        # Create search record
        search_record = SearchRecord(name=name, birth_year=birth_year)
        
        # Perform search in thread
        self.perform_search_threaded([search_record])
    
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
                
                # Update status
                self.status_var.set("Searching...")
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
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        # Start search thread
        threading.Thread(target=search_thread, daemon=True).start()
    
    def update_results_display(self, new_results: List[GUISearchResult]):
        """Update results display with new results"""
        # Add to results list
        self.search_results.extend(new_results)
        
        # Update summary tree
        for result in new_results:
            self.summary_tree.insert('', tk.END, values=(
                result.name,
                result.status,
                result.matches_found,
                f"{result.search_duration:.2f}",
                result.match_category
            ))
        
        # Update detailed view
        self.update_detailed_view()
        
        # Update status
        self.status_var.set("Ready")
        self.results_count_var.set(f"Results: {len(self.search_results)}")
        
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
        """Export results as JSON"""
        data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'total_results': len(self.search_results),
                'tool_version': 'ReadySearch Advanced GUI v2.0'
            },
            'results': [
                {
                    'name': r.name,
                    'status': r.status,
                    'search_duration': r.search_duration,
                    'matches_found': r.matches_found,
                    'exact_matches': r.exact_matches,
                    'partial_matches': r.partial_matches,
                    'match_category': r.match_category,
                    'match_reasoning': r.match_reasoning,
                    'detailed_results': r.detailed_results,
                    'timestamp': r.timestamp,
                    'birth_year': r.birth_year,
                    'error': r.error
                }
                for r in self.search_results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_csv(self, filename: str):
        """Export results as CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Name', 'Status', 'Search Duration (s)', 'Matches Found',
                'Exact Matches', 'Partial Matches', 'Match Category',
                'Match Reasoning', 'Birth Year', 'Timestamp', 'Error'
            ])
            
            # Data rows
            for result in self.search_results:
                writer.writerow([
                    result.name,
                    result.status,
                    result.search_duration,
                    result.matches_found,
                    result.exact_matches,
                    result.partial_matches,
                    result.match_category,
                    result.match_reasoning,
                    result.birth_year or '',
                    result.timestamp,
                    result.error or ''
                ])
    
    def export_txt(self, filename: str):
        """Export results as formatted text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("READYSEARCH ADVANCED GUI - SEARCH RESULTS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Searches: {len(self.search_results)}\n\n")
            
            for i, result in enumerate(self.search_results, 1):
                f.write(f"{i}. {result.name}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Status: {result.status}\n")
                f.write(f"Duration: {result.search_duration:.2f}s\n")
                f.write(f"Matches Found: {result.matches_found}\n")
                f.write(f"Category: {result.match_category}\n")
                f.write(f"Reasoning: {result.match_reasoning}\n")
                
                if result.birth_year:
                    f.write(f"Birth Year: {result.birth_year}\n")
                
                if result.detailed_results:
                    f.write("Detailed Matches:\n")
                    for match in result.detailed_results:
                        f.write(f"  - {match['matched_name']} ({match['match_type']})\n")
                
                if result.error:
                    f.write(f"Error: {result.error}\n")
                
                f.write("\n")
    
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
            
            # Update status
            self.results_count_var.set("Results: 0")
            messagebox.showinfo("Cleared", "All results have been cleared.")
    
    def clear_batch_input(self):
        """Clear batch input text"""
        self.batch_text.delete("1.0", tk.END)
        example_text = ("Examples:\n"
                       "John Smith\n"
                       "Jane Doe,1985\n"
                       "Bob Jones;Alice Brown,1990")
        self.batch_text.insert(tk.END, example_text)
    
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