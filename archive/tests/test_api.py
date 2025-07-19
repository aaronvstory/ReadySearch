"""
Simple test script to verify API server is working
"""
import requests
import json

def test_api():
    print("Testing ReadySearch API server...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ API server is running and healthy")
        else:
            print(f"❌ API server returned error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API server: {e}")
        return False
    
    # Test start automation endpoint with sample data
    try:
        test_data = {
            "names": ["Andro Cutuk,1975", "Anthony Bek,1993", "Ghafoor Jaggi Nadery,1978"],
            "config": {
                "delay": 2.5,
                "retries": 3,
                "headless": True,
                "timeout": 30
            }
        }
        
        print("\nTesting start automation endpoint...")
        response = requests.post(
            "http://localhost:5000/api/start-automation",
            json=test_data,
            timeout=10
        )
        
        print(f"Start automation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Automation started successfully")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Total names: {result.get('total_names')}")
            return True
        else:
            print(f"❌ Start automation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to start automation: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 API server is working correctly!")
    else:
        print("\n❌ API server has issues that need to be resolved.")