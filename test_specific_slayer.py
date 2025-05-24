#!/usr/bin/env python3
"""
Test the Slayer specific monster calculation
"""

import requests
import json

def test_specific_monster():
    url = "http://localhost:5000/api/calculate_gp_hr"
    data = {
        "activity_type": "slayer",
        "params": {
            "calculation_mode": "specific",
            "specific_monster_id": "gargoyles",
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

def test_expected_mode():
    url = "http://localhost:5000/api/calculate_gp_hr"
    data = {
        "activity_type": "slayer",
        "params": {
            "calculation_mode": "expected",
            "slayer_master_id": "spria",
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

def test_breakdown_mode():
    url = "http://localhost:5000/api/slayer/breakdown"
    data = {
        "slayer_master_id": "spria",
        "user_levels": {
            "slayer_level": 85,
            "combat_level": 100,
            "attack_level": 80,
            "strength_level": 80,
            "defence_level": 75,
            "ranged_level": 85,
            "magic_level": 80
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
    print("🎯 Testing Specific Monster calculation...")
    result1 = test_specific_monster()
    
    print("\n📊 Testing Expected mode calculation...")
    result2 = test_expected_mode()
    
    print("\n📋 Testing Breakdown mode...")
    result3 = test_breakdown_mode() 