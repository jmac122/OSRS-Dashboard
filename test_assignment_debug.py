#!/usr/bin/env python3
"""
Test assignment matching debug
"""

import requests
import json

def test_debug_assignments():
    """Test to see what assignments Nieve has"""
    
    # Test getting slayer masters from API
    print("🔍 Testing slayer masters API...")
    try:
        response = requests.get("http://localhost:5000/api/items/slayer")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if result.get('success') and result.get('items', {}).get('masters'):
            masters = result['items']['masters']
            print(f"Found {len(masters)} masters")
            
            nieve = masters.get('nieve')
            if nieve:
                print(f"\nNieve data:")
                print(f"  Name: {nieve.get('name')}")
                print(f"  Combat Req: {nieve.get('combat_req')}")
                print(f"  Task Assignments: {len(nieve.get('task_assignments', {}))}")
                assignments = nieve.get('task_assignments', {})
                print(f"  Assignment IDs: {list(assignments.keys())[:10]}...")
                
                print(f"\nFirst 5 assignments with weights:")
                for i, (monster_id, weight) in enumerate(list(assignments.items())[:5]):
                    print(f"    {i+1}. {monster_id}: weight {weight}")
        else:
            print("No masters found in API response")
            print(f"Response: {json.dumps(result, indent=2)}")
    
    except Exception as e:
        print(f"Error: {e}")

    # Test breakdown to see what the actual issue is
    print("\n📋 Testing breakdown with debug...")
    try:
        url = "http://localhost:5000/api/slayer/breakdown"
        data = {
            "slayer_master_id": "nieve",
            "user_levels": {
                "slayer_level": 1,  # Set very low to see if requirements are the issue
                "combat_level": 200,  # Set very high
                "attack_level": 99,
                "strength_level": 99,
                "defence_level": 99,
                "ranged_level": 99,
                "magic_level": 99
            }
        }
        
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Breakdown Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_debug_assignments() 