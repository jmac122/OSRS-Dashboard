#!/usr/bin/env python3
"""
Debug database content for slayer masters and monsters
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.database_service import item_db

def debug_slayer_data():
    """Debug what slayer data is actually in the database"""
    print("🔍 Debugging Slayer Database Content...")
    
    try:
        # Get masters data
        print("\n👑 Slayer Masters:")
        masters_data = item_db.get_global_items('slayer', 'masters')
        if masters_data:
            for master_id, master_info in masters_data.items():
                print(f"  - {master_id}: {master_info.get('name', 'Unknown')}")
                print(f"    Combat Req: {master_info.get('combat_req', 'N/A')}")
                print(f"    Assignments: {len(master_info.get('task_assignments', {}))}")
                if master_info.get('task_assignments'):
                    print(f"    Assignment IDs: {list(master_info.get('task_assignments', {}).keys())[:5]}...")
        else:
            print("  No masters data found!")
        
        # Get monsters data
        print("\n👹 Slayer Monsters:")
        monsters_data = item_db.get_global_items('slayer', 'monsters')
        if monsters_data:
            print(f"  Total monsters: {len(monsters_data)}")
            for i, (monster_id, monster_info) in enumerate(monsters_data.items()):
                if i < 10:  # Show first 10
                    print(f"  - {monster_id}: {monster_info.get('name', 'Unknown')}")
                    print(f"    Slayer Req: {monster_info.get('slayer_level_req', 'N/A')}")
                    print(f"    Drop Table: {len(monster_info.get('drop_table', {}))}")
        else:
            print("  No monsters data found!")
        
        # Check specific assignment matching
        print("\n🔗 Assignment Matching Check:")
        if masters_data and monsters_data:
            nieve_data = masters_data.get('nieve')
            if nieve_data:
                assignments = nieve_data.get('task_assignments', {})
                print(f"Nieve has {len(assignments)} assignments:")
                for assignment_id in list(assignments.keys())[:10]:
                    monster_exists = assignment_id in monsters_data
                    print(f"  - {assignment_id}: {'✅' if monster_exists else '❌'} (in monsters DB)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_slayer_data() 