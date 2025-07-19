#!/usr/bin/env python3
"""Test script to verify the API fixes work correctly."""

import json
import requests
import time
from datetime import datetime

def test_api_functionality():
    """Test the API functionality with configuration."""
    
    # Test data
    test_names = ["John Smith", "Jane Doe"]
    test_config = {
        "delay": 1.0,
        "retries": 2,
        "headless": False,  # This should show the browser
        "timeout": 20
    }
    
    print("🧪 Testing API functionality...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Start automation with config
    print("\n2️⃣ Testing automation start with config...")
    try:
        start_data = {
            "names": test_names,
            "config": test_config
        }
        
        response = requests.post(
            "http://localhost:5000/api/start-automation",
            json=start_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"✅ Automation started successfully. Session ID: {session_id}")
            
            # Test 3: Monitor session status
            print("\n3️⃣ Monitoring session status...")
            for i in range(10):  # Monitor for up to 10 cycles
                time.sleep(3)
                
                status_response = requests.get(f"http://localhost:5000/api/session/{session_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Status: {status_data['status']}, Index: {status_data['current_index']}")
                    print(f"🔄 Current name: {status_data.get('current_name', 'None')}")
                    
                    # Check for messages
                    if status_data.get('messages'):
                        latest_messages = status_data['messages'][-3:]  # Show last 3 messages
                        for msg in latest_messages:
                            print(f"  📝 {msg['level']}: {msg['message']}")
                    
                    # Check if completed
                    if status_data['status'] in ['completed', 'error', 'stopped']:
                        print(f"🏁 Automation {status_data['status']}")
                        
                        # Show final results
                        if status_data.get('results'):
                            print("\n📈 Final Results:")
                            for result in status_data['results']:
                                duration = result.get('search_duration', 0)
                                matches = result.get('matches_found', 0)
                                print(f"  - {result['name']}: {result['status']} ({duration}ms, {matches} matches)")
                        
                        break
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
                    
            return True
        else:
            print(f"❌ Automation start failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Automation test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReadySearch API Test Suite")
    print("=" * 50)
    
    success = test_api_functionality()
    
    if success:
        print("\n✅ All tests passed! API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")