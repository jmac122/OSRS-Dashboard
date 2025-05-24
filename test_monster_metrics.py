#!/usr/bin/env python3
"""
Test monster metrics estimation
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService

def test_monster_metrics():
    """Test monster metrics estimation for different monster types"""
    print("Testing monster metrics estimation...")
    
    wiki_service = OSRSWikiSyncService()
    
    # Test different monster types
    test_monsters = [
        {
            'name': 'Gargoyles (known)',
            'combat_level': 111,
            'monster_hp': 105,
            'slayer_level_req': 75,
            'monster_id': 'gargoyles'  # This should use hardcoded stats
        },
        {
            'name': 'Low Level Monster',
            'combat_level': 50,
            'monster_hp': 40,
            'slayer_level_req': 1,
            'monster_id': 'unknown_low'  # This should use estimation
        },
        {
            'name': 'Mid Level Monster',
            'combat_level': 150,
            'monster_hp': 120,
            'slayer_level_req': 60,
            'monster_id': 'unknown_mid'  # This should use estimation
        },
        {
            'name': 'High Level Monster',
            'combat_level': 350,
            'monster_hp': 400,
            'slayer_level_req': 85,
            'monster_id': 'unknown_high'  # This should use estimation
        },
        {
            'name': 'Boss Level Monster',
            'combat_level': 500,
            'monster_hp': 800,
            'slayer_level_req': 95,
            'monster_id': 'unknown_boss'  # This should use estimation
        }
    ]
    
    for monster in test_monsters:
        print(f"\n--- {monster['name']} ---")
        print(f"Combat Level: {monster['combat_level']}, HP: {monster['monster_hp']}, Slayer: {monster['slayer_level_req']}")
        
        # Test estimation
        estimated = wiki_service._estimate_combat_metrics(monster)
        print(f"Estimated KPH: {estimated['estimated_kills_per_hour']}")
        print(f"Estimated Supply Cost/hr: {estimated['estimated_supply_cost_per_hour']:,}")
        print(f"Estimated Kill Time: {estimated['estimated_kill_time_seconds']} seconds")
        
        # Test what would actually be used in the sync
        combat_stats = {
            'gargoyles': {
                'base_kph_range': [350, 400],
                'common_supply_cost_per_hour_base': 30000,
            }
        }
        
        if monster['monster_id'] in combat_stats:
            actual_kph = sum(combat_stats[monster['monster_id']]['base_kph_range']) / 2
            actual_supply = combat_stats[monster['monster_id']]['common_supply_cost_per_hour_base']
            print(f"ACTUAL (hardcoded) KPH: {actual_kph}")
            print(f"ACTUAL (hardcoded) Supply Cost/hr: {actual_supply:,}")
        else:
            actual_kph = estimated['estimated_kills_per_hour']
            actual_supply = estimated['estimated_supply_cost_per_hour']
            print(f"ACTUAL (estimated) KPH: {actual_kph}")
            print(f"ACTUAL (estimated) Supply Cost/hr: {actual_supply:,}")

if __name__ == "__main__":
    test_monster_metrics() 