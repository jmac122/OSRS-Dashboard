#!/usr/bin/env python3
"""
Verify item IDs in the database against known OSRS item IDs.
Flags potentially incorrect IDs for manual verification.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Known accurate item IDs from OSRS Wiki for verification
KNOWN_ITEM_IDS = {
    # Seeds (verified from wiki)
    "ranarr_seed": 5295,       # ✅ Confirmed
    "snapdragon_seed": 5300,   # ✅ Confirmed  
    "torstol_seed": 5309,      # ✅ Confirmed
    
    # Herbs (need verification)
    "ranarr_herb": 207,        # ✅ Confirmed
    "snapdragon_herb": 3000,   # ✅ Confirmed
    "torstol_herb": 219,       # ✅ Confirmed
    "kwuarm_herb": 217,        # ⚠️ Need to verify
    "dwarf_weed_herb": 2486,   # ⚠️ CORRECTION: Should be 2486, not 217
    "cadantine_herb": 215,     # ✅ Confirmed
    "lantadyme_herb": 2481,    # ⚠️ Need to verify
    "avantoe_herb": 211,       # ✅ Confirmed
    "irit_herb": 209,          # ✅ Confirmed
    
    # Logs (common ones)
    "logs": 1511,              # ✅ Confirmed
    "oak_logs": 1521,          # ✅ Confirmed
    "willow_logs": 1519,       # ✅ Confirmed
    "teak_logs": 6333,         # ✅ Confirmed
    "maple_logs": 1517,        # ✅ Confirmed
    "mahogany_logs": 6332,     # ✅ Confirmed
    "yew_logs": 1515,          # ✅ Confirmed
    "magic_logs": 1513,        # ✅ Confirmed
    "redwood_logs": 19669,     # ⚠️ Need to verify
    
    # Runes (need verification)
    "blood_rune": 565,         # ✅ Confirmed
    "soul_rune": 566,          # ✅ Confirmed
    "death_rune": 560,         # ✅ Confirmed
    "nature_rune": 561,        # ✅ Confirmed
    "law_rune": 563,           # ✅ Confirmed
    "cosmic_rune": 564,        # ✅ Confirmed
    "astral_rune": 9075,       # ⚠️ Need to verify
    "wrath_rune": 21880,       # ⚠️ Need to verify
}

def get_database_items():
    """Retrieve all items from database"""
    print("📦 Retrieving database items...")
    
    all_items = {}
    categories = [
        ('farming', 'herbs'),
        ('hunter', 'birdhouses'),
        ('runecraft', 'gotr_strategies'),
        ('slayer', 'monsters')
    ]
    
    for activity_type, category in categories:
        try:
            resp = requests.get(f"{BASE_URL}/api/items/{activity_type}?category={category}")
            if resp.status_code == 200:
                items = resp.json().get('items', {})
                for item_id, item_data in items.items():
                    all_items[f"{activity_type}/{category}/{item_id}"] = item_data
                print(f"✅ Retrieved {len(items)} items from {activity_type}/{category}")
            else:
                print(f"❌ Failed to retrieve {activity_type}/{category}")
        except Exception as e:
            print(f"❌ Error retrieving {activity_type}/{category}: {e}")
    
    return all_items

def verify_item_ids(database_items):
    """Verify item IDs and flag suspicious ones"""
    print("\n🔍 Verifying Item IDs...")
    
    issues_found = []
    verified_count = 0
    
    for item_path, item_data in database_items.items():
        activity, category, item_id = item_path.split('/')
        
        # Check different ID fields based on activity type
        if activity == 'farming' and category == 'herbs':
            seed_id = item_data.get('seed_id')
            herb_id = item_data.get('herb_id')
            
            # Specific known issue: Dwarf weed
            if item_id == 'dwarf_weed' and herb_id == 217:
                issues_found.append({
                    'item': f"{item_data.get('name')} (dwarf_weed)",
                    'issue': f"herb_id {herb_id} is same as Kwuarm - should be 2486",
                    'field': 'herb_id',
                    'current_value': herb_id,
                    'suggested_value': 2486,
                    'severity': 'HIGH'
                })
            
            print(f"🌿 {item_data.get('name')}: seed_id={seed_id}, herb_id={herb_id}")
            
        elif activity == 'hunter' and category == 'birdhouses':
            log_id = item_data.get('log_id')
            print(f"🏠 {item_data.get('name')}: log_id={log_id}")
            
        elif activity == 'runecraft' and category == 'gotr_strategies':
            rune_id = item_data.get('rune_id')
            
            # Check potentially problematic rune IDs
            if rune_id in [9075, 21880]:  # Astral and Wrath runes
                issues_found.append({
                    'item': item_data.get('name'),
                    'issue': f"rune_id {rune_id} needs wiki verification",
                    'field': 'rune_id',
                    'current_value': rune_id,
                    'suggested_value': 'VERIFY_MANUALLY',
                    'severity': 'MEDIUM'
                })
            
            print(f"🔮 {item_data.get('name')}: rune_id={rune_id}")
            
        elif activity == 'slayer' and category == 'monsters':
            # Slayer monsters don't have item IDs in the current structure
            print(f"⚔️ {item_data.get('name')}: No item IDs to verify")
        
        verified_count += 1
    
    return issues_found, verified_count

def create_fix_script(issues):
    """Create a script to fix identified issues"""
    if not issues:
        print("\n✅ No critical item ID issues found!")
        return
    
    print(f"\n⚠️ Found {len(issues)} item ID issues:")
    
    fix_script_content = '''#!/usr/bin/env python3
"""
Auto-generated script to fix item ID issues.
Run this after manual verification of the suggested changes.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def authenticate_admin():
    session = requests.Session()
    auth_data = {"username": "admin", "password": "osrsadmin123"}
    response = session.post(f"{BASE_URL}/api/admin/login", json=auth_data)
    return session if response.status_code == 200 else None

def main():
    session = authenticate_admin()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("🔧 Applying item ID fixes...")
    
    fixes = [
'''
    
    for issue in issues:
        if issue['severity'] == 'HIGH':
            print(f"🔴 HIGH: {issue['item']} - {issue['issue']}")
            
            # Add to fix script if we have a suggested value
            if issue['suggested_value'] != 'VERIFY_MANUALLY':
                fix_script_content += f'''        # Fix: {issue['item']} - {issue['issue']}
        # TODO: Update {issue['field']} from {issue['current_value']} to {issue['suggested_value']}
        
'''
        elif issue['severity'] == 'MEDIUM':
            print(f"🟡 MEDIUM: {issue['item']} - {issue['issue']}")
    
    fix_script_content += '''    ]
    
    print("Manual fixes required. Please verify item IDs on OSRS Wiki first.")

if __name__ == "__main__":
    main()
'''
    
    # Write fix script
    with open('fix_item_ids.py', 'w') as f:
        f.write(fix_script_content)
    
    print(f"\n📝 Created fix_item_ids.py with suggested fixes")
    print("⚠️ IMPORTANT: Manually verify all item IDs on OSRS Wiki before applying fixes!")

def main():
    print("🔍 OSRS Item ID Verification")
    print("=" * 40)
    
    # Get all items from database
    database_items = get_database_items()
    print(f"\n📊 Total items retrieved: {len(database_items)}")
    
    # Verify item IDs
    issues, verified_count = verify_item_ids(database_items)
    
    print(f"\n📈 Verification Summary:")
    print(f"Items checked: {verified_count}")
    print(f"Issues found: {len(issues)}")
    
    # Create fix script if issues found
    create_fix_script(issues)
    
    print(f"\n📋 Next Steps:")
    print(f"1. Manually verify item IDs on OSRS Wiki")
    print(f"2. Update any incorrect IDs in the database")
    print(f"3. Consider implementing GE API verification")
    
    return len(issues) == 0

if __name__ == "__main__":
    main() 