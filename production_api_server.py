#!/usr/bin/env python3
"""
PRODUCTION API server for ReadySearch with REAL automation integration.
NO MOCK DATA - Uses actual ReadySearch automation with advanced matching.
"""

import asyncio
import logging
import threading
import uuid
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import REAL automation system - NO MOCKS
from main import ReadySearchAutomation
from config import Config
from readysearch_automation.input_loader import SearchRecord
from readysearch_automation.enhanced_result_parser import PersonResult
from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# In-memory storage for sessions and results
active_sessions = {}
session_results = {}

# Initialize the advanced matcher
advanced_matcher = AdvancedNameMatcher()

class ProductionAutomationEngine:
    """
    PRODUCTION automation engine using the REAL ReadySearch automation system.
    NO MOCK DATA - connects to actual readysearch.com.au
    """
    
    def __init__(self):
        self.advanced_matcher = AdvancedNameMatcher()
        
        # Base REAL automation configuration - use Config.get_config() to ensure all required keys
        self.base_config = Config.get_config()
        
        # Override specific settings for API server
        self.base_config.update({
            'log_level': 'INFO',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file': 'readysearch_automation.log',
            'output_file': 'readysearch_results'
        })
        
        logger.info("🚀 Production Automation Engine initialized with REAL automation")
    
    async def run_search(self, search_record: SearchRecord, session_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a REAL search operation using the production ReadySearch automation.
        
        Args:
            search_record: The search record to process
            session_config: Optional session-specific configuration overrides
            
        Returns:
            Dict containing search results with advanced matching details
        """
        try:
            logger.info(f"🔍 Starting REAL automation for: {search_record.name}")
            
            # Merge session config with base config
            config = self.base_config.copy()
            if session_config:
                logger.info(f"📋 Applying session config: {session_config}")
                config.update(session_config)
                logger.info(f"🔧 Browser mode: {'VISIBLE' if not config.get('headless', True) else 'HEADLESS'}")
            
            # Create REAL automation instance with session-specific config
            automation = ReadySearchAutomation(config)
            
            # Run REAL automation for this single record
            start_time = time.time()
            success = await automation.run_automation([search_record])
            end_time = time.time()
            
            search_duration = int((end_time - start_time) * 1000)  # Convert to milliseconds
            
            logger.info(f"🔧 Automation completed for {search_record.name}, success: {success}")
            logger.info(f"📊 Reporter has {len(automation.reporter.get_results())} results")
            
            if success:
                # Get results from the reporter
                results_data = automation.reporter.get_results()
                logger.info(f"📋 Results data: {results_data}")
                
                if results_data and len(results_data) > 0:
                    result = results_data[0]  # Get the first (and only) result
                    
                    # Extract detailed match information
                    match_details = result.get('match_details', [])
                    exact_matches = len([d for d in match_details if d.get('match_type') == 'exact'])
                    partial_matches = len([d for d in match_details if d.get('match_type') == 'partial'])
                    total_matches = result.get('matches_found', 0)
                    
                    # Prepare detailed results for API response
                    detailed_results = []
                    for detail in match_details:
                        # Apply advanced matching to get detailed reasoning
                        advanced_match = self.advanced_matcher.match_names(
                            search_record.name, 
                            detail.get('matched_name', '')
                        )
                        
                        detailed_results.append({
                            "name": detail.get('matched_name', ''),
                            "match_category": advanced_match.get_display_category(),
                            "match_reasoning": advanced_match.reasoning,
                            "confidence": advanced_match.confidence,
                            "date_of_birth": detail.get('date_of_birth', ''),
                            "location": detail.get('location', '')
                        })
                    
                    # Determine overall match status
                    if exact_matches > 0:
                        overall_status = "Match"
                        overall_category = "EXACT MATCH"
                        main_reasoning = f"Found {exact_matches} exact matches"
                    elif partial_matches > 0:
                        overall_status = "Match"
                        overall_category = "PARTIAL MATCH"
                        main_reasoning = f"Found {partial_matches} partial matches"
                    elif total_matches > 0:
                        overall_status = "Match"
                        overall_category = "PARTIAL MATCH"
                        main_reasoning = f"Found {total_matches} matches"
                    else:
                        overall_status = "No Match"
                        overall_category = "NOT MATCHED"
                        main_reasoning = "No meaningful matches found"
                    
                    return {
                        "status": overall_status,
                        "matches_found": total_matches,
                        "exact_matches": exact_matches,
                        "partial_matches": partial_matches,
                        "match_category": overall_category,
                        "match_reasoning": main_reasoning,
                        "detailed_results": detailed_results,
                        "search_duration": search_duration,
                        "total_results": result.get('total_results', 0)
                    }
                else:
                    return {
                        "status": "No Match",
                        "matches_found": 0,
                        "exact_matches": 0,
                        "partial_matches": 0,
                        "match_category": "NOT MATCHED",
                        "match_reasoning": "No results found during search",
                        "detailed_results": [],
                        "search_duration": search_duration,
                        "total_results": 0
                    }
            else:
                logger.error(f"❌ Automation returned success=False for {search_record.name}")
                # Still check if there are any results even if success=False
                results_data = automation.reporter.get_results()
                logger.info(f"📋 Even though success=False, reporter has {len(results_data)} results")
                
                return {
                    "status": "Error",
                    "matches_found": 0,
                    "exact_matches": 0,
                    "partial_matches": 0,
                    "match_category": "ERROR",
                    "match_reasoning": "Automation failed to complete",
                    "detailed_results": [],
                    "search_duration": search_duration,
                    "error": "Real automation failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Error in REAL automation for '{search_record.name}': {str(e)}")
            return {
                "status": "Error",
                "matches_found": 0,
                "exact_matches": 0,
                "partial_matches": 0,
                "match_category": "ERROR",
                "match_reasoning": f"Automation error: {str(e)}",
                "detailed_results": [],
                "search_duration": 0,
                "error": str(e)
            }

# Initialize PRODUCTION automation engine - NO MOCKS
automation_engine = ProductionAutomationEngine()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'PRODUCTION ReadySearch API Server with REAL Automation',
        'features': [
            'REAL automation - connects to readysearch.com.au',
            'Advanced name matching with variations',
            'Detailed match reasoning and explanations',
            'EXACT vs PARTIAL match categorization',
            'Individual result breakdown with confidence scores',
            'NO MOCK DATA - genuine search results'
        ]
    })

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start PRODUCTION automation with REAL ReadySearch searches."""
    try:
        data = request.get_json()
        names = data.get('names', [])
        config = data.get('config', {})
        
        if not names:
            return jsonify({'error': 'No names provided'}), 400
        
        # Parse names with birth years
        search_records = []
        for name_entry in names:
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
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'search_records': [{'name': sr.name, 'birth_year': sr.birth_year} for sr in search_records],
            'config': config,
            'status': 'started',
            'created_at': datetime.now().isoformat(),
            'total_names': len(search_records),
            'processed_names': 0,
            'current_name': '',
            'current_index': 0,
            'results': []
        }
        
        active_sessions[session_id] = session_data
        session_results[session_id] = []
        
        logger.info(f"Started PRODUCTION automation session {session_id} with {len(search_records)} names")
        
        # Start background processing with REAL automation
        threading.Thread(
            target=lambda: asyncio.run(process_production_automation(session_id, search_records, config)),
            daemon=True
        ).start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(search_records),
            'message': 'PRODUCTION automation session created - using REAL readysearch.com.au',
            'features': [
                'REAL automation with genuine search results',
                'Advanced matching with detailed reasoning',
                'EXACT vs PARTIAL match categorization',
                'Individual result breakdown'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error starting PRODUCTION automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

async def process_production_automation(session_id: str, search_records: List[SearchRecord], config: Dict[str, Any]):
    """Process automation in background with REAL ReadySearch automation."""
    try:
        session = active_sessions[session_id]
        delay = config.get('delay', 2.5)
        
        for i, search_record in enumerate(search_records):
            # Update session status
            session['current_name'] = search_record.name
            session['processed_names'] = i
            session['current_index'] = i
            
            logger.info(f"Processing {search_record.name} with REAL automation...")
            
            # Run REAL automation search with session config
            result = await automation_engine.run_search(search_record, config)
            
            # Store result
            result['name'] = search_record.name
            result['timestamp'] = datetime.now().isoformat()
            session['results'].append(result)
            session_results[session_id].append(result)
            
            logger.info(f"Completed {search_record.name}: {result['status']} - {result['match_category']}")
            
            # Realistic delay between searches
            await asyncio.sleep(delay)
        
        # Mark session as completed
        session['status'] = 'completed'
        session['completed_at'] = datetime.now().isoformat()
        session['processed_names'] = len(search_records)
        session['current_index'] = len(search_records)
        
        logger.info(f"PRODUCTION automation session {session_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in PRODUCTION automation processing: {str(e)}")
        session['status'] = 'error'
        session['error'] = str(e)

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get session status with detailed REAL automation results."""
    try:
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Add current timestamp
        session['last_checked'] = datetime.now().isoformat()
        
        # Include detailed results if available
        if session_id in session_results:
            session['detailed_results'] = session_results[session_id]
        
        return jsonify(session)
        
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/stop', methods=['POST'])
def stop_session(session_id):
    """Stop a session."""
    try:
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        session['status'] = 'stopped'
        session['stopped_at'] = datetime.now().isoformat()
        
        logger.info(f"Stopped PRODUCTION session {session_id}")
        
        return jsonify({'status': 'stopped', 'message': 'Session stopped successfully'})
        
    except Exception as e:
        logger.error(f"Error stopping session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions."""
    try:
        return jsonify({
            'sessions': list(active_sessions.values()),
            'total_sessions': len(active_sessions),
            'features': [
                'PRODUCTION automation with REAL readysearch.com.au searches',
                'Advanced matching with name variations',
                'Detailed reasoning for each match',
                'EXACT vs PARTIAL categorization'
            ]
        })
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("========================================")
    print("    PRODUCTION READYSEARCH API SERVER")
    print("========================================")
    print(f"🚀 Starting PRODUCTION API server with REAL Automation...")
    print(f"🎯 Features:")
    print(f"   - REAL automation connecting to readysearch.com.au")
    print(f"   - Advanced name matching with variations (JOHN → JONATHAN)")
    print(f"   - Middle name detection (JOHN SMITH → JOHN MICHAEL SMITH)")
    print(f"   - Detailed match reasoning and explanations")
    print(f"   - EXACT vs PARTIAL match categorization")
    print(f"   - Individual result breakdown with confidence scores")
    print(f"   - NO MOCK DATA - genuine search results")
    print(f"")
    print(f"🌐 Health check: http://localhost:5000/api/health")
    print(f"📡 API endpoints available:")
    print(f"   POST /api/start-automation")
    print(f"   GET  /api/session/<id>/status")
    print(f"   POST /api/session/<id>/stop")
    print(f"   GET  /api/sessions")
    print("========================================")
    
    app.run(host='0.0.0.0', port=5000, debug=True)