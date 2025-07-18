"""Flask API for ReadySearch automation."""

import asyncio
import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from typing import Dict, List, Any
import uuid
import json

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
                    
                    # Add enhanced match details with territory/location parsing
                    if exact_matches:
                        result['match_details'] = []
                        for match in exact_matches[:20]:  # Show up to 20 exact matches
                            match_detail = {
                                'matched_name': getattr(match, 'name', name),
                                'location': getattr(match, 'location', 'N/A'),
                                'confidence': getattr(match, 'confidence_score', 0.0),
                                'match_type': getattr(match, 'match_type', 'exact'),
                                'additional_info': getattr(match, 'additional_info', ''),
                                'raw_data': getattr(match, 'raw_data', {})
                            }
                            
                            # Enhanced location parsing for territory/state information
                            location_text = match_detail['location']
                            if location_text and location_text != 'N/A':
                                # Extract territory/state from location
                                location_parts = location_text.split()
                                territories = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'NT', 'ACT', 'TAS']
                                countries = ['AUSTRALIA', 'UNITED KINGDOM', 'NEW ZEALAND', 'CANADA', 'USA']
                                
                                match_detail['territory'] = 'N/A'
                                match_detail['country'] = 'N/A'
                                
                                for part in location_parts:
                                    if part.upper() in territories:
                                        match_detail['territory'] = part.upper()
                                        match_detail['country'] = 'AUSTRALIA'
                                    elif part.upper() in countries:
                                        match_detail['country'] = part.upper()
                                        if part.upper() == 'AUSTRALIA':
                                            match_detail['territory'] = 'AUSTRALIA'
                            else:
                                match_detail['territory'] = 'N/A'
                                match_detail['country'] = 'N/A'
                            
                            result['match_details'].append(match_detail)
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

def _generate_csv_data(name: str, exact_matches: list) -> str:
    """Generate CSV data for downloadable results."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Search_Name', 'Matched_Name', 'Location', 'Territory', 'Country', 'Confidence', 'Match_Type', 'Additional_Info'])
    
    # Write data rows
    for match in exact_matches:
        matched_name = getattr(match, 'name', 'N/A')
        location = getattr(match, 'location', 'N/A')
        confidence = getattr(match, 'confidence_score', 0.0)
        match_type = getattr(match, 'match_type', 'exact')
        additional_info = getattr(match, 'additional_info', '')
        
        # Parse territory/country from location
        territory = _extract_territory(location)
        country = _extract_country(location)
        
        writer.writerow([name, matched_name, location, territory, country, confidence, match_type, additional_info])
    
    return output.getvalue()


def _generate_json_data(name: str, exact_matches: list, statistics) -> dict:
    """Generate JSON data for downloadable results."""
    return {
        'search_name': name,
        'search_statistics': {
            'total_results_found': statistics.total_results_found if statistics else 0,
            'exact_matches': statistics.exact_matches if statistics else 0,
            'partial_matches': statistics.partial_matches if statistics else 0,
            'search_time': statistics.search_time if statistics else 0.0,
            'timestamp': datetime.now().isoformat()
        },
        'exact_matches': [
            {
                'matched_name': getattr(match, 'name', 'N/A'),
                'location': getattr(match, 'location', 'N/A'),
                'territory': _extract_territory(getattr(match, 'location', 'N/A')),
                'country': _extract_country(getattr(match, 'location', 'N/A')),
                'confidence': getattr(match, 'confidence_score', 0.0),
                'match_type': getattr(match, 'match_type', 'exact'),
                'additional_info': getattr(match, 'additional_info', ''),
                'raw_data': getattr(match, 'raw_data', {})
            }
            for match in exact_matches
        ]
    }


def _extract_territory(location: str) -> str:
    """Extract territory/state from location string."""
    if not location or location == 'N/A':
        return 'N/A'
    
    territories = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'NT', 'ACT', 'TAS']
    location_parts = location.split()
    
    for part in location_parts:
        if part.upper() in territories:
            return part.upper()
    
    if 'AUSTRALIA' in location.upper():
        return 'AUSTRALIA'
    
    return 'N/A'


def _extract_country(location: str) -> str:
    """Extract country from location string."""
    if not location or location == 'N/A':
        return 'N/A'
    
    countries = ['AUSTRALIA', 'UNITED KINGDOM', 'NEW ZEALAND', 'CANADA', 'USA']
    location_parts = location.split()
    
    for part in location_parts:
        if part.upper() in countries:
            return part.upper()
    
    # Check for Australian territories
    territories = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'NT', 'ACT', 'TAS']
    for part in location_parts:
        if part.upper() in territories:
            return 'AUSTRALIA'
    
    return 'N/A'


@app.route('/api/session/<session_id>/download/csv', methods=['GET'])
def download_csv_results(session_id: str):
    """Download CSV results for a session."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if not session.results:
            return jsonify({'error': 'No results available'}), 404
        
        # Generate CSV data for all results
        csv_data = "Search_Name,Status,Total_Results,Exact_Matches,Search_Time,Timestamp\n"
        
        for result in session.results:
            name = result.get('name', 'N/A')
            status = result.get('status', 'N/A')
            total_results = result.get('total_results', 0)
            exact_matches = result.get('exact_matches', 0)
            search_time = result.get('search_time', 0.0)
            timestamp = result.get('timestamp', 'N/A')
            
            csv_data += f'"{name}","{status}",{total_results},{exact_matches},{search_time},"{timestamp}"\n'
        
        # Create response
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=readysearch_results_{session_id}.csv'
        
        return response

@app.route('/api/session/<session_id>/download/json', methods=['GET'])
def download_json_results(session_id: str):
    """Download JSON results for a session."""
    with session_lock:
        session = automation_sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if not session.results:
            return jsonify({'error': 'No results available'}), 404
        
        # Generate comprehensive JSON data
        json_data = {
            'session_id': session_id,
            'generated_at': datetime.now().isoformat(),
            'total_searches': len(session.results),
            'session_status': session.status,
            'search_results': session.results
        }
        
        # Create response
        response = make_response(json.dumps(json_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=readysearch_results_{session_id}.json'
        
        return response

@app.route('/api/import/batch', methods=['POST'])
def import_batch_names():
    """Import batch names from different formats."""
    try:
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            # JSON format
            data = request.get_json()
            if 'names' in data:
                names = data['names']
            else:
                return jsonify({'error': 'JSON must contain a "names" array'}), 400
                
        elif 'text/csv' in content_type or 'text/plain' in content_type:
            # CSV or plain text format
            raw_data = request.data.decode('utf-8')
            
            # Try to parse as CSV first
            try:
                import csv
                import io
                csv_reader = csv.reader(io.StringIO(raw_data))
                names = []
                for row in csv_reader:
                    if row:  # Skip empty rows
                        names.append(row[0].strip())  # Take first column
            except:
                # Fallback to comma-separated parsing
                names = [name.strip() for name in raw_data.split(',') if name.strip()]
                
        elif 'multipart/form-data' in content_type:
            # File upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            file_content = file.read().decode('utf-8')
            
            if file.filename.endswith('.json'):
                # JSON file
                try:
                    data = json.loads(file_content)
                    if 'names' in data:
                        names = data['names']
                    else:
                        return jsonify({'error': 'JSON file must contain a "names" array'}), 400
                except json.JSONDecodeError:
                    return jsonify({'error': 'Invalid JSON file'}), 400
                    
            elif file.filename.endswith('.csv'):
                # CSV file
                try:
                    import csv
                    import io
                    csv_reader = csv.reader(io.StringIO(file_content))
                    names = []
                    for row in csv_reader:
                        if row:  # Skip empty rows
                            names.append(row[0].strip())  # Take first column
                except:
                    return jsonify({'error': 'Invalid CSV file'}), 400
                    
            else:
                # Plain text file (comma-separated)
                names = [name.strip() for name in file_content.split(',') if name.strip()]
                
        else:
            # Default: try to parse as form data or JSON
            if request.form.get('names'):
                names = [name.strip() for name in request.form.get('names').split(',') if name.strip()]
            else:
                try:
                    data = request.get_json()
                    if data and 'names' in data:
                        names = data['names']
                    else:
                        return jsonify({'error': 'Please provide names in JSON format with "names" array, CSV format, or comma-separated text'}), 400
                except:
                    return jsonify({'error': 'Invalid request format'}), 400
        
        # Validate names
        if not names:
            return jsonify({'error': 'No valid names provided'}), 400
            
        # Clean and validate names
        cleaned_names = []
        for name in names:
            if isinstance(name, str) and name.strip():
                cleaned_names.append(name.strip())
                
        if not cleaned_names:
            return jsonify({'error': 'No valid names after cleaning'}), 400
            
        # Limit to reasonable batch size
        if len(cleaned_names) > 100:
            return jsonify({'error': 'Batch size limited to 100 names'}), 400
            
        # Create session and start automation
        session_id = str(uuid.uuid4())
        session = AutomationSession(session_id, cleaned_names)
        
        with session_lock:
            automation_sessions[session_id] = session
            
        # Start automation in background thread
        thread = threading.Thread(target=run_automation_async, args=(session_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'total_names': len(cleaned_names),
            'names_imported': cleaned_names[:10],  # Show first 10 for confirmation
            'total_imported': len(cleaned_names)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import/examples', methods=['GET'])
def get_import_examples():
    """Get examples of different import formats."""
    examples = {
        'json_format': {
            'description': 'JSON format with names array',
            'example': {
                'names': ['John Smith', 'Jane Doe', 'Bob Johnson']
            }
        },
        'csv_format': {
            'description': 'CSV format (first column used as names)',
            'example': 'John Smith,Details\nJane Doe,More details\nBob Johnson,Additional info'
        },
        'comma_separated': {
            'description': 'Simple comma-separated names',
            'example': 'John Smith, Jane Doe, Bob Johnson'
        },
        'endpoints': {
            'batch_import': '/api/import/batch',
            'methods': ['POST'],
            'content_types': ['application/json', 'text/csv', 'text/plain', 'multipart/form-data']
        }
    }
    
    return jsonify(examples)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)