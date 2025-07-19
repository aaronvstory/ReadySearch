#!/usr/bin/env python3
"""Start the API server for testing."""

import sys
import logging
from api import app

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting ReadySearch API Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Test endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/start-automation")
    print("  - GET  /api/session/{id}/status")
    print("  - POST /api/session/{id}/stop")
    print("\n💡 To test the API, run: python test_api_fix.py")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)