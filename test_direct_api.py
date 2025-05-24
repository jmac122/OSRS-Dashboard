#!/usr/bin/env python3
"""
Test direct API calls to understand the data structure
"""

import requests
import json

def test_direct_api():
    """Test direct API calls"""
    
    # Test with no category
    print("🔍 Testing /api/items/slayer (no category)...")
    try:
        response = requests.get("http://localhost:5000/api/items/slayer")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with masters category
    print("\n👑 Testing /api/items/slayer?category=masters...")
    try:
        response = requests.get("http://localhost:5000/api/items/slayer?category=masters")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with monsters category
    print("\n👹 Testing /api/items/slayer?category=monsters...")
    try:
        response = requests.get("http://localhost:5000/api/items/slayer?category=monsters")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get('success') and result.get('items'):
            print(f"Found {len(result['items'])} monsters")
            print(f"First 3 monster keys: {list(result['items'].keys())[:3]}")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_api() 