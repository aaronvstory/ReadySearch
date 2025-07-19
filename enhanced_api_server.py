"""
Enhanced API server for ReadySearch with advanced matching integration.
Provides detailed matching breakdown and reasoning for the UI.
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

# Import the new advanced matching system
import sys
import os
sys.path.append(os.path.dirname(__file__))

from readysearch_automation.advanced_name_matcher import AdvancedNameMatcher, MatchType
from readysearch_automation.input_loader import SearchRecord
from readysearch_automation.enhanced_result_parser import PersonResult

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

class MockAutomationEngine:
    """
    Mock automation engine that simulates the ReadySearch automation
    with the new advanced matching system for demonstration purposes.
    """
    
    def __init__(self):
        self.advanced_matcher = AdvancedNameMatcher()
    
    async def simulate_search(self, search_record: SearchRecord) -> Dict[str, Any]:
        """
        Simulate a search operation with realistic results and advanced matching.
        """
        search_name = search_record.name
        
        # Mock realistic search results based on the name
        mock_results = self._generate_mock_results(search_name, search_record.birth_year)
        
        # Apply advanced matching to each result
        person_results = []
        exact_matches = 0
        partial_matches = 0
        
        for mock_result in mock_results:
            # Create PersonResult object
            person = PersonResult(
                name=mock_result["name"],
                date_of_birth=mock_result["date_of_birth"],
                location=mock_result["location"],
                additional_info=f"DOB: {mock_result['date_of_birth']}, Location: {mock_result['location']}"
            )
            
            # Apply advanced matching
            detailed_match = self.advanced_matcher.match_names(search_name, person.name)
            person.detailed_match = detailed_match
            person.__post_init__()  # Update fields based on detailed match
            
            person_results.append(person)
            
            # Count match types
            if detailed_match.match_type == MatchType.EXACT:
                exact_matches += 1
            elif detailed_match.is_match:
                partial_matches += 1
        
        # Prepare detailed results for API response
        detailed_results = []
        for person in person_results:
            detailed_results.append({
                "name": person.name,
                "match_category": person.match_category,
                "match_reasoning": person.match_reasoning,
                "confidence": person.confidence_score,
                "date_of_birth": person.date_of_birth,
                "location": person.location
            })
        
        # Calculate overall match status
        total_matches = exact_matches + partial_matches
        if exact_matches > 0:
            overall_status = "Match"
            overall_category = "EXACT MATCH"
            main_reasoning = f"Found {exact_matches} exact matches"
        elif partial_matches > 0:
            overall_status = "Match"
            overall_category = "PARTIAL MATCH"
            main_reasoning = f"Found {partial_matches} partial matches"
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
            "search_duration": 1500 + len(search_name) * 100,  # Simulate realistic timing
        }
    
    def _generate_mock_results(self, search_name: str, birth_year: int = None) -> List[Dict[str, str]]:
        """Generate realistic mock results based on the search name."""
        
        # Parse the search name
        name_parts = search_name.lower().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0].title()
            last_name = name_parts[-1].title()
        else:
            first_name = search_name.title()
            last_name = "Smith"  # Default
        
        results = []
        
        # Always include some exact matches
        results.extend([
            {
                "name": f"{first_name.upper()} {last_name.upper()}",
                "date_of_birth": f"15/03/{birth_year or 1990}",
                "location": "SYDNEY NSW"
            },
            {
                "name": f"{first_name.upper()} {last_name.upper()}",
                "date_of_birth": f"22/08/{birth_year+1 if birth_year else 1991}",
                "location": "MELBOURNE VIC"
            }
        ])
        
        # Add some partial matches based on name patterns
        if first_name.lower() == "john":
            results.extend([
                {
                    "name": f"JONATHAN {last_name.upper()}",
                    "date_of_birth": f"10/05/{birth_year or 1990}",
                    "location": "BRISBANE QLD"
                },
                {
                    "name": f"{first_name.upper()} MICHAEL {last_name.upper()}",
                    "date_of_birth": f"03/12/{birth_year or 1990}",
                    "location": "PERTH WA"
                }
            ])
        elif first_name.lower() == "anthony":
            results.extend([
                {
                    "name": f"{first_name.upper()} BAKHOS",
                    "date_of_birth": f"14/06/{birth_year or 1993}",
                    "location": "CAMPSIE NSW"
                },
                {
                    "name": f"{first_name.upper()} BOUCHAIA",
                    "date_of_birth": f"04/05/{birth_year-1 if birth_year else 1992}",
                    "location": "CAMPSIE NSW"
                }
            ])
        elif first_name.lower() == "mike":
            results.extend([
                {
                    "name": f"MICHAEL {last_name.upper()}",
                    "date_of_birth": f"20/07/{birth_year or 1990}",
                    "location": "ADELAIDE SA"
                }
            ])
        
        # Add some completely unrelated results for realism
        results.extend([
            {
                "name": "ROBERT JOHNSON",
                "date_of_birth": f"05/09/{birth_year-5 if birth_year else 1985}",
                "location": "DARWIN NT"
            },
            {
                "name": "MARY WILLIAMS",
                "date_of_birth": f"18/11/{birth_year+3 if birth_year else 1993}",
                "location": "HOBART TAS"
            }
        ])
        
        return results

# Initialize mock automation engine
automation_engine = MockAutomationEngine()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Enhanced ReadySearch API Server with Advanced Matching',
        'features': [
            'Advanced name matching with variations',
            'Detailed match reasoning and explanations',
            'EXACT vs PARTIAL match categorization',
            'Individual result breakdown with confidence scores'
        ]
    })

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start automation with enhanced matching and detailed results."""
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
            'results': []
        }
        
        active_sessions[session_id] = session_data
        session_results[session_id] = []
        
        logger.info(f"Started enhanced automation session {session_id} with {len(search_records)} names")
        
        # Start background processing
        threading.Thread(
            target=lambda: asyncio.run(process_automation(session_id, search_records, config)),
            daemon=True
        ).start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(search_records),
            'message': 'Enhanced automation session created successfully',
            'features': [
                'Advanced matching with detailed reasoning',
                'EXACT vs PARTIAL match categorization',
                'Individual result breakdown'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

async def process_automation(session_id: str, search_records: List[SearchRecord], config: Dict[str, Any]):
    """Process automation in background with enhanced matching."""
    try:
        session = active_sessions[session_id]
        delay = config.get('delay', 2.5)
        
        for i, search_record in enumerate(search_records):
            # Update session status
            session['current_name'] = search_record.name
            session['processed_names'] = i
            
            logger.info(f"Processing {search_record.name} with enhanced matching...")
            
            # Simulate the search with advanced matching
            result = await automation_engine.simulate_search(search_record)
            
            # Store result
            result['name'] = search_record.name
            result['timestamp'] = datetime.now().strftime("%H:%M:%S")
            session['results'].append(result)
            session_results[session_id].append(result)
            
            logger.info(f"Completed {search_record.name}: {result['status']} - {result['match_category']}")
            
            # Simulate processing delay
            await asyncio.sleep(delay)
        
        # Mark session as completed
        session['status'] = 'completed'
        session['completed_at'] = datetime.now().isoformat()
        session['processed_names'] = len(search_records)
        
        logger.info(f"Enhanced automation session {session_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in automation processing: {str(e)}")
        session['status'] = 'error'
        session['error'] = str(e)

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get enhanced session status with detailed matching results."""
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
        
        logger.info(f"Stopped enhanced session {session_id}")
        
        return jsonify({'status': 'stopped', 'message': 'Session stopped successfully'})
        
    except Exception as e:
        logger.error(f"Error stopping session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions with enhanced information."""
    try:
        return jsonify({
            'sessions': list(active_sessions.values()),
            'total_sessions': len(active_sessions),
            'features': [
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
    print("    ENHANCED READYSEARCH API SERVER")
    print("========================================")
    print(f"🚀 Starting Enhanced API server with Advanced Matching...")
    print(f"🎯 Features:")
    print(f"   - Advanced name matching with variations (JOHN → JONATHAN)")
    print(f"   - Middle name detection (JOHN SMITH → JOHN MICHAEL SMITH)")
    print(f"   - Detailed match reasoning and explanations")
    print(f"   - EXACT vs PARTIAL match categorization")
    print(f"   - Individual result breakdown with confidence scores")
    print(f"")
    print(f"🌐 Health check: http://localhost:5000/api/health")
    print(f"📡 API endpoints available:")
    print(f"   POST /api/start-automation")
    print(f"   GET  /api/session/<id>/status")
    print(f"   POST /api/session/<id>/stop")
    print(f"   GET  /api/sessions")
    print("========================================")
    
    app.run(host='0.0.0.0', port=5000, debug=True)