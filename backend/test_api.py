"""
Quick test script for Chartwise AI API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_predictions():
    """Test predictions endpoint"""
    response = requests.get(f"{BASE_URL}/api/predictions/top-picks?limit=5")
    print(f"\nTop Picks: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} predictions")
        for item in data[:3]:
            print(f"  {item['rank']}. {item['symbol']}: {item['bullish_score']}% - {item['recommendation']}")
    return response.status_code == 200

def test_stock_analysis():
    """Test stock analysis"""
    response = requests.get(f"{BASE_URL}/api/stocks/AAPL/prediction")
    print(f"\nAAPL Analysis: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Bullish Score: {data['bullish_score']}%")
        print(f"  Confidence: {data['confidence']}%")
        print(f"  Recommendation: {data['recommendation']}")
        print(f"  Signals: {data['signals']}")
    return response.status_code == 200

if __name__ == "__main__":
    print("🧪 Testing Chartwise AI API\n")
    
    try:
        if test_health():
            test_predictions()
            test_stock_analysis()
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Health check failed - is the server running?")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running: python main.py")
