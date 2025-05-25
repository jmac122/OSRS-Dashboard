#!/usr/bin/env python3
"""
Fix Nieve's corrupted slayer task data
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def authenticate_admin():
    """Authenticate as admin"""
    session = requests.Session()
    
    auth_data = {
        "username": "admin",
        "password": "osrsadmin123"
    }
    
    response = session.post(f"{BASE_URL}/api/admin/login", json=auth_data)
    
    if response.status_code == 200 and response.json().get('success'):
        print("✅ Admin authenticated")
        return session
    else:
        print("❌ Admin authentication failed")
        return None

def fix_nieve_data(session):
    """Fix Nieve's task assignments with correct monster data"""
    print("🔧 Fixing Nieve's task assignments...")
    
    # Correct Nieve task assignments based on OSRS Wiki
    # https://oldschool.runescape.wiki/w/Nieve
    correct_nieve_data = {
        "name": "Nieve",
        "combat_req": 85,
        "slayer_req": 0,
        "location": "Tree Gnome Stronghold",
        "wiki_url": "https://oldschool.runescape.wiki/w/Nieve",
        "source": "manual_fix",
        "task_assignments": {
            # High-level profitable monsters
            "abyssal_demons": 0.12,      # 12% - Very profitable
            "gargoyles": 0.10,           # 10% - Consistent profit
            "nechryael": 0.08,           # 8% - Good profit
            "black_demons": 0.08,        # 8% - Decent profit
            "greater_demons": 0.07,      # 7% - Moderate profit
            "bloodvelds": 0.08,          # 8% - Good for bursting
            "dust_devils": 0.07,         # 7% - Good for bursting
            "kurask": 0.06,              # 6% - Decent profit
            "skeletal_wyverns": 0.04,    # 4% - High profit but slower
            "brutal_black_dragons": 0.03, # 3% - Very high profit
            
            # Mid-level monsters
            "cave_horrors": 0.05,        # 5% - Black mask drops
            "aberrant_spectres": 0.06,   # 6% - Herb drops
            "spiritual_mages": 0.04,     # 4% - Rune drops
            "spiritual_warriors": 0.04,  # 4% - Rune drops
            "fire_giants": 0.05,         # 5% - Rune drops
            "hellhounds": 0.03,          # 3% - Clue scrolls
        },
        "avg_task_quantity": {
            # Task quantities for each monster (min, max)
            "abyssal_demons": [130, 200],
            "gargoyles": [110, 170],
            "nechryael": [110, 170],
            "black_demons": [130, 200],
            "greater_demons": [130, 200],
            "bloodvelds": [130, 200],
            "dust_devils": [130, 200],
            "kurask": [110, 170],
            "skeletal_wyverns": [40, 80],
            "brutal_black_dragons": [10, 20],
            "cave_horrors": [110, 170],
            "aberrant_spectres": [130, 200],
            "spiritual_mages": [110, 170],
            "spiritual_warriors": [110, 170],
            "fire_giants": [130, 200],
            "hellhounds": [130, 200],
        }
    }
    
    # Update Nieve's data
    payload = {
        "item_id": "nieve",
        "item_data": correct_nieve_data
    }
    
    response = session.post(
        f"{BASE_URL}/api/admin/items/slayer/masters",
        json=payload
    )
    
    if response.status_code == 200:
        print("✅ Nieve's data fixed successfully!")
        return True
    else:
        print(f"❌ Failed to fix Nieve's data: {response.text}")
        return False

def verify_nieve_fix():
    """Verify that Nieve's data is now correct"""
    print("🔍 Verifying Nieve's fixed data...")
    
    response = requests.get(f"{BASE_URL}/api/items/slayer?category=masters")
    
    if response.status_code == 200:
        data = response.json()
        nieve_data = data.get('items', {}).get('nieve', {})
        
        if nieve_data:
            task_assignments = nieve_data.get('task_assignments', {})
            
            print(f"📊 Nieve now has {len(task_assignments)} task assignments:")
            
            # Check for proper monster names (not "every_X" nonsense)
            proper_monsters = [name for name in task_assignments.keys() 
                             if not name.startswith('every_')]
            
            if len(proper_monsters) > 10:
                print("✅ Nieve now has proper monster assignments!")
                
                # Show some examples
                for monster in list(proper_monsters)[:5]:
                    probability = task_assignments[monster]
                    print(f"   - {monster}: {probability:.1%}")
                
                return True
            else:
                print("❌ Nieve still has corrupted data")
                return False
        else:
            print("❌ Nieve data not found")
            return False
    else:
        print("❌ Failed to retrieve Nieve data")
        return False

def test_nieve_calculation():
    """Test a slayer calculation with Nieve"""
    print("🧪 Testing slayer calculation with fixed Nieve...")
    
    test_params = {
        "activity_type": "slayer",
        "params": {
            "slayer_master": "nieve",
            "user_levels": {
                "combat": 111,
                "slayer": 82,
                "attack": 86,
                "strength": 88,
                "defence": 89,
                "ranged": 84,
                "magic": 83
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/calculate_gp_hr", json=test_params)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            gp_hr = result.get('result', {}).get('gp_hr', 0)
            eligible_tasks = result.get('result', {}).get('eligible_tasks', 0)
            
            print(f"✅ Calculation successful!")
            print(f"   GP/hr: {gp_hr:,}")
            print(f"   Eligible tasks: {eligible_tasks}")
            
            if gp_hr > 0 and eligible_tasks > 0:
                print("🎉 Nieve is now working correctly!")
                return True
            else:
                print("⚠️ Calculation returned but values seem low")
                return False
        else:
            print(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ API request failed: {response.status_code}")
        return False

def main():
    print("🔧 Fixing Nieve's Corrupted Slayer Data")
    print("=" * 45)
    
    # Step 1: Authenticate
    session = authenticate_admin()
    if not session:
        return False
    
    # Step 2: Fix Nieve's data
    if not fix_nieve_data(session):
        return False
    
    # Step 3: Verify the fix
    if not verify_nieve_fix():
        return False
    
    # Step 4: Test calculation
    if not test_nieve_calculation():
        return False
    
    print("\n🎉 SUCCESS: Nieve has been fixed!")
    print("✅ Proper monster task assignments")
    print("✅ Realistic task quantities")
    print("✅ Slayer calculations working")
    print("\n🌐 You can now use Nieve in the frontend!")
    
    return True

if __name__ == "__main__":
    main() 