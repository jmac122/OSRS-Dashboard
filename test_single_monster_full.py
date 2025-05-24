#!/usr/bin/env python3
"""
Test full monster sync process for a single monster
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService

def test_single_monster_full():
    """Test the complete monster processing pipeline"""
    print("Testing complete monster processing...")
    
    wiki_service = OSRSWikiSyncService()
    
    # Simulate processing a monster that would be found in the sync
    # Using a monster that's NOT in the hardcoded combat_stats
    monster_id = 'dust_devils'
    monster_info = {
        'name': 'Dust devils',
        'wiki_path': '/w/Dust_devil',
        'slayer_req': 65
    }
    
    print(f"Processing: {monster_info['name']}")
    
    # Simulate the process that happens in sync_slayer_monsters
    monster_data = {
        'name': monster_info['name'],
        'wiki_slug': monster_id,
        'slayer_level_req': monster_info.get('slayer_req', 1),
        'combat_level': 93,  # Typical dust devil stats
        'monster_hp': 105,
        'drop_table': {
            'always': [{'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}],
            'common': [{'item_id': 995, 'quantity_range': [100, 300], 'probability': 0.2}],
            'rare': [],
            'very_rare': []
        }
    }
    
    # Check if in hardcoded stats (it shouldn't be)
    hardcoded_monsters = ['gargoyles', 'abyssal_demons', 'alchemical_hydra', 'nechryael', 
                         'rune_dragons', 'cerberus', 'vorkath', 'zulrah']
    
    if monster_id in hardcoded_monsters:
        print("Using hardcoded combat stats")
    else:
        print("Using estimated combat stats")
        estimated_metrics = wiki_service._estimate_combat_metrics(monster_data)
        monster_data.update({
            'avg_kill_time_seconds_base': estimated_metrics['estimated_kill_time_seconds'],
            'base_kph_range': [estimated_metrics['estimated_kills_per_hour'] - 10, 
                             estimated_metrics['estimated_kills_per_hour'] + 10],
            'common_supply_cost_per_hour_base': estimated_metrics['estimated_supply_cost_per_hour'],
            'notes': f'Estimated metrics based on combat level {monster_data.get("combat_level", "unknown")} and Slayer req {monster_data.get("slayer_level_req", 1)}.'
        })
    
    # Calculate the final validation fields (same as in sync_slayer_monsters)
    expected_loot = wiki_service._calculate_expected_loot_value(monster_data['drop_table'])
    base_kph = sum(monster_data.get('base_kph_range', [30, 40])) / 2
    supply_cost = monster_data.get('common_supply_cost_per_hour_base', 50000)
    
    # Add required fields for validation
    monster_data.update({
        'avg_loot_value_per_kill': expected_loot,
        'kills_per_hour': base_kph,
        'avg_supply_cost_per_hour': supply_cost
    })
    
    # Display results
    print("\n=== FINAL VALIDATION FIELDS ===")
    print(f"avg_loot_value_per_kill: {monster_data['avg_loot_value_per_kill']:.2f} GP")
    print(f"kills_per_hour: {monster_data['kills_per_hour']:.0f} KPH")
    print(f"avg_supply_cost_per_hour: {monster_data['avg_supply_cost_per_hour']:,} GP/hr")
    
    print(f"\n=== MONSTER DETAILS ===")
    print(f"Combat Level: {monster_data.get('combat_level', 'unknown')}")
    print(f"HP: {monster_data.get('monster_hp', 'unknown')}")
    print(f"Slayer Requirement: {monster_data.get('slayer_level_req', 1)}")
    print(f"Notes: {monster_data.get('notes', 'No notes')}")
    
    # Verify no default values
    if monster_data['kills_per_hour'] == 125:
        print("\n❌ WARNING: Still using old default KPH value!")
    elif monster_data['avg_supply_cost_per_hour'] == 50000:
        print("\n❌ WARNING: Still using old default supply cost!")
    else:
        print("\n✅ SUCCESS: Using dynamic estimated values!")

if __name__ == "__main__":
    test_single_monster_full() 