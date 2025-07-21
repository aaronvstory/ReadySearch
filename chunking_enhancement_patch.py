#!/usr/bin/env python3
"""
Chunking Enhancement Patch for Enhanced CLI
Adds intelligent chunking to existing enhanced_cli.py without breaking functionality
"""

import asyncio
import gc
import psutil
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Rich imports for enhanced display
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

class ChunkingConfig:
    """Configuration for intelligent chunking"""
    def __init__(self):
        self.max_chunk_size = 15        # Max searches per chunk
        self.min_chunk_size = 5         # Min searches per chunk
        self.memory_threshold = 80.0    # Memory usage threshold (%)
        self.pause_between_chunks = 2.0 # Pause between chunks (seconds)
        self.enable_chunking = True     # Enable chunking for large batches

class ChunkedBatchProcessor:
    """Add chunking capabilities to existing enhanced CLI"""
    
    def __init__(self, production_cli, console: Console):
        self.production_cli = production_cli
        self.console = console
        self.config = ChunkingConfig()
        
    def should_use_chunking(self, search_records) -> bool:
        """Determine if chunking should be used"""
        return (self.config.enable_chunking and 
                len(search_records) > 10)  # Use chunking for 11+ records
    
    def calculate_optimal_chunks(self, search_records) -> List[List]:
        """Calculate optimal chunk sizes based on system resources and batch size"""
        total_records = len(search_records)
        
        if total_records <= self.config.min_chunk_size:
            return [search_records]
        
        # Check system memory
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > self.config.memory_threshold:
            chunk_size = max(self.config.min_chunk_size, self.config.max_chunk_size // 2)
        else:
            chunk_size = self.config.max_chunk_size
        
        # Create chunks
        chunks = []
        for i in range(0, total_records, chunk_size):
            chunk = search_records[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    async def process_chunked_batch(self, search_records, SearchResult) -> List:
        """Process large batches using intelligent chunking"""
        
        # Calculate chunks
        chunks = self.calculate_optimal_chunks(search_records)
        chunk_count = len(chunks)
        total_records = len(search_records)
        
        # Display chunking information
        self.console.print(f"\n🎯 Large batch detected: {total_records} records")
        self.console.print(f"📦 Using intelligent chunking: {chunk_count} chunks")
        
        for i, chunk in enumerate(chunks):
            self.console.print(f"   Chunk {i+1}: {len(chunk)} records")
        
        # Display system information
        memory_percent = psutil.virtual_memory().percent
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Setting", style="bold")
        info_table.add_column("Value")
        
        info_table.add_row("System Memory Usage", f"{memory_percent:.1f}%")
        info_table.add_row("Chunk Size Strategy", f"{self.config.min_chunk_size}-{self.config.max_chunk_size} records")
        info_table.add_row("Pause Between Chunks", f"{self.config.pause_between_chunks}s")
        
        self.console.print(Panel(info_table, title="Chunking Configuration", style="#00D4AA"))
        
        # Process chunks with progress tracking
        all_results = []
        total_start = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            overall_task = progress.add_task("Overall Progress", total=total_records)
            
            for chunk_id, chunk in enumerate(chunks, 1):
                # Display chunk header
                chunk_panel = Panel(
                    f"[bold]Processing Chunk {chunk_id}/{chunk_count}[/bold]\n"
                    f"Records: {len(chunk)} | Estimated time: {len(chunk) * 7:.0f}s",
                    title=f"🔄 Chunk {chunk_id}",
                    style="#00D4AA"
                )
                self.console.print(chunk_panel)
                
                # Process the chunk
                try:
                    chunk_results = await self.process_single_chunk(chunk, chunk_id, SearchResult)
                    all_results.extend(chunk_results)
                    
                    # Update overall progress
                    progress.update(overall_task, advance=len(chunk))
                    
                    # Display chunk summary
                    successful = len([r for r in chunk_results if r.status != 'Error'])
                    matches = len([r for r in chunk_results if r.matches_found > 0])
                    
                    self.console.print(f"   ✅ Chunk {chunk_id} completed: {successful}/{len(chunk)} successful, {matches} matches found")
                    
                except Exception as e:
                    self.console.print(f"   ❌ Chunk {chunk_id} failed: {str(e)}", style="red")
                    
                    # Create error results for this chunk
                    for search_record in chunk:
                        error_result = SearchResult(
                            name=search_record.name,
                            status='Error',
                            search_duration=0.0,
                            matches_found=0,
                            exact_matches=0,
                            partial_matches=0,
                            match_category='ERROR',
                            match_reasoning=f'Chunk processing failed: {str(e)}',
                            detailed_results=[],
                            timestamp=datetime.now().isoformat(),
                            birth_year=search_record.birth_year,
                            error=str(e)
                        )
                        all_results.append(error_result)
                    
                    progress.update(overall_task, advance=len(chunk))
                
                # Pause between chunks (except for the last one)
                if chunk_id < chunk_count and self.config.pause_between_chunks > 0:
                    self.console.print(f"   ⏸️  Pausing {self.config.pause_between_chunks}s between chunks...")
                    await asyncio.sleep(self.config.pause_between_chunks)
                
                # Memory cleanup between chunks
                gc.collect()
        
        total_duration = time.time() - total_start
        
        # Display final chunking summary
        self.display_chunked_summary(all_results, total_duration, chunk_count)
        
        return all_results
    
    async def process_single_chunk(self, chunk, chunk_id, SearchResult) -> List:
        """Process a single chunk of search records"""
        results = []
        
        for i, search_record in enumerate(chunk):
            try:
                # Display progress
                self.console.print(f"  🔍 [{i+1}/{len(chunk)}] Processing: {search_record.name}", style="dim")
                
                # Perform search using existing production CLI
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
                
                # Status update
                status_emoji = "✅" if enhanced_result.matches_found > 0 else "⭕" if enhanced_result.status != "Error" else "❌"
                self.console.print(f"    {status_emoji} {enhanced_result.name}: {enhanced_result.status} ({enhanced_result.search_duration:.1f}s)", style="dim")
                
            except Exception as e:
                self.console.print(f"    ❌ {search_record.name}: Error - {str(e)}", style="red dim")
                error_result = SearchResult(
                    name=search_record.name,
                    status='Error',
                    search_duration=0.0,
                    matches_found=0,
                    exact_matches=0,
                    partial_matches=0,
                    match_category='ERROR',
                    match_reasoning=f'Processing failed: {str(e)}',
                    detailed_results=[],
                    timestamp=datetime.now().isoformat(),
                    birth_year=search_record.birth_year,
                    error=str(e)
                )
                results.append(error_result)
        
        return results
    
    def display_chunked_summary(self, results, total_duration, chunk_count):
        """Display comprehensive chunked batch processing summary"""
        total_searches = len(results)
        successful = len([r for r in results if r.status != 'Error'])
        matches = len([r for r in results if r.matches_found > 0])
        errors = len([r for r in results if r.status == 'Error'])
        
        # Performance metrics
        throughput = total_searches / (total_duration / 60)  # searches per minute
        avg_duration = total_duration / total_searches if total_searches > 0 else 0
        
        # Create summary table
        summary_table = Table(title="🎯 Chunked Batch Processing Summary", style="#4ECDC4")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", justify="right")
        
        summary_table.add_row("Total Searches", str(total_searches))
        summary_table.add_row("Processing Chunks", str(chunk_count))
        summary_table.add_row("Total Duration", f"{total_duration:.1f}s ({total_duration/60:.1f}m)")
        summary_table.add_row("Average per Search", f"{avg_duration:.1f}s")
        summary_table.add_row("Throughput", f"{throughput:.1f} searches/min")
        summary_table.add_row("", "")  # Separator
        summary_table.add_row("Successful Searches", f"[green]{successful}[/green]")
        summary_table.add_row("Found Matches", f"[green]{matches}[/green]")
        summary_table.add_row("Errors", f"[red]{errors}[/red]")
        summary_table.add_row("Success Rate", f"{(successful/total_searches*100):.1f}%")
        summary_table.add_row("Match Rate", f"{(matches/total_searches*100):.1f}%")
        
        self.console.print("\n")
        self.console.print(summary_table)
        
        # Performance comparison
        theoretical_sequential = total_searches * 7.6  # Average from analysis
        if total_duration < theoretical_sequential:
            improvement = ((theoretical_sequential - total_duration) / theoretical_sequential) * 100
            self.console.print(f"\n⚡ Performance Improvement: {improvement:.1f}% faster than sequential processing")
        
        self.console.print("\n")

def add_chunking_to_enhanced_cli():
    """
    Function to monkey-patch the existing enhanced CLI with chunking capabilities
    This preserves all existing functionality while adding chunking
    """
    import enhanced_cli
    
    # Store original perform_search method
    original_perform_search = enhanced_cli.EnhancedReadySearchCLI.perform_search
    
    # Add chunking processor to the CLI class
    def enhanced_init(self):
        # Call original init
        original_init(self)
        # Add chunking processor
        self.chunk_processor = ChunkedBatchProcessor(self.production_cli, self.console)
    
    # Store original init
    original_init = enhanced_cli.EnhancedReadySearchCLI.__init__
    enhanced_cli.EnhancedReadySearchCLI.__init__ = enhanced_init
    
    # Enhanced perform_search with chunking detection
    async def enhanced_perform_search(self, names_input: str):
        search_records = self.parse_names_input(names_input)
        
        if not search_records:
            self.console.print("[red]❌ No valid names found in input[/red]")
            return []
        
        # Check if chunking should be used
        if self.chunk_processor.should_use_chunking(search_records):
            self.console.print(f"🚀 Large batch detected ({len(search_records)} records). Using intelligent chunking...")
            return await self.chunk_processor.process_chunked_batch(search_records, enhanced_cli.SearchResult)
        else:
            # Use original method for small batches
            return await original_perform_search(self, names_input)
    
    # Replace the method
    enhanced_cli.EnhancedReadySearchCLI.perform_search = enhanced_perform_search
    
    return enhanced_cli

# Usage example:
if __name__ == "__main__":
    # This demonstrates how to use the chunking enhancement
    enhanced_cli = add_chunking_to_enhanced_cli()
    
    # Now the enhanced CLI has chunking capabilities
    # All existing functionality is preserved
    # Large batches (>10 records) automatically use chunking