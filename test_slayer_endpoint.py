#!/usr/bin/env python3
"""
Test the Slayer calculation endpoint
"""

import requests
import json

def test_slayer_calc():
    url = "http://localhost:5000/api/calculate_gp_hr"
    data = {
        "activity_type": "slayer",
        "params": {
            "slayer_master_id": "nieve",
            "user_slayer_level": 85,
            "user_combat_level": 100,
            "user_attack_level": 80,
            "user_strength_level": 80,
            "user_defence_level": 75,
            "user_ranged_level": 85,
            "user_magic_level": 80
        }
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 Testing Slayer calculation...")
    result = test_slayer_calc()
    
    if result and result.get('success') and not result.get('result', {}).get('error'):
        print("✅ Slayer calculation successful!")
        print(f"GP/Hour: {result['result']['gp_hr']:,}")
    else:
        print("❌ Slayer calculation failed or data not populated!") 