#!/usr/bin/env python3
"""
Enhanced ReadySearch CLI - Beautiful, structured, and feature-rich interface
"""

import asyncio
import sys
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os

# Rich for beautiful CLI output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.rule import Rule
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing rich for enhanced CLI...")
    os.system("pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.rule import Rule
    from rich.markdown import Markdown
    from rich.syntax import Syntax

# Import existing functionality
sys.path.append(str(Path(__file__).parent))
from config import Config
from readysearch_automation.input_loader import SearchRecord
from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

# Import the existing production CLI for search functionality
from production_cli import ProductionCLI

@dataclass
class SearchResult:
    """Enhanced search result with export capabilities"""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return asdict(self)

class EnhancedReadySearchCLI:
    """Enhanced CLI with beautiful interface and export capabilities"""
    
    def __init__(self):
        self.console = Console()
        self.production_cli = ProductionCLI()
        self.session_results: List[SearchResult] = []
        self.config = Config.get_config()
        
        # Color scheme
        self.colors = {
            'primary': '#00D4AA',      # Teal
            'secondary': '#FF6B6B',    # Coral
            'success': '#4ECDC4',      # Light teal
            'warning': '#FFE66D',      # Yellow
            'error': '#FF6B6B',        # Red
            'info': '#74C0FC',         # Light blue
            'accent': '#845EC2',       # Purple
            'text': '#F8F9FA',         # Light gray
            'muted': '#ADB5BD'         # Muted gray
        }
    
    def display_banner(self):
        """Display beautiful startup banner"""
        banner_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🔍 ReadySearch Enhanced CLI v2.0                          ║
║                                                              ║
║    Professional Name Search Tool with Advanced Features     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            Align.center(banner_text.strip()), 
            style=f"bold {self.colors['primary']}",
            padding=(1, 2)
        ))
    
    def display_main_menu(self):
        """Display enhanced main menu"""
        menu_options = [
            ("🔍", "Quick Search", "Search for names quickly"),
            ("📁", "Batch Search", "Upload file or enter multiple names"),
            ("📊", "View Results", "View current session results"),
            ("💾", "Export Data", "Export results in various formats"),
            ("⚙️", "Settings", "Configure search parameters"),
            ("📈", "Statistics", "View search statistics"),
            ("❓", "Help", "View help and documentation"),
            ("🚪", "Exit", "Exit the application")
        ]
        
        # Create menu table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Icon", style=f"bold {self.colors['accent']}")
        table.add_column("Option", style=f"bold {self.colors['primary']}")
        table.add_column("Description", style=self.colors['muted'])
        
        for i, (icon, option, desc) in enumerate(menu_options, 1):
            table.add_row(f"{i}. {icon}", option, desc)
        
        menu_panel = Panel(
            table,
            title="[bold]Main Menu[/bold]",
            title_align="center",
            style=self.colors['info']
        )
        
        self.console.print("\n")
        self.console.print(menu_panel)
        self.console.print("\n")
    
    def display_quick_search_interface(self):
        """Display quick search interface"""
        search_panel = Panel(
            "[bold]Quick Search Interface[/bold]\n\n"
            "Enter names in one of these formats:\n"
            "• Single name: [cyan]John Smith[/cyan]\n"
            "• With birth year: [cyan]John Smith,1990[/cyan]\n"
            "• Multiple names: [cyan]John Smith;Jane Doe,1985;Bob Jones[/cyan]\n\n"
            "Type [yellow]'back'[/yellow] to return to main menu",
            title="🔍 Quick Search",
            style=self.colors['info']
        )
        self.console.print(search_panel)
    
    async def perform_search(self, names_input: str) -> List[SearchResult]:
        """Perform search with beautiful progress display"""
        # Parse input into search records
        search_records = self.parse_names_input(names_input)
        
        if not search_records:
            self.console.print("[red]❌ No valid names found in input[/red]")
            return []
        
        results = []
        
        # Progress bar setup
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            for i, search_record in enumerate(search_records):
                task = progress.add_task(
                    f"Searching for {search_record.name}...", 
                    total=None
                )
                
                # Display current search info
                search_info = Panel(
                    f"[bold]{search_record.name}[/bold]"
                    + (f" (Born: {search_record.birth_year})" if search_record.birth_year else ""),
                    title=f"Search {i+1} of {len(search_records)}",
                    style=self.colors['primary']
                )
                self.console.print(search_info)
                
                # Perform the actual search using existing functionality
                start_time = time.time()
                search_result = await self.production_cli.search_person(search_record)
                
                # Convert to enhanced result format
                enhanced_result = SearchResult(
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
                
                results.append(enhanced_result)
                progress.remove_task(task)
                
                # Show immediate result
                self.display_search_result_summary(enhanced_result)
        
        return results
    
    def display_search_result_summary(self, result: SearchResult):
        """Display a beautiful summary of a single search result"""
        # Status styling
        if result.status == "Match":
            status_style = self.colors['success']
            status_icon = "✅"
        elif result.status == "No Match":
            status_style = self.colors['warning']
            status_icon = "⭕"
        else:
            status_style = self.colors['error']
            status_icon = "❌"
        
        # Create result table
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="bold")
        table.add_column("Value")
        
        table.add_row("Status", f"[{status_style}]{status_icon} {result.status}[/{status_style}]")
        table.add_row("Duration", f"{result.search_duration:.2f}s")
        table.add_row("Matches", str(result.matches_found))
        table.add_row("Category", f"[{status_style}]{result.match_category}[/{status_style}]")
        
        if result.detailed_results:
            matches_text = "\n".join([
                f"• {match['matched_name']} ({match['match_type']})"
                for match in result.detailed_results[:3]
            ])
            if len(result.detailed_results) > 3:
                matches_text += f"\n... and {len(result.detailed_results) - 3} more"
            table.add_row("Top Matches", matches_text)
        
        result_panel = Panel(
            table,
            title=f"[bold]{result.name}[/bold]",
            style=status_style
        )
        
        self.console.print(result_panel)
        self.console.print()
    
    def display_results_overview(self):
        """Display comprehensive results overview"""
        if not self.session_results:
            self.console.print("[yellow]No search results in current session[/yellow]")
            return
        
        # Summary statistics
        total_searches = len(self.session_results)
        matches = [r for r in self.session_results if r.matches_found > 0]
        no_matches = [r for r in self.session_results if r.matches_found == 0 and r.status != 'Error']
        errors = [r for r in self.session_results if r.status == 'Error']
        avg_duration = sum(r.search_duration for r in self.session_results) / total_searches
        
        # Create summary table
        summary_table = Table(title="Session Summary", style=self.colors['primary'])
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", justify="right")
        
        summary_table.add_row("Total Searches", str(total_searches))
        summary_table.add_row("Found Matches", f"[green]{len(matches)}[/green]")
        summary_table.add_row("No Matches", f"[yellow]{len(no_matches)}[/yellow]")
        summary_table.add_row("Errors", f"[red]{len(errors)}[/red]")
        summary_table.add_row("Success Rate", f"{((len(matches) + len(no_matches))/total_searches*100):.1f}%")
        summary_table.add_row("Avg Duration", f"{avg_duration:.2f}s")
        
        # Create detailed results table
        results_table = Table(title="Detailed Results", style=self.colors['info'])
        results_table.add_column("Name", style="bold")
        results_table.add_column("Status")
        results_table.add_column("Matches", justify="center")
        results_table.add_column("Duration", justify="right")
        results_table.add_column("Category")
        
        for result in self.session_results:
            status_color = "green" if result.matches_found > 0 else "yellow" if result.status != "Error" else "red"
            results_table.add_row(
                result.name,
                f"[{status_color}]{result.status}[/{status_color}]",
                str(result.matches_found),
                f"{result.search_duration:.2f}s",
                result.match_category
            )
        
        # Display both tables
        self.console.print("\n")
        self.console.print(summary_table)
        self.console.print("\n")
        self.console.print(results_table)
        self.console.print("\n")
    
    def export_results(self, format_type: str, filename: Optional[str] = None):
        """Export results in specified format"""
        if not self.session_results:
            self.console.print("[red]No results to export[/red]")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"readysearch_results_{timestamp}"
        
        try:
            if format_type.lower() == 'json':
                self.export_json(filename)
            elif format_type.lower() == 'csv':
                self.export_csv(filename)
            elif format_type.lower() == 'txt':
                self.export_txt(filename)
            else:
                self.console.print(f"[red]Unsupported format: {format_type}[/red]")
                return
            
            self.console.print(f"[green]✅ Results exported successfully to {filename}[/green]")
            
        except KeyboardInterrupt:
                    self.console.print("[yellow]⚠️ Keyboard interruption detected. Exiting gracefully...[/yellow]")
                    return
                except Exception as e:
            self.console.print(f"[red]❌ Export failed: {str(e)}[/red]")
    
    def export_json(self, filename: str):
        """Export results as JSON"""
        data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'total_results': len(self.session_results),
                'tool_version': 'Enhanced ReadySearch CLI v2.0'
            },
            'results': [result.to_dict() for result in self.session_results]
        }
        
        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_csv(self, filename: str):
        """Export results as CSV"""
        with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Name', 'Status', 'Search Duration (s)', 'Matches Found',
                'Exact Matches', 'Partial Matches', 'Match Category',
                'Match Reasoning', 'Birth Year', 'Timestamp', 'Error'
            ])
            
            # Data rows
            for result in self.session_results:
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
        with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
            f.write("READYSEARCH ENHANCED CLI - SEARCH RESULTS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Searches: {len(self.session_results)}\n\n")
            
            for i, result in enumerate(self.session_results, 1):
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
    
    def parse_names_input(self, names_input: str) -> List[SearchRecord]:
        """Parse names input into SearchRecord objects"""
        search_records = []
        names = names_input.split(';')
        
        for name_entry in names:
            name_entry = name_entry.strip()
            if not name_entry:
                continue
                
            if ',' in name_entry:
                parts = name_entry.split(',', 1)
                name = parts[0].strip()
                try:
                    birth_year = int(parts[1].strip())
                    search_records.append(SearchRecord(name=name, birth_year=birth_year))
                except ValueError:
                    search_records.append(SearchRecord(name=name_entry))
            else:
                search_records.append(SearchRecord(name=name_entry))
        
        return search_records
    
    def display_help(self):
        """Display help information"""
        help_content = """
# ReadySearch Enhanced CLI Help

## Quick Search
Enter names in these formats:
- **Single name**: `John Smith`
- **With birth year**: `John Smith,1990`
- **Multiple names**: `John Smith;Jane Doe,1985;Bob Jones`

## Features
- 🔍 **Real-time search** with progress indicators
- 📊 **Structured results** with beautiful formatting
- 💾 **Export capabilities** (JSON, CSV, TXT)
- 📈 **Session statistics** and performance metrics
- 🔄 **Continuous searching** without restarts

## Export Formats
- **JSON**: Complete data with metadata
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable report

## Tips
- Use birth years for more accurate results
- Check session statistics for performance insights
- Export results for record keeping
        """
        
        help_panel = Panel(
            Markdown(help_content.strip()),
            title="[bold]Help & Documentation[/bold]",
            style=self.colors['info']
        )
        
        self.console.print(help_panel)
    
    async def run(self):
        """Main application loop"""
        self.display_banner()
        
        while True:
            try:
                self.display_main_menu()
                
                choice = Prompt.ask(
                    "Select an option",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                    default="1"
                )
                
                self.console.print()
                
                if choice == "1":  # Quick Search
                    self.display_quick_search_interface()
                    names_input = Prompt.ask("Enter names to search")
                    
                    if names_input.lower() == 'back':
                        continue
                    
                    results = await self.perform_search(names_input)
                    self.session_results.extend(results)
                    
                    if results:
                        self.console.print(f"\n[green]✅ Completed {len(results)} searches[/green]")
                        if Confirm.ask("View detailed results?"):
                            self.display_results_overview()
                
                elif choice == "2":  # Batch Search
                    self.console.print("[yellow]Batch search functionality coming soon![/yellow]")
                
                elif choice == "3":  # View Results
                    self.display_results_overview()
                
                elif choice == "4":  # Export Data
                    if not self.session_results:
                        self.console.print("[yellow]No results to export[/yellow]")
                        continue
                    
                    format_choice = Prompt.ask(
                        "Choose export format",
                        choices=["json", "csv", "txt"],
                        default="json"
                    )
                    
                    filename = Prompt.ask(
                        "Enter filename (without extension)",
                        default=f"readysearch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    
                    self.export_results(format_choice, filename)
                
                elif choice == "5":  # Settings
                    self.console.print("[yellow]Settings configuration coming soon![/yellow]")
                
                elif choice == "6":  # Statistics
                    self.display_results_overview()
                
                elif choice == "7":  # Help
                    self.display_help()
                
                elif choice == "8":  # Exit
                    if Confirm.ask("Are you sure you want to exit?"):
                        break
                
                # Pause before returning to menu
                if choice not in ["8"]:
                    Prompt.ask("\nPress Enter to continue", default="")
                    self.console.clear()
            
            except KeyboardInterrupt:
                if Confirm.ask("\nAre you sure you want to exit?"):
                    break
            except KeyboardInterrupt:
                    self.console.print("[yellow]⚠️ Keyboard interruption detected. Exiting gracefully...[/yellow]")
                    return
                except Exception as e:
                self.console.print(f"[red]❌ An error occurred: {str(e)}[/red]")
                Prompt.ask("Press Enter to continue", default="")
        
        # Exit message
        goodbye_panel = Panel(
            Align.center("Thank you for using ReadySearch Enhanced CLI!\n"
                        f"Session completed with {len(self.session_results)} searches."),
            style=self.colors['success']
        )
        self.console.print(goodbye_panel)

def main():
    """Entry point for enhanced CLI"""
    cli = EnhancedReadySearchCLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()