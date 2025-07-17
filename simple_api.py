"""Simple Flask API for ReadySearch automation testing."""

import logging
import threading
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any
import uuid

app = Flask(__name__)
CORS(app)

# Global state management
automation_sessions = {}
session_lock = threading.Lock()

class AutomationSession:
    """Manages a single automation session."""
    
    def __init__(self, session_id: str, names: List[str]):
        self.session_id = session_id
        self.names = names
        self.status = 'pending'
        self.current_index = 0
        self.results = []
        self.start_time = None
        self.end_time = None
        self.error_message = None
        
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

def run_automation_simulation(session_id: str):
    """Run automation simulation in a separate thread."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return
            
    try:
        session.status = 'running'
        session.start_time = datetime.now()
        
        # Simulate processing each name
        for i, name in enumerate(session.names):
            if session.status == 'stopped':
                break
                
            session.current_index = i
            
            # Simulate processing time
            time.sleep(2)
            
            # Simulate random results
            outcomes = ['Match', 'No Match', 'Error']
            outcome = random.choice(outcomes)
            
            result = {
                'name': name,
                'status': outcome,
                'timestamp': datetime.now().isoformat()
            }
            
            if outcome == 'Error':
                result['error'] = 'Connection timeout'
            elif outcome == 'Match':
                result['matches_found'] = random.randint(1, 3)
                
            session.results.append(result)
        
        if session.status != 'stopped':
            session.status = 'completed'
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = 'error'
        session.error_message = str(e)
        session.end_time = datetime.now()

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start a new automation session."""
    try:
        data = request.get_json()
        names = data.get('names', [])
        
        if not names:
            return jsonify({'error': 'No names provided'}), 400
            
        session_id = str(uuid.uuid4())
        session = AutomationSession(session_id, names)
        
        with session_lock:
            automation_sessions[session_id] = session
            
        # Start automation in background thread
        thread = threading.Thread(target=run_automation_simulation, args=(session_id,))
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Starting ReadySearch API server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)