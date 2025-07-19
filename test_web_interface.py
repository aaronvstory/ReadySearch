#!/usr/bin/env python3
"""
Test script for ReadySearch web interface functionality
Tests both API server and web interface integration
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:5000"
WEB_APP_URL = "http://localhost:5173"

def test_api_health():
    """Test API server health check"""
    print("🧪 Testing API Server Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("   ✅ API server is healthy")
            health_data = response.json()
            print(f"   📊 Status: {health_data.get('status', 'Unknown')}")
            print(f"   🕐 Timestamp: {health_data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"   ❌ API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API health check failed: {e}")
        return False

def test_web_app_accessibility():
    """Test that web app is accessible"""
    print("🧪 Testing Web App Accessibility...")
    try:
        response = requests.get(WEB_APP_URL)
        if response.status_code == 200:
            print("   ✅ Web app is accessible")
            # Check if it contains React app content
            if "vite" in response.text.lower() or "react" in response.text.lower():
                print("   ✅ React/Vite content detected")
            return True
        else:
            print(f"   ❌ Web app not accessible, status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Web app accessibility test failed: {e}")
        return False

def test_api_search_functionality():
    """Test API search functionality with sample names"""
    print("🧪 Testing API Search Functionality...")
    
    # Test data - same sample names used in other tests
    test_names = [
        "Anthony Bek,1993",
        "Andro Cutuk,1975"
    ]
    
    try:
        # Start automation session
        search_payload = {
            "names": test_names,
            "mode": "standard"
        }
        
        print("   🚀 Starting automation session...")
        response = requests.post(f"{API_BASE_URL}/api/start-automation", 
                               json=search_payload,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get('session_id')
            print(f"   ✅ Session started: {session_id}")
            
            # Monitor session progress
            print("   ⏳ Monitoring search progress...")
            max_wait_time = 60  # 60 seconds max
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status_response = requests.get(f"{API_BASE_URL}/api/session/{session_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', {})
                    
                    print(f"   📊 Status: {status}, Progress: {progress.get('completed', 0)}/{progress.get('total', 0)}")
                    
                    if status == 'completed':
                        results = status_data.get('results', [])
                        print(f"   ✅ Search completed with {len(results)} results")
                        
                        # Validate results structure
                        for i, result in enumerate(results):
                            name = result.get('name', 'Unknown')
                            status = result.get('status', 'Unknown')
                            matches = result.get('matches_found', 0)
                            print(f"      {i+1}. {name}: {status} ({matches} matches)")
                        
                        return True
                    elif status == 'error':
                        error = status_data.get('error', 'Unknown error')
                        print(f"   ❌ Search failed: {error}")
                        return False
                    
                    time.sleep(2)  # Wait 2 seconds before next check
                else:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
                    return False
            
            print("   ⚠️ Search timed out")
            return False
        else:
            print(f"   ❌ Failed to start session: {response.status_code}")
            if response.text:
                print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API search test failed: {e}")
        return False

def test_web_integration():
    """Test overall web integration"""
    print("🧪 Testing Web Integration...")
    
    # Test if both servers are running
    api_ok = test_api_health()
    web_ok = test_web_app_accessibility()
    
    if api_ok and web_ok:
        print("   ✅ Both API and web app are running")
        print("   ✅ Web interface integration ready")
        return True
    else:
        print("   ❌ Web integration incomplete")
        return False

def main():
    """Run all web interface tests"""
    print("🚀 ReadySearch Web Interface Testing")
    print("=" * 50)
    
    # Run all tests
    api_health = test_api_health()
    web_access = test_web_app_accessibility() 
    web_integration = test_web_integration()
    api_search = test_api_search_functionality()
    
    print("=" * 50)
    print("📊 Web Interface Test Summary:")
    print(f"   API Health: {'✅ PASS' if api_health else '❌ FAIL'}")
    print(f"   Web Access: {'✅ PASS' if web_access else '❌ FAIL'}")
    print(f"   Integration: {'✅ PASS' if web_integration else '❌ FAIL'}")
    print(f"   API Search: {'✅ PASS' if api_search else '❌ FAIL'}")
    
    if all([api_health, web_access, web_integration, api_search]):
        print("🎉 All web interface tests PASSED!")
        return True
    else:
        print("⚠️ Some web interface tests FAILED")
        return False

if __name__ == "__main__":
    main()