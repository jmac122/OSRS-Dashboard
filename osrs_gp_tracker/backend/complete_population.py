#!/usr/bin/env python3
"""
Complete the missing data population for GOTR and Slayer.
"""

import sys
import os
import requests
import json
import time

# Add the backend directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def add_item(session, activity_type, category, item_id, item_data):
    """Add a single item"""
    payload = {"item_id": item_id, "item_data": item_data}
    
    response = session.post(
        f"{BASE_URL}/api/admin/items/{activity_type}/{category}",
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✅ Added {activity_type}/{category}/{item_id}")
        return True
    else:
        print(f"❌ Failed to add {item_id}: {response.text}")
        return False

def complete_gotr_strategies(session):
    """Add the missing GOTR strategies"""
    print("\n🔮 Completing GOTR Strategies...")
    
    # Missing strategies (Death, Law, Cosmic, Astral, Wrath)
    missing_strategies = {
        "death_runes_focus": {
            "name": "Death Runes Focus",
            "wiki_id": "Guardians_of_the_Rift/Strategies",
            "rune_id": 560,
            "avg_runes_per_game": 180,
            "points_req": 65,
            "runecraft_level_req": 65,
            "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
            "category": "gotr_strategy",
            "description": "High-level strategy with consistent profit from death runes"
        },
        "law_runes_focus": {
            "name": "Law Runes Focus",
            "wiki_id": "Guardians_of_the_Rift/Strategies", 
            "rune_id": 563,
            "avg_runes_per_game": 190,
            "points_req": 54,
            "runecraft_level_req": 54,
            "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
            "category": "gotr_strategy",
            "description": "Mid-high level strategy focusing on law runes"
        },
        "cosmic_runes_focus": {
            "name": "Cosmic Runes Focus",
            "wiki_id": "Guardians_of_the_Rift/Strategies",
            "rune_id": 564,
            "avg_runes_per_game": 210,
            "points_req": 27,
            "runecraft_level_req": 27,
            "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
            "category": "gotr_strategy",
            "description": "Early-mid level strategy with decent profits"
        },
        "astral_runes_focus": {
            "name": "Astral Runes Focus",
            "wiki_id": "Guardians_of_the_Rift/Strategies",
            "rune_id": 9075,
            "avg_runes_per_game": 170,
            "points_req": 40,
            "runecraft_level_req": 40,
            "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
            "category": "gotr_strategy",
            "description": "Mid-level strategy with good astral rune profits"
        },
        "wrath_runes_focus": {
            "name": "Wrath Runes Focus",
            "wiki_id": "Guardians_of_the_Rift/Strategies",
            "rune_id": 21880,
            "avg_runes_per_game": 100,
            "points_req": 95,
            "runecraft_level_req": 95,
            "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
            "category": "gotr_strategy",
            "description": "Highest level strategy with very valuable wrath runes"
        }
    }
    
    success_count = 0
    for strategy_id, strategy_data in missing_strategies.items():
        if add_item(session, "runecraft", "gotr_strategies", strategy_id, strategy_data):
            success_count += 1
        time.sleep(0.1)
    
    print(f"🔮 Added {success_count}/5 missing GOTR strategies")
    return success_count

def complete_slayer_monsters(session):
    """Add the missing slayer monsters"""
    print("\n⚔️ Completing Slayer Monsters...")
    
    # Missing monsters (Alchemical Hydra, Nechryael, Gargoyles, etc.)
    missing_monsters = {
        "alchemical_hydra": {
            "name": "Alchemical Hydra",
            "wiki_id": "Alchemical_Hydra",
            "avg_loot_value_per_kill": 180000,
            "kills_per_hour": 28,
            "avg_supply_cost_per_hour": 120000,
            "slayer_level_req": 95,
            "combat_level": 426,
            "wiki_url": "https://oldschool.runescape.wiki/w/Alchemical_Hydra",
            "category": "hydra",
            "description": "Extremely profitable high-level slayer boss"
        },
        "nechryael": {
            "name": "Nechryael",
            "wiki_id": "Nechryael",
            "avg_loot_value_per_kill": 8500,
            "kills_per_hour": 280,
            "avg_supply_cost_per_hour": 50000,
            "slayer_level_req": 80,
            "combat_level": 115,
            "wiki_url": "https://oldschool.runescape.wiki/w/Nechryael",
            "category": "demon",
            "description": "Fast profitable task with good alchables"
        },
        "gargoyles": {
            "name": "Gargoyles",
            "wiki_id": "Gargoyle",
            "avg_loot_value_per_kill": 4200,
            "kills_per_hour": 350,
            "avg_supply_cost_per_hour": 30000,
            "slayer_level_req": 75,
            "combat_level": 111,
            "wiki_url": "https://oldschool.runescape.wiki/w/Gargoyle",
            "category": "gargoyle",
            "description": "Consistent profitable task with good alchables"
        },
        "brutal_black_dragons": {
            "name": "Brutal Black Dragons",
            "wiki_id": "Brutal_black_dragon",
            "avg_loot_value_per_kill": 25000,
            "kills_per_hour": 55,
            "avg_supply_cost_per_hour": 85000,
            "slayer_level_req": 1,
            "combat_level": 318,
            "wiki_url": "https://oldschool.runescape.wiki/w/Brutal_black_dragon",
            "category": "dragon",
            "description": "High-value dragon with consistent drops"
        },
        "abyssal_demons": {
            "name": "Abyssal Demons",
            "wiki_id": "Abyssal_demon",
            "avg_loot_value_per_kill": 6800,
            "kills_per_hour": 400,
            "avg_supply_cost_per_hour": 40000,
            "slayer_level_req": 85,
            "combat_level": 124,
            "wiki_url": "https://oldschool.runescape.wiki/w/Abyssal_demon",
            "category": "demon",
            "description": "Fast task with valuable whip drops"
        },
        "skeletal_wyverns": {
            "name": "Skeletal Wyverns",
            "wiki_id": "Skeletal_Wyvern",
            "avg_loot_value_per_kill": 15000,
            "kills_per_hour": 110,
            "avg_supply_cost_per_hour": 65000,
            "slayer_level_req": 72,
            "combat_level": 140,
            "wiki_url": "https://oldschool.runescape.wiki/w/Skeletal_Wyvern",
            "category": "wyvern",
            "description": "Mid-high level task with valuable unique drops"
        },
        "cerberus": {
            "name": "Cerberus",
            "wiki_id": "Cerberus",
            "avg_loot_value_per_kill": 75000,
            "kills_per_hour": 65,
            "avg_supply_cost_per_hour": 90000,
            "slayer_level_req": 91,
            "combat_level": 318,
            "wiki_url": "https://oldschool.runescape.wiki/w/Cerberus",
            "category": "boss",
            "description": "High-level slayer boss with valuable uniques"
        }
    }
    
    success_count = 0
    for monster_id, monster_data in missing_monsters.items():
        if add_item(session, "slayer", "monsters", monster_id, monster_data):
            success_count += 1
        time.sleep(0.1)
    
    print(f"⚔️ Added {success_count}/7 missing slayer monsters")
    return success_count

def add_missing_birdhouse(session):
    """Add the missing 9th birdhouse"""
    print("\n🏠 Adding Missing Birdhouse...")
    
    redwood_birdhouse = {
        "name": "Redwood Birdhouse",
        "wiki_id": "Redwood_bird_house",
        "log_id": 19669,
        "hunter_req": 90,
        "exp_per_birdhouse": 1200,
        "avg_nests_per_run": 12.0,
        "wiki_url": "https://oldschool.runescape.wiki/w/Redwood_bird_house",
        "category": "birdhouse",
        "description": "Highest level birdhouse with best possible yields"
    }
    
    success = add_item(session, "hunter", "birdhouses", "redwood_birdhouse", redwood_birdhouse)
    print(f"🏠 Added {1 if success else 0}/1 missing birdhouse")
    return 1 if success else 0

def main():
    print("🔄 Completing Missing Data Population")
    print("=" * 40)
    
    session = authenticate_admin()
    if not session:
        return False
    
    total_added = 0
    total_added += add_missing_birdhouse(session)
    total_added += complete_gotr_strategies(session)
    total_added += complete_slayer_monsters(session)
    
    print(f"\n📊 Completion Summary:")
    print(f"Total new items added: {total_added}")
    
    # Final verification
    print("\n🔍 Final verification...")
    resp = requests.get(f"{BASE_URL}/api/items/farming?category=herbs")
    farming_count = len(resp.json().get('items', {})) if resp.status_code == 200 else 0
    
    resp = requests.get(f"{BASE_URL}/api/items/hunter?category=birdhouses")
    birdhouse_count = len(resp.json().get('items', {})) if resp.status_code == 200 else 0
    
    resp = requests.get(f"{BASE_URL}/api/items/runecraft?category=gotr_strategies")
    gotr_count = len(resp.json().get('items', {})) if resp.status_code == 200 else 0
    
    resp = requests.get(f"{BASE_URL}/api/items/slayer?category=monsters")
    slayer_count = len(resp.json().get('items', {})) if resp.status_code == 200 else 0
    
    total_items = farming_count + birdhouse_count + gotr_count + slayer_count
    
    print(f"✅ Farming herbs: {farming_count}/9")
    print(f"✅ Birdhouses: {birdhouse_count}/9")
    print(f"✅ GOTR strategies: {gotr_count}/8")
    print(f"✅ Slayer monsters: {slayer_count}/10")
    print(f"📊 TOTAL: {total_items}/36+")
    
    if total_items >= 36:
        print(f"\n🎉 SUCCESS! Comprehensive database complete!")
        return True
    else:
        print(f"\n⚠️ Still missing items. Target: 36+, Actual: {total_items}")
        return False

if __name__ == "__main__":
    main() 