#!/usr/bin/env python3
"""
Initial data population script for OSRS GP Tracker.
Transforms existing hardcoded data into database structure.
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

class DataPopulator:
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
    
    def populate_farming_herbs(self):
        """Populate farming herb data"""
        print("\n🌿 Populating Farming Herbs...")
        
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
            }
        }
        
        success_count = 0
        for herb_id, herb_data in herbs.items():
            if self.add_global_item("farming", "herbs", herb_id, herb_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🌿 Farming herbs: {success_count}/{len(herbs)} added successfully")
        return success_count
    
    def populate_birdhouse_types(self):
        """Populate birdhouse type data"""
        print("\n🏠 Populating Birdhouse Types...")
        
        birdhouses = {
            "regular_birdhouse": {
                "name": "Regular Birdhouse",
                "wiki_id": "Bird_house",
                "log_id": 1511,
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
                "log_id": 1521,
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
                "log_id": 1519,
                "hunter_req": 25,
                "exp_per_birdhouse": 560,
                "avg_nests_per_run": 9.0,
                "wiki_url": "https://oldschool.runescape.wiki/w/Willow_bird_house",
                "category": "birdhouse",
                "description": "Mid-level birdhouse with good efficiency"
            }
        }
        
        success_count = 0
        for birdhouse_id, birdhouse_data in birdhouses.items():
            if self.add_global_item("hunter", "birdhouses", birdhouse_id, birdhouse_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🏠 Birdhouses: {success_count}/{len(birdhouses)} added successfully")
        return success_count
    
    def populate_gotr_strategies(self):
        """Populate GOTR strategy data"""
        print("\n🔮 Populating GOTR Strategies...")
        
        strategies = {
            "blood_runes_focus": {
                "name": "Blood Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 565,
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
                "rune_id": 566,
                "avg_runes_per_game": 120,
                "points_req": 90,
                "runecraft_level_req": 90,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "Highest level strategy for maximum profit"
            },
            "nature_runes_focus": {
                "name": "Nature Runes Focus",
                "wiki_id": "Guardians_of_the_Rift/Strategies",
                "rune_id": 561,
                "avg_runes_per_game": 200,
                "points_req": 44,
                "runecraft_level_req": 44,
                "wiki_url": "https://oldschool.runescape.wiki/w/Guardians_of_the_Rift/Strategies",
                "category": "gotr_strategy",
                "description": "Mid-level strategy with consistent profits"
            }
        }
        
        success_count = 0
        for strategy_id, strategy_data in strategies.items():
            if self.add_global_item("runecraft", "gotr_strategies", strategy_id, strategy_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"🔮 GOTR strategies: {success_count}/{len(strategies)} added successfully")
        return success_count
    
    def populate_slayer_monsters(self):
        """Populate slayer monster data"""
        print("\n⚔️ Populating Slayer Monsters...")
        
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
            }
        }
        
        success_count = 0
        for monster_id, monster_data in monsters.items():
            if self.add_global_item("slayer", "monsters", monster_id, monster_data):
                success_count += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"⚔️ Slayer monsters: {success_count}/{len(monsters)} added successfully")
        return success_count
    
    def verify_data_retrieval(self):
        """Verify that populated data can be retrieved"""
        print("\n🔍 Verifying data retrieval...")
        
        test_cases = [
            ("farming", "herbs"),
            ("hunter", "birdhouses"), 
            ("runecraft", "gotr_strategies"),
            ("slayer", "monsters")
        ]
        
        for activity_type, category in test_cases:
            response = self.session.get(f"{BASE_URL}/api/items/{activity_type}?category={category}")
            
            if response.status_code == 200:
                data = response.json()
                item_count = len(data.get('items', {}))
                print(f"✅ {activity_type}/{category}: {item_count} items retrieved")
            else:
                print(f"❌ Failed to retrieve {activity_type}/{category}: {response.text}")
    
    def run_full_population(self):
        """Run the complete data population process"""
        print("🚀 Starting Phase 1: Initial Data Population")
        print("=" * 50)
        
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed.")
            return False
        
        total_success = 0
        total_success += self.populate_farming_herbs()
        total_success += self.populate_birdhouse_types()
        total_success += self.populate_gotr_strategies()
        total_success += self.populate_slayer_monsters()
        
        print(f"\n📊 Population Summary:")
        print(f"Total items added: {total_success}")
        
        self.verify_data_retrieval()
        
        print(f"\n🎉 Phase 1 Complete! Database populated with initial data.")
        print(f"Next: Update frontend to use database instead of hardcoded data.")
        
        return True

if __name__ == "__main__":
    print("OSRS GP Tracker - Initial Data Population")
    print("This script will populate the database with initial item data.")
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
    
    # Run population
    populator = DataPopulator()
    success = populator.run_full_population()
    
    if success:
        print("\n✅ Data population completed successfully!")
    else:
        print("\n❌ Data population failed!")
        exit(1) 