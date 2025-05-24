#!/usr/bin/env python3
"""
Simple test script to call the sync endpoint
"""

import requests
import json

def test_sync():
    url = "http://localhost:5000/api/admin/sync_wiki"
    data = {"sync_type": "slayer"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing Slayer data sync...")
    result = test_sync()
    
    if result and result.get('success'):
        print("✅ Sync successful!")
    else:
        print("❌ Sync failed!") 