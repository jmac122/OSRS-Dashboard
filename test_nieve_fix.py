#!/usr/bin/env python3
"""
Test Nieve Fix
"""

import requests
import json

def test_nieve_calculation():
    """Test slayer calculation with fixed Nieve"""
    print("🧪 Testing Nieve Slayer Calculation")
    print("=" * 35)
    
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
    
    try:
        print("🔄 Sending calculation request...")
        response = requests.post("http://localhost:5000/api/calculate_gp_hr", json=test_params)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            
            if result.get('success'):
                gp_hr = result.get('result', {}).get('gp_hr', 0)
                eligible_tasks = result.get('result', {}).get('eligible_tasks', 0)
                
                print(f"💰 GP/hr: {gp_hr:,}")
                print(f"📋 Eligible tasks: {eligible_tasks}")
                
                if gp_hr > 0 and eligible_tasks > 0:
                    print("🎉 SUCCESS: Nieve is working correctly!")
                    
                    # Show some details if available
                    result_data = result.get('result', {})
                    if 'task_breakdown' in result_data:
                        print("\n📋 Task Breakdown:")
                        for task in result_data['task_breakdown'][:5]:  # Show first 5
                            monster = task.get('monster', 'Unknown')
                            task_gp = task.get('gp_hr', 0)
                            print(f"   - {monster}: {task_gp:,} GP/hr")
                    
                    return True
                else:
                    print("⚠️ Calculation returned but values are low")
                    print("This might indicate drop table issues")
                    return False
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Calculation failed: {error}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def verify_nieve_data():
    """Verify Nieve's task assignments are correct"""
    print("\n🔍 Verifying Nieve's Task Data")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:5000/api/items/slayer?category=masters")
        
        if response.status_code == 200:
            data = response.json()
            nieve_data = data.get('items', {}).get('nieve', {})
            
            if nieve_data:
                task_assignments = nieve_data.get('task_assignments', {})
                
                print(f"📊 Total assignments: {len(task_assignments)}")
                
                # Check for corrupted data
                corrupted = [name for name in task_assignments.keys() if name.startswith('every_')]
                proper = [name for name in task_assignments.keys() if not name.startswith('every_')]
                
                print(f"✅ Proper monster names: {len(proper)}")
                print(f"❌ Corrupted entries: {len(corrupted)}")
                
                if len(corrupted) == 0 and len(proper) >= 20:
                    print("✅ Nieve's data is clean and complete!")
                    
                    # Show some high-value monsters
                    high_value = ['abyssal_demons', 'gargoyles', 'nechryael', 'kurask', 'skeletal_wyverns']
                    print("\n💎 High-value assignments:")
                    for monster in high_value:
                        if monster in task_assignments:
                            prob = task_assignments[monster]
                            print(f"   - {monster}: {prob:.1%}")
                    
                    return True
                else:
                    print("❌ Nieve still has issues")
                    if corrupted:
                        print(f"Corrupted entries: {corrupted}")
                    return False
            else:
                print("❌ Nieve data not found")
                return False
        else:
            print(f"❌ Failed to get data: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("🎯 NIEVE FIX VERIFICATION")
    print("=" * 25)
    
    # Step 1: Verify data structure
    data_ok = verify_nieve_data()
    
    # Step 2: Test calculation
    calc_ok = test_nieve_calculation()
    
    # Final result
    print("\n" + "=" * 40)
    if data_ok and calc_ok:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ Nieve's data is fixed")
        print("✅ Slayer calculations work")
        print("✅ Ready for frontend testing")
        print("\n🌐 You can now use Nieve in the frontend!")
    elif data_ok:
        print("⚠️ PARTIAL SUCCESS")
        print("✅ Nieve's data is fixed")
        print("❌ Calculations may need work")
        print("(Likely drop table issues)")
    else:
        print("❌ FAILED")
        print("Nieve still has data issues")

if __name__ == "__main__":
    main() 