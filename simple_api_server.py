"""
Simple, reliable API server for ReadySearch automation
"""
import asyncio
import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Simple in-memory storage for demo
active_sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'ReadySearch API Server is running'
    })

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start automation with birth year support."""
    try:
        data = request.get_json()
        names = data.get('names', [])
        config = data.get('config', {})
        
        if not names:
            return jsonify({'error': 'No names provided'}), 400
        
        # Parse names with birth years
        parsed_names = []
        for name_entry in names:
            if ',' in name_entry:
                parts = name_entry.split(',', 1)
                name = parts[0].strip()
                try:
                    birth_year = int(parts[1].strip())
                    parsed_names.append({
                        'name': name,
                        'birth_year': birth_year,
                        'birth_year_range': f"{birth_year-2}-{birth_year+2}"
                    })
                except ValueError:
                    parsed_names.append({'name': name_entry, 'birth_year': None})
            else:
                parsed_names.append({'name': name_entry, 'birth_year': None})
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'names': parsed_names,
            'config': config,
            'status': 'started',
            'created_at': datetime.now().isoformat(),
            'message': f'Session created for {len(parsed_names)} names'
        }
        
        active_sessions[session_id] = session_data
        
        logger.info(f"Started automation session {session_id} with {len(parsed_names)} names")
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(parsed_names),
            'parsed_names': parsed_names,
            'message': 'Automation session created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get session status."""
    try:
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Add current timestamp
        session['last_checked'] = datetime.now().isoformat()
        
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
        
        logger.info(f"Stopped session {session_id}")
        
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
            'total_sessions': len(active_sessions)
        })
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("========================================")
    print("    READYSEARCH API SERVER")
    print("========================================")
    print(f"Starting API server on port 5000...")
    print(f"Health check: http://localhost:5000/api/health")
    print(f"API endpoints available:")
    print(f"  POST /api/start-automation")
    print(f"  GET  /api/session/<id>/status")
    print(f"  POST /api/session/<id>/stop")
    print(f"  GET  /api/sessions")
    print("========================================")
    
    app.run(host='0.0.0.0', port=5000, debug=True)