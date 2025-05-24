#!/usr/bin/env python3
"""
Comprehensive data population script for OSRS GP Tracker.
Includes ALL items specifically requested by the user.
"""

import sys
import os
import requests
import json
import time

# Add the backend directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_service import item_db
from utils.auth_service import auth_service

# Base URL for our API
BASE_URL = "http://localhost:5000"

class ComprehensiveDataPopulator:
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate_admin(self):
        """Authenticate as admin for data population"""
        print("🔐 Authenticating as admin...")
        
        auth_data = {
            "username": "admin",
            "password": "osrsadmin123"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/login",
            json=auth_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Admin authentication successful")
                self.authenticated = True
                return True
        
        print(f"❌ Admin authentication failed: {response.text}")
        return False
    
    def add_global_item(self, activity_type, category, item_id, item_data):
        """Add a global item via API"""
        if not self.authenticated:
            print("❌ Not authenticated!")
            return False
        
        payload = {
            "item_id": item_id,
            "item_data": item_data
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/items/{activity_type}/{category}",
            json=payload
        )
        
        if response.status_code == 200:
            print(f"✅ Added {activity_type}/{category}/{item_id}")
            return True
        else:
            print(f"❌ Failed to add {item_id}: {response.text}")
            return False
    
    def populate_all_farming_herbs(self):
        """Populate ALL common farming herbs as requested"""
        print("\n🌿 Populating ALL Farming Herbs...")
        
        # All common herbs (Ranarr, Snapdragon, Torstol, Kwuarm, Dwarf weed, Cadantine, Lantadyme, Avantoe, Irit)
        herbs = {
            "ranarr_weed": {
                "name": "Ranarr Weed",
                "wiki_id": "Ranarr_weed",
                "seed_id": 5295,
                "herb_id": 207,
                "growth_time_minutes": 80,
                "farming_level_req": 32,
                "default_yield": 8.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Ranarr_weed",
                "category": "herb",
                "description": "A common profitable herb, good for intermediate farmers"
            },
            "snapdragon": {
                "name": "Snapdragon",
                "wiki_id": "Snapdragon",
                "seed_id": 5300,
                "herb_id": 3000,
                "growth_time_minutes": 80,
                "farming_level_req": 62,
                "default_yield": 7.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Snapdragon",
                "category": "herb", 
                "description": "High-level herb with good profit margins"
            },
            "torstol": {
                "name": "Torstol",
                "wiki_id": "Torstol",
                "seed_id": 5309,
                "herb_id": 219,
                "growth_time_minutes": 80,
                "farming_level_req": 85,
                "default_yield": 8.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Torstol",
                "category": "herb",
                "description": "Highest level herb with excellent profit potential"
            },
            "kwuarm": {
                "name": "Kwuarm",
                "wiki_id": "Kwuarm",
                "seed_id": 5299,
                "herb_id": 217,
                "growth_time_minutes": 80,
                "farming_level_req": 56,
                "default_yield": 7.8,
                "wiki_url": "https://oldschool.runescape.wiki/w/Kwuarm",
                "category": "herb",
                "description": "Mid-high level herb with consistent profits"
            },
            "dwarf_weed": {
                "name": "Dwarf Weed",
                "wiki_id": "Dwarf_weed",
                "seed_id": 5303,
                "herb_id": 217,
                "growth_time_minutes": 80,
                "farming_level_req": 79,
                "default_yield": 7.2,
                "wiki_url": "https://oldschool.runescape.wiki/w/Dwarf_weed",
                "category": "herb",
                "description": "High-level herb used in ranging potions"
            },
            "cadantine": {
                "name": "Cadantine",
                "wiki_id": "Cadantine",
                "seed_id": 5301,
                "herb_id": 215,
                "growth_time_minutes": 80,
                "farming_level_req": 67,
                "default_yield": 7.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Cadantine",
                "category": "herb",
                "description": "High level herb used in prayer potions"
            },
            "lantadyme": {
                "name": "Lantadyme",
                "wiki_id": "Lantadyme",
                "seed_id": 5302,
                "herb_id": 2481,
                "growth_time_minutes": 80,
                "farming_level_req": 73,
                "default_yield": 7.3,
                "wiki_url": "https://oldschool.runescape.wiki/w/Lantadyme",
                "category": "herb",
                "description": "High level herb used in antifire potions"
            },
            "avantoe": {
                "name": "Avantoe",
                "wiki_id": "Avantoe",
                "seed_id": 5298,
                "herb_id": 211,
                "growth_time_minutes": 80,
                "farming_level_req": 50,
                "default_yield": 8.1,
                "wiki_url": "https://oldschool.runescape.wiki/w/Avantoe",
                "category": "herb",
                "description": "Mid-level herb with moderate profits"
            },
            "irit_leaf": {
                "name": "Irit Leaf",
                "wiki_id": "Irit_leaf",
                "seed_id": 5297,
                "herb_id": 209,
                "growth_time_minutes": 80,
                "farming_level_req": 44,
                "default_yield": 8.3,
                "wiki_url": "https://oldschool.runescape.wiki/w/Irit_leaf",
                "category": "herb",
                "description": "Mid-level herb used in various potions"
            }
        }
        
        success_count = 0
        for herb_id, herb_data in herbs.items():
            if self.add_global_item("farming", "herbs", herb_id, herb_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🌿 Farming herbs: {success_count}/{len(herbs)} added successfully")
        return success_count
    
    def populate_all_birdhouse_types(self):
        """Populate ALL birdhouse log types as requested"""
        print("\n🏠 Populating ALL Birdhouse Types...")
        
        # All log types (Oak, Willow, Teak, Maple, Mahogany, Yew, Magic, Redwood)
        birdhouses = {
            "regular_birdhouse": {
                "name": "Regular Birdhouse",
                "wiki_id": "Bird_house",
                "log_id": 1511,  # Regular logs
                "hunter_req": 5,
                "exp_per_birdhouse": 280,
                "avg_nests_per_run": 8.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Bird_house",
                "category": "birdhouse",
                "description": "Basic birdhouse for early hunters"
            },
            "oak_birdhouse": {
                "name": "Oak Birdhouse", 
                "wiki_id": "Oak_bird_house",
                "log_id": 1521,  # Oak logs
                "hunter_req": 15,
                "exp_per_birdhouse": 420,
                "avg_nests_per_run": 8.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Oak_bird_house",
                "category": "birdhouse",
                "description": "Improved birdhouse with better nest rates"
            },
            "willow_birdhouse": {
                "name": "Willow Birdhouse",
                "wiki_id": "Willow_bird_house", 
                "log_id": 1519,  # Willow logs
                "hunter_req": 25,
                "exp_per_birdhouse": 560,
                "avg_nests_per_run": 9.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Willow_bird_house",
                "category": "birdhouse",
                "description": "Mid-level birdhouse with good efficiency"
            },
            "teak_birdhouse": {
                "name": "Teak Birdhouse",
                "wiki_id": "Teak_bird_house",
                "log_id": 6333,  # Teak logs
                "hunter_req": 35,
                "exp_per_birdhouse": 700,
                "avg_nests_per_run": 9.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Teak_bird_house",
                "category": "birdhouse",
                "description": "High-tier birdhouse with good nest rates"
            },
            "maple_birdhouse": {
                "name": "Maple Birdhouse",
                "wiki_id": "Maple_bird_house",
                "log_id": 1517,  # Maple logs
                "hunter_req": 45,
                "exp_per_birdhouse": 820,
                "avg_nests_per_run": 10.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Maple_bird_house",
                "category": "birdhouse",
                "description": "High-level birdhouse with excellent nest yields"
            },
            "mahogany_birdhouse": {
                "name": "Mahogany Birdhouse",
                "wiki_id": "Mahogany_bird_house",
                "log_id": 6332,  # Mahogany logs
                "hunter_req": 50,
                "exp_per_birdhouse": 960,
                "avg_nests_per_run": 10.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Mahogany_bird_house",
                "category": "birdhouse",
                "description": "Premium birdhouse with very high nest rates"
            },
            "yew_birdhouse": {
                "name": "Yew Birdhouse",
                "wiki_id": "Yew_bird_house",
                "log_id": 1515,  # Yew logs
                "hunter_req": 59,
                "exp_per_birdhouse": 1020,
                "avg_nests_per_run": 11.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Yew_bird_house",
                "category": "birdhouse",
                "description": "High-end birdhouse with excellent experience and nests"
            },
            "magic_birdhouse": {
                "name": "Magic Birdhouse",
                "wiki_id": "Magic_bird_house",
                "log_id": 1513,  # Magic logs
                "hunter_req": 75,
                "exp_per_birdhouse": 1140,
                "avg_nests_per_run": 11.5,
                "wiki_url": "https://oldschool.runescape.wiki/w/Magic_bird_house",
                "category": "birdhouse",
                "description": "Top-tier birdhouse with maximum nest yields"
            },
            "redwood_birdhouse": {
                "name": "Redwood Birdhouse",
                "wiki_id": "Redwood_bird_house",
                "log_id": 19669,  # Redwood logs
                "hunter_req": 90,
                "exp_per_birdhouse": 1200,
                "avg_nests_per_run": 12.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Redwood_bird_house",
                "category": "birdhouse",
                "description": "Highest level birdhouse with best possible yields"
            }
        }
        
        success_count = 0
        for birdhouse_id, birdhouse_data in birdhouses.items():
            if self.add_global_item("hunter", "birdhouses", birdhouse_id, birdhouse_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🏠 Birdhouses: {success_count}/{len(birdhouses)} added successfully")
        return success_count
    
    def populate_all_gotr_strategies(self):
        """Populate ALL GOTR rune strategies as requested"""
        print("\n🔮 Populating ALL GOTR Rune Strategies...")
        
        # All rune types (Blood, Soul, Death, Nature, Law, Cosmic, Astral, Wrath)
        strategies = {
            "blood_runes_focus": {
                "name": "Blood Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 565,  # Blood rune
                "avg_runes_per_game": 150,
                "points_req": 77,
                "runecraft_level_req": 77,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "High-level strategy focusing on valuable blood runes"
            },
            "soul_runes_focus": {
                "name": "Soul Runes Focus", 
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 566,  # Soul rune
                "avg_runes_per_game": 120,
                "points_req": 90,
                "runecraft_level_req": 90,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "Highest level strategy for maximum profit"
            },
            "death_runes_focus": {
                "name": "Death Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 560,  # Death rune
                "avg_runes_per_game": 180,
                "points_req": 65,
                "runecraft_level_req": 65,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "High-level strategy with consistent profit from death runes"
            },
            "nature_runes_focus": {
                "name": "Nature Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 561,  # Nature rune
                "avg_runes_per_game": 200,
                "points_req": 44,
                "runecraft_level_req": 44,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "Mid-level strategy with consistent profits"
            },
            "law_runes_focus": {
                "name": "Law Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies", 
                "rune_id": 563,  # Law rune
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
                "rune_id": 564,  # Cosmic rune
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
                "rune_id": 9075,  # Astral rune
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
                "rune_id": 21880,  # Wrath rune
                "avg_runes_per_game": 100,
                "points_req": 95,
                "runecraft_level_req": 95,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "Highest level strategy with very valuable wrath runes"
            }
        }
        
        success_count = 0
        for strategy_id, strategy_data in strategies.items():
            if self.add_global_item("runecraft", "gotr_strategies", strategy_id, strategy_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🔮 GOTR strategies: {success_count}/{len(strategies)} added successfully")
        return success_count
    
    def populate_profitable_slayer_monsters(self):
        """Populate profitable slayer monsters as requested"""
        print("\n⚔️ Populating Profitable Slayer Monsters...")
        
        # Profitable monsters including those mentioned + more
        monsters = {
            "rune_dragons": {
                "name": "Rune Dragons",
                "wiki_id": "Rune_dragon",
                "avg_loot_value_per_kill": 37000,
                "kills_per_hour": 40,
                "avg_supply_cost_per_hour": 100000,
                "slayer_level_req": 1,
                "combat_level": 380,
                "wiki_url": "https://oldschool.runescape.wiki/w/Rune_dragon",
                "category": "dragon",
                "description": "High-level dragons with valuable rune drops"
            },
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
            "vorkath": {
                "name": "Vorkath",
                "wiki_id": "Vorkath",
                "avg_loot_value_per_kill": 150000,
                "kills_per_hour": 25,
                "avg_supply_cost_per_hour": 80000,
                "slayer_level_req": 1,
                "combat_level": 732,
                "wiki_url": "https://oldschool.runescape.wiki/w/Vorkath",
                "category": "boss",
                "description": "Profitable boss with consistent high-value drops"
            },
            "zulrah": {
                "name": "Zulrah",
                "wiki_id": "Zulrah",
                "avg_loot_value_per_kill": 120000,
                "kills_per_hour": 30,
                "avg_supply_cost_per_hour": 70000,
                "slayer_level_req": 1,
                "combat_level": 725,
                "wiki_url": "https://oldschool.runescape.wiki/w/Zulrah",
                "category": "boss",
                "description": "Snake boss with valuable unique drops"
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
        for monster_id, monster_data in monsters.items():
            if self.add_global_item("slayer", "monsters", monster_id, monster_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"⚔️ Slayer monsters: {success_count}/{len(monsters)} added successfully")
        return success_count
    
    def verify_comprehensive_data(self):
        """Verify that all comprehensive data was populated"""
        print("\n🔍 Verifying comprehensive data population...")
        
        test_cases = [
            ("farming", "herbs", 9),      # Should have 9 herbs
            ("hunter", "birdhouses", 9),  # Should have 9 birdhouse types  
            ("runecraft", "gotr_strategies", 8),  # Should have 8 rune strategies
            ("slayer", "monsters", 10)    # Should have 10+ monsters
        ]
        
        total_items = 0
        all_success = True
        
        for activity_type, category, expected_count in test_cases:
            response = self.session.get(f"{BASE_URL}/api/items/{activity_type}?category={category}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', {})
                actual_count = len(items)
                total_items += actual_count
                
                if actual_count >= expected_count:
                    print(f"✅ {activity_type}/{category}: {actual_count} items (expected {expected_count}+)")
                else:
                    print(f"⚠️ {activity_type}/{category}: {actual_count} items (expected {expected_count}+)")
                    all_success = False
                    
                # Show some examples
                if items:
                    item_names = [items[item_id].get('name', 'N/A') for item_id in list(items.keys())[:3]]
                    print(f"   Examples: {', '.join(item_names)}")
            else:
                print(f"❌ Failed to retrieve {activity_type}/{category}: {response.text}")
                all_success = False
        
        print(f"\n📊 Total items: {total_items} (target: 36+)")
        return all_success and total_items >= 36
    
    def run_comprehensive_population(self):
        """Run the comprehensive data population process"""
        print("🚀 Starting COMPREHENSIVE Data Population")
        print("=" * 60)
        print("📋 Target:")
        print("   • 9 Farming herbs")
        print("   • 9 Birdhouse types") 
        print("   • 8 GOTR rune strategies")
        print("   • 10+ Slayer monsters")
        print("   • TOTAL: 36+ items")
        print("=" * 60)
        
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed.")
            return False
        
        total_success = 0
        total_success += self.populate_all_farming_herbs()
        total_success += self.populate_all_birdhouse_types()
        total_success += self.populate_all_gotr_strategies()
        total_success += self.populate_profitable_slayer_monsters()
        
        print(f"\n📊 Population Summary:")
        print(f"Total items added: {total_success}")
        
        success = self.verify_comprehensive_data()
        
        if success:
            print(f"\n🎉 COMPREHENSIVE Data Population Complete!")
            print(f"✅ Database now contains full coverage as requested")
            print(f"🔄 Next: Update frontend to use comprehensive database")
        else:
            print(f"\n⚠️ Some issues detected in population")
        
        return success

if __name__ == "__main__":
    print("OSRS GP Tracker - COMPREHENSIVE Data Population")
    print("This will populate ALL requested items (36+ total)")
    print()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Backend not responding. Please start the backend first.")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please start the backend first.")
        exit(1)
    
    # Run comprehensive population
    populator = ComprehensiveDataPopulator()
    success = populator.run_comprehensive_population()
    
    if success:
        print("\n✅ Comprehensive data population completed successfully!")
        print("🎯 Database now ready for full-featured comparisons!")
    else:
        print("\n❌ Comprehensive data population failed!")
        exit(1) 