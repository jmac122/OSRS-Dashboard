#!/usr/bin/env python3
"""
Fix the Dwarf Weed herb_id issue (should be 2486, not 217).
"""

import requests

BASE_URL = "http://localhost:5000"

def fix_dwarf_weed():
    """Fix the Dwarf Weed herb_id"""
    print("🔧 Fixing Dwarf Weed herb_id...")
    
    # Authenticate as admin
    session = requests.Session()
    auth_data = {"username": "admin", "password": "osrsadmin123"}
    response = session.post(f"{BASE_URL}/api/admin/login", json=auth_data)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    print("✅ Admin authenticated")
    
    # Get current dwarf weed data
    resp = session.get(f"{BASE_URL}/api/items/farming?category=herbs")
    if resp.status_code != 200:
        print("❌ Failed to retrieve farming herbs")
        return False
    
    items = resp.json().get('items', {})
    dwarf_weed = items.get('dwarf_weed')
    
    if not dwarf_weed:
        print("❌ Dwarf weed not found in database")
        return False
    
    print(f"📋 Current dwarf weed herb_id: {dwarf_weed.get('herb_id')}")
    
    # Update the herb_id
    dwarf_weed['herb_id'] = 2486  # Correct ID
    
    # Submit the fix
    payload = {
        "item_id": "dwarf_weed",
        "item_data": dwarf_weed
    }
    
    response = session.post(
        f"{BASE_URL}/api/admin/items/farming/herbs",
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✅ Fixed! Dwarf Weed herb_id updated to 2486")
        return True
    else:
        print(f"❌ Failed to update: {response.text}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Critical Item ID Issue")
    print("=" * 35)
    
    success = fix_dwarf_weed()
    
    if success:
        print("\n✅ Critical fix applied successfully!")
        print("🔍 Run verify_item_ids.py again to confirm")
    else:
        print("\n❌ Fix failed!") 