"""
Minimal working API server for ReadySearch
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage
sessions = {}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    try:
        data = request.get_json()
        names = data.get('names', [])
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'session_id': session_id,
            'names': names,
            'status': 'started',
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(names)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_status(session_id):
    try:
        session = sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(session)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting minimal API server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)