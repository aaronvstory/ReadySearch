"""Flask API for ReadySearch automation."""

import asyncio
import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any
import uuid

from config import Config
from main import ReadySearchAutomation

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global state management
automation_sessions = {}
session_lock = threading.Lock()

class AutomationSession:
    """Manages a single automation session."""
    
    def __init__(self, session_id: str, names: List[str]):
        self.session_id = session_id
        self.names = names
        self.status = 'pending'  # pending, running, completed, error, stopped
        self.current_index = 0
        self.results = []
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.automation = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON response."""
        return {
            'session_id': self.session_id,
            'status': self.status,
            'current_index': self.current_index,
            'total_names': len(self.names),
            'results': self.results,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message
        }

def run_automation_async(session_id: str):
    """Run automation in a separate thread."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return
            
    try:
        # Set up the automation
        config = Config.get_config()
        session.automation = ReadySearchAutomation(config)
        session.status = 'running'
        session.start_time = datetime.now()
        
        # Run the automation with progress tracking
        asyncio.run(run_automation_with_progress(session))
        
    except Exception as e:
        session.status = 'error'
        session.error_message = str(e)
        session.end_time = datetime.now()
        logging.error(f"Automation error for session {session_id}: {str(e)}")

async def run_automation_with_progress(session: AutomationSession):
    """Run automation with progress updates."""
    try:
        config = Config.get_config()
        
        # Start browser
        await session.automation.browser_controller.start_browser()
        
        # Navigate to search page
        navigation_success = await session.automation.browser_controller.navigate_to_search_page()
        if not navigation_success:
            raise Exception("Failed to navigate to search page")
            
        # Process each name
        for i, name in enumerate(session.names):
            if session.status == 'stopped':
                break
                
            session.current_index = i
            
            try:
                # Search for the name
                search_result = await session.automation._search_single_name_enhanced(name)
                
                # Create result entry with enhanced information
                result = {
                    'name': name,
                    'status': search_result['status'],
                    'timestamp': datetime.now().isoformat()
                }
                
                if search_result['status'] == 'Error':
                    result['error'] = search_result.get('error', 'Unknown error')
                elif search_result['status'] == 'Match':
                    statistics = search_result.get('statistics')
                    exact_matches = search_result.get('exact_matches', [])
                    
                    result['matches_found'] = len(exact_matches)
                    result['total_results'] = statistics.total_results_found if statistics else 0
                    result['exact_matches'] = statistics.exact_matches if statistics else 0
                    result['partial_matches'] = statistics.partial_matches if statistics else 0
                    result['search_time'] = statistics.search_time if statistics else 0.0
                    
                    # Add match details
                    if exact_matches:
                        result['match_details'] = []
                        for match in exact_matches:
                            result['match_details'].append({
                                'matched_name': match.name,
                                'location': match.location,
                                'confidence': match.confidence_score,
                                'match_type': match.match_type
                            })
                elif search_result['status'] == 'No Match':
                    statistics = search_result.get('statistics')
                    result['total_results'] = statistics.total_results_found if statistics else 0
                    result['search_time'] = statistics.search_time if statistics else 0.0
                    
                session.results.append(result)
                
            except Exception as e:
                result = {
                    'name': name,
                    'status': 'Error',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
                session.results.append(result)
                
            # Rate limiting delay
            if i < len(session.names) - 1 and session.status != 'stopped':
                await asyncio.sleep(config['delay'])
                
        # Mark as completed
        if session.status != 'stopped':
            session.status = 'completed'
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = 'error'
        session.error_message = str(e)
        session.end_time = datetime.now()
        
    finally:
        # Clean up browser
        if session.automation and session.automation.browser_controller:
            await session.automation.browser_controller.cleanup()

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start a new automation session."""
    try:
        data = request.get_json()
        names = data.get('names', [])
        
        if not names:
            return jsonify({'error': 'No names provided'}), 400
            
        # Create new session
        session_id = str(uuid.uuid4())
        session = AutomationSession(session_id, names)
        
        with session_lock:
            automation_sessions[session_id] = session
            
        # Start automation in background thread
        thread = threading.Thread(target=run_automation_async, args=(session_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(names)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id: str):
    """Get the status of an automation session."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
            
        return jsonify(session.to_dict())

@app.route('/api/session/<session_id>/stop', methods=['POST'])
def stop_session(session_id: str):
    """Stop an automation session."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
            
        if session.status == 'running':
            session.status = 'stopped'
            session.end_time = datetime.now()
            
        return jsonify({'status': 'stopped'})

@app.route('/api/session/<session_id>/results', methods=['GET'])
def get_session_results(session_id: str):
    """Get the results of an automation session."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
            
        return jsonify({
            'session_id': session_id,
            'results': session.results,
            'status': session.status
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)