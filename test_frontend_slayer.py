#!/usr/bin/env python3
"""
Frontend Slayer Functionality Test
==================================

Test the slayer functionality as it would be used from the frontend.
This simulates the actual API calls the React frontend makes.
"""

import requests
import json

def test_frontend_slayer_workflow():
    """Test the complete slayer workflow as used by the frontend"""
    
    print("🎮 Testing Frontend Slayer Workflow")
    print("=" * 50)
    
    api_base = "http://localhost:5000/api"
    
    # Test 1: Load Slayer Masters (for dropdown)
    print("\n1. 👑 Loading Slayer Masters...")
    try:
        response = requests.get(f"{api_base}/items/slayer?category=masters", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                masters = data.get('items', {})
                print(f"   ✅ Loaded {len(masters)} masters")
                print(f"   📋 Available: {list(masters.keys())}")
            else:
                print(f"   ❌ API Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False
    
    # Test 2: Load Slayer Monsters (for dropdown)
    print("\n2. 🐉 Loading Slayer Monsters...")
    try:
        response = requests.get(f"{api_base}/items/slayer?category=monsters", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                monsters = data.get('items', {})
                print(f"   ✅ Loaded {len(monsters)} monsters")
                
                # Show some example monsters with Slayer requirements
                examples = list(monsters.items())[:5]
                print("   📋 Examples:")
                for monster_id, monster_data in examples:
                    name = monster_data.get('name', monster_id)
                    slayer_req = monster_data.get('slayer_level_req', 1)
                    print(f"      - {name}: {slayer_req}+ Slayer")
            else:
                print(f"   ❌ API Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False
    
    # Test 3: Expected Mode Calculation (Frontend Default)
    print("\n3. 📊 Testing Expected Mode (Frontend Default)...")
    try:
        frontend_params = {
            "activity_type": "slayer",
            "params": {
                "calculation_mode": "expected",
                "slayer_master_id": "spria",  # Default master
                "user_slayer_level": 85,
                "user_combat_level": 100,
                "user_attack_level": 80,
                "user_strength_level": 80,
                "user_defence_level": 75,
                "user_ranged_level": 85,
                "user_magic_level": 80
            }
        }
        
        response = requests.post(f"{api_base}/calculate_gp_hr", json=frontend_params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                gp_hr = result.get('gp_hr', 0)
                master_name = result.get('master_name', 'Unknown')
                eligible_tasks = result.get('eligible_tasks', 0)
                print(f"   ✅ Expected GP/hr: {gp_hr:,}")
                print(f"   👑 Master: {master_name}")
                print(f"   📊 Eligible Tasks: {eligible_tasks}")
            else:
                print(f"   ❌ Calculation Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False
    
    # Test 4: Specific Mode Calculation
    print("\n4. 🎯 Testing Specific Mode (Gargoyles)...")
    try:
        specific_params = {
            "activity_type": "slayer",
            "params": {
                "calculation_mode": "specific",
                "specific_monster_id": "gargoyles",
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
        
        response = requests.post(f"{api_base}/calculate_gp_hr", json=specific_params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                gp_hr = result.get('gp_hr', 0)
                monster_name = result.get('monster_name', 'Unknown')
                kph = result.get('kills_per_hour', 0)
                loot_per_kill = result.get('loot_per_kill', 0)
                print(f"   ✅ Specific GP/hr: {gp_hr:,}")
                print(f"   🐉 Monster: {monster_name}")
                print(f"   ⚔️ Kills/Hour: {kph}")
                print(f"   💎 Loot/Kill: {loot_per_kill:,} GP")
            else:
                print(f"   ❌ Calculation Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False
    
    # Test 5: Breakdown Endpoint
    print("\n5. 📋 Testing Breakdown Endpoint...")
    try:
        breakdown_params = {
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
        
        response = requests.post(f"{api_base}/slayer/breakdown", json=breakdown_params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                assignments = result.get('assignments', [])
                overall = result.get('overall', {})
                
                print(f"   ✅ Breakdown loaded: {len(assignments)} assignments")
                if overall:
                    expected_gp_hr = overall.get('expected_gp_per_hour', 0)
                    print(f"   💰 Overall Expected: {expected_gp_hr:,} GP/hr")
                
                # Show top 3 most profitable
                if assignments:
                    print("   🏆 Top 3 Most Profitable:")
                    for i, assignment in enumerate(assignments[:3], 1):
                        name = assignment.get('monster_name', 'Unknown')
                        gp_hr = assignment.get('gp_per_hour', 0)
                        prob = assignment.get('probability', 0) * 100
                        print(f"      {i}. {name}: {gp_hr:,} GP/hr ({prob:.1f}% chance)")
            else:
                print(f"   ❌ Breakdown Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL FRONTEND SLAYER TESTS PASSED!")
    print("✅ The slayer system is ready for use in the browser!")
    print("\n📱 You can now:")
    print("   - Open http://localhost:3000 in your browser")
    print("   - Navigate to the Slayer activity")
    print("   - Select different masters and monsters")
    print("   - Calculate GP/hour with all modes")
    print("   - View detailed task breakdowns")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_frontend_slayer_workflow() 