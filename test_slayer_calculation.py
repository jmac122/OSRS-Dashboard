#!/usr/bin/env python3
"""
Test Slayer Calculation
Verify that slayer calculations work properly with fixed drop tables
"""

import requests
import json

def test_slayer_calculation():
    """Test slayer calculation with gargoyles"""
    api_base = "http://localhost:5000"
    
    # Test data
    test_data = {
        "activity_type": "slayer",
        "params": {
            "calculation_mode": "specific",
            "specific_monster_id": "gargoyles",
            "slayer_master_id": "nieve",
            "user_slayer_level": 85,
            "user_combat_level": 100
        }
    }
    
    print("🧪 TESTING SLAYER CALCULATION")
    print("=" * 50)
    print(f"Testing: {test_data['params']['specific_monster_id']} with {test_data['params']['slayer_master_id']}")
    print()
    
    try:
        response = requests.post(
            f"{api_base}/api/calculate_gp_hr",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(result, indent=2))
            
            # Check if we got positive GP/hr
            gp_hr = result.get('result', {}).get('gp_hr', 0)
            if gp_hr > 0:
                print(f"\n🎉 EXCELLENT: Positive GP/hr of {gp_hr:,.0f}!")
                return True
            else:
                print(f"\n⚠️  ISSUE: GP/hr is {gp_hr}")
                return False
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_multiple_monsters():
    """Test multiple monsters to verify coverage"""
    api_base = "http://localhost:5000"
    
    test_monsters = [
        "gargoyles",
        "abyssal_demons", 
        "nechryael",
        "black_demons",
        "bloodvelds"
    ]
    
    print("\n🧪 TESTING MULTIPLE MONSTERS")
    print("=" * 50)
    
    results = {}
    
    for monster in test_monsters:
        test_data = {
            "activity_type": "slayer",
            "params": {
                "calculation_mode": "specific",
                "specific_monster_id": monster,
                "slayer_master_id": "nieve",
                "user_slayer_level": 85,
                "user_combat_level": 100
            }
        }
        
        print(f"Testing {monster}...", end=" ")
        
        try:
            response = requests.post(
                f"{api_base}/api/calculate_gp_hr",
                headers={"Content-Type": "application/json"},
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                gp_hr = result.get('result', {}).get('gp_hr', 0)
                results[monster] = gp_hr
                
                if gp_hr > 0:
                    print(f"✅ {gp_hr:,.0f} GP/hr")
                else:
                    print(f"⚠️  {gp_hr} GP/hr")
            else:
                print(f"❌ Error {response.status_code}")
                results[monster] = None
                
        except Exception as e:
            print(f"❌ {e}")
            results[monster] = None
    
    # Summary
    print(f"\n📊 SUMMARY:")
    working = sum(1 for gp in results.values() if gp and gp > 0)
    total = len(results)
    print(f"   Working calculations: {working}/{total}")
    print(f"   Success rate: {working/total*100:.1f}%")
    
    return working >= total * 0.8  # 80% success rate

def main():
    print("🚀 SLAYER CALCULATION VERIFICATION")
    print("=" * 60)
    
    # Test 1: Single calculation
    test1_success = test_slayer_calculation()
    
    # Test 2: Multiple monsters
    test2_success = test_multiple_monsters()
    
    # Overall result
    print(f"\n🏁 FINAL RESULT:")
    if test1_success and test2_success:
        print("🎉 ALL TESTS PASSED! Slayer calculations are working properly.")
        return True
    elif test1_success or test2_success:
        print("⚠️  PARTIAL SUCCESS: Some calculations working.")
        return False
    else:
        print("❌ TESTS FAILED: Slayer calculations need more work.")
        return False

if __name__ == "__main__":
    main() 