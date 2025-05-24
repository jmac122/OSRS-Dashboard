#!/usr/bin/env python3
"""
Test real monsters that would be found in comprehensive sync
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService

def test_real_monsters():
    """Test estimation for real monsters that would be found in sync"""
    print("Testing estimation for real OSRS monsters...")
    
    wiki_service = OSRSWikiSyncService()
    
    # Real monsters that would likely be found in the comprehensive sync
    real_monsters = [
        {'name': 'Cows', 'combat_level': 2, 'monster_hp': 8, 'slayer_level_req': 1},
        {'name': 'Spiders', 'combat_level': 1, 'monster_hp': 1, 'slayer_level_req': 1},
        {'name': 'Cave Crawlers', 'combat_level': 23, 'monster_hp': 22, 'slayer_level_req': 10},
        {'name': 'Bloodvelds', 'combat_level': 76, 'monster_hp': 120, 'slayer_level_req': 50},
        {'name': 'Dust Devils', 'combat_level': 93, 'monster_hp': 105, 'slayer_level_req': 65},
        {'name': 'Greater Demons', 'combat_level': 92, 'monster_hp': 87, 'slayer_level_req': 1},
        {'name': 'Black Demons', 'combat_level': 172, 'monster_hp': 157, 'slayer_level_req': 1},
        {'name': 'Dark Beasts', 'combat_level': 182, 'monster_hp': 220, 'slayer_level_req': 90},
        {'name': 'Wyrms', 'combat_level': 99, 'monster_hp': 130, 'slayer_level_req': 62},
        {'name': 'Drakes', 'combat_level': 192, 'monster_hp': 188, 'slayer_level_req': 84}
    ]
    
    print("\nMonster Estimates:")
    print("=" * 80)
    print(f"{'Monster':<15} {'Combat':<7} {'HP':<5} {'Slayer':<6} {'KPH':<5} {'Supply Cost':<12}")
    print("=" * 80)
    
    for monster in real_monsters:
        estimated = wiki_service._estimate_combat_metrics(monster)
        
        print(f"{monster['name']:<15} {monster['combat_level']:<7} {monster['monster_hp']:<5} "
              f"{monster['slayer_level_req']:<6} {estimated['estimated_kills_per_hour']:<5} "
              f"{estimated['estimated_supply_cost_per_hour']:,}")

if __name__ == "__main__":
    test_real_monsters() 