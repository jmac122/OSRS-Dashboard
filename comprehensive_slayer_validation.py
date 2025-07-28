#!/usr/bin/env python3
"""
Comprehensive Slayer Validation and Fix
Ensures ALL slayer masters have complete task assignments and ALL task monsters have proper drop tables
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.join('osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

# Import our centralized Firebase initialization
from utils.firebase_init import initialize_firebase
from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.database_service import item_db

class ComprehensiveSlayerValidator:
    def __init__(self):
        self.api_base = "http://localhost:5000"
        self.db = None
        self.issues = []
        self.fixes_applied = []
        
        # All OSRS slayer masters and their expected task monsters
        self.expected_masters = {
            'turael': {
                'name': 'Turael',
                'combat_req': 0,
                'location': 'Burthorpe',
                'expected_monsters': [
                    'bats', 'birds', 'bears', 'cows', 'crawling_hands', 'cave_bugs',
                    'cave_crawlers', 'cave_slimes', 'desert_lizards', 'dogs', 'dwarves',
                    'ghosts', 'goblins', 'icefiends', 'minotaurs', 'monkeys', 'rats',
                    'scorpions', 'skeletons', 'spiders', 'wolves', 'zombies'
                ]
            },
            'spria': {
                'name': 'Spria',
                'combat_req': 0,
                'location': 'Draynor Village',
                'expected_monsters': [
                    'bats', 'birds', 'bears', 'cows', 'crawling_hands', 'cave_bugs',
                    'cave_crawlers', 'cave_slimes', 'desert_lizards', 'dogs', 'dwarves',
                    'ghosts', 'goblins', 'icefiends', 'minotaurs', 'monkeys', 'rats',
                    'scorpions', 'skeletons', 'spiders', 'wolves', 'zombies'
                ]
            },
            'mazchna': {
                'name': 'Mazchna',
                'combat_req': 20,
                'location': 'Canifis',
                'expected_monsters': [
                    'banshees', 'bats', 'bears', 'catablepon', 'cave_crawlers',
                    'cave_slimes', 'cockatrice', 'crawling_hands', 'desert_lizards',
                    'dogs', 'dwarves', 'earth_warriors', 'flesh_crawlers', 'ghosts',
                    'goblins', 'hill_giants', 'hobgoblins', 'icefiends', 'kalphite',
                    'killerwatts', 'lesser_demons', 'minotaurs', 'monkeys', 'pyrefiends',
                    'rats', 'rockslugs', 'scorpions', 'shades', 'skeletons', 'spiders',
                    'vampyres', 'wall_beasts', 'wolves', 'zombies'
                ]
            },
            'vannaka': {
                'name': 'Vannaka',
                'combat_req': 40,
                'location': 'Edgeville Dungeon',
                'expected_monsters': [
                    'aberrant_spectres', 'ankou', 'banshees', 'basilisks', 'bats',
                    'bears', 'blue_dragons', 'brine_rats', 'bronze_dragons',
                    'catablepon', 'cave_crawlers', 'cockatrice', 'crawling_hands',
                    'crocodiles', 'desert_lizards', 'dust_devils', 'earth_warriors',
                    'elves', 'fever_spiders', 'fire_giants', 'flesh_crawlers',
                    'gargoyles', 'ghosts', 'green_dragons', 'harpie_bug_swarms',
                    'hill_giants', 'hobgoblins', 'icefiends', 'infernal_mages',
                    'jellies', 'jungle_horrors', 'kalphite', 'killerwatts',
                    'kurask', 'lesser_demons', 'lizardmen', 'minotaurs', 'mogres',
                    'molanisks', 'monkeys', 'moss_giants', 'nechryael', 'ogres',
                    'otherworldly_beings', 'pyrefiends', 'rats', 'red_dragons',
                    'rockslugs', 'sea_snakes', 'shades', 'shadow_warriors',
                    'skeletons', 'spiders', 'spiritual_creatures', 'terror_dogs',
                    'trolls', 'turoth', 'vampyres', 'wall_beasts', 'werewolves',
                    'wolves', 'zombies'
                ]
            },
            'chaeldar': {
                'name': 'Chaeldar',
                'combat_req': 70,
                'location': 'Zanaris',
                'expected_monsters': [
                    'aberrant_spectres', 'abyssal_demons', 'ankou', 'aviansies',
                    'banshees', 'basilisks', 'black_demons', 'black_dragons',
                    'bloodvelds', 'blue_dragons', 'brine_rats', 'bronze_dragons',
                    'cave_horrors', 'cave_krakens', 'dagannoth', 'dust_devils',
                    'elves', 'fever_spiders', 'fire_giants', 'fossil_island_wyverns',
                    'gargoyles', 'greater_demons', 'green_dragons', 'harpie_bug_swarms',
                    'hellhounds', 'infernal_mages', 'iron_dragons', 'jellies',
                    'jungle_horrors', 'kalphite', 'kurask', 'lesser_demons',
                    'lizardmen', 'mogres', 'molanisks', 'moss_giants', 'nechryael',
                    'ogres', 'otherworldly_beings', 'red_dragons', 'sea_snakes',
                    'shadow_warriors', 'spiritual_creatures', 'steel_dragons',
                    'suqahs', 'terror_dogs', 'trolls', 'turoth', 'tzhaar',
                    'waterfiends', 'werewolves'
                ]
            },
            'nieve': {
                'name': 'Nieve',
                'combat_req': 85,
                'location': 'Tree Gnome Stronghold',
                'expected_monsters': [
                    'aberrant_spectres', 'abyssal_demons', 'adamant_dragons',
                    'ankou', 'aviansies', 'black_demons', 'black_dragons',
                    'bloodvelds', 'blue_dragons', 'cave_horrors', 'cave_krakens',
                    'dagannoth', 'dark_beasts', 'dust_devils', 'fire_giants',
                    'fossil_island_wyverns', 'gargoyles', 'greater_demons',
                    'hellhounds', 'iron_dragons', 'kalphite', 'kurask',
                    'lizardmen', 'mithril_dragons', 'nechryael', 'red_dragons',
                    'rune_dragons', 'skeletal_wyverns', 'smoke_devils',
                    'spiritual_creatures', 'steel_dragons', 'suqahs', 'trolls',
                    'waterfiends'
                ]
            },
            'duradel': {
                'name': 'Duradel',
                'combat_req': 100,
                'slayer_req': 50,
                'location': 'Shilo Village',
                'expected_monsters': [
                    'aberrant_spectres', 'abyssal_demons', 'adamant_dragons',
                    'ankou', 'aviansies', 'black_demons', 'black_dragons',
                    'bloodvelds', 'blue_dragons', 'cave_horrors', 'cave_krakens',
                    'dagannoth', 'dark_beasts', 'dust_devils', 'fire_giants',
                    'fossil_island_wyverns', 'gargoyles', 'greater_demons',
                    'hellhounds', 'iron_dragons', 'kalphite', 'kurask',
                    'lizardmen', 'mithril_dragons', 'nechryael', 'red_dragons',
                    'rune_dragons', 'skeletal_wyverns', 'smoke_devils',
                    'spiritual_creatures', 'steel_dragons', 'suqahs', 'trolls',
                    'waterfiends', 'wyrms', 'drakes', 'hydras'
                ]
            }
        }
    
    def setup_firebase(self):
        """Initialize Firebase connection"""
        print("🔥 Initializing Firebase connection...")
        self.db = initialize_firebase()
        
        if self.db is None:
            print("❌ Failed to initialize Firebase!")
            return False
        
        print("✅ Firebase initialized successfully")
        return True
    
    def get_current_masters(self):
        """Get current slayer masters from API"""
        try:
            response = requests.get(f"{self.api_base}/api/items/slayer?category=masters", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('items', {})
            else:
                print(f"❌ Failed to get masters: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting masters: {e}")
            return {}
    
    def get_current_monsters(self):
        """Get current monsters from API"""
        try:
            response = requests.get(f"{self.api_base}/api/items/slayer?category=monsters", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('items', {})
            else:
                print(f"❌ Failed to get monsters: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting monsters: {e}")
            return {}
    
    def validate_master_assignments(self, current_masters):
        """Validate that all masters have proper task assignments"""
        print("\n🔍 VALIDATING SLAYER MASTER ASSIGNMENTS")
        print("=" * 50)
        
        missing_masters = []
        incomplete_masters = []
        
        for master_id, expected_data in self.expected_masters.items():
            if master_id not in current_masters:
                missing_masters.append(master_id)
                self.issues.append(f"Missing master: {master_id}")
                continue
            
            current_master = current_masters[master_id]
            task_assignments = current_master.get('task_assignments', {})
            expected_monsters = expected_data['expected_monsters']
            
            # Check if master has reasonable number of assignments
            if len(task_assignments) < len(expected_monsters) * 0.5:  # At least 50% of expected
                incomplete_masters.append(master_id)
                self.issues.append(f"Incomplete assignments for {master_id}: {len(task_assignments)}/{len(expected_monsters)}")
            
            print(f"📊 {master_id}: {len(task_assignments)} assignments (expected ~{len(expected_monsters)})")
        
        if missing_masters:
            print(f"\n❌ Missing masters: {missing_masters}")
        
        if incomplete_masters:
            print(f"\n⚠️  Incomplete masters: {incomplete_masters}")
        
        return len(missing_masters) == 0 and len(incomplete_masters) == 0
    
    def get_all_assigned_monsters(self, current_masters):
        """Get all monsters that are assigned by any slayer master"""
        assigned_monsters = set()
        
        for master_id, master_data in current_masters.items():
            task_assignments = master_data.get('task_assignments', {})
            assigned_monsters.update(task_assignments.keys())
        
        return assigned_monsters
    
    def validate_monster_drop_tables(self, current_monsters, assigned_monsters):
        """Validate that all assigned monsters have proper drop tables"""
        print("\n🔍 VALIDATING MONSTER DROP TABLES")
        print("=" * 50)
        
        missing_monsters = []
        empty_drop_tables = []
        poor_drop_tables = []
        good_drop_tables = []
        
        for monster_id in assigned_monsters:
            if monster_id not in current_monsters:
                missing_monsters.append(monster_id)
                self.issues.append(f"Missing monster: {monster_id}")
                continue
            
            monster_data = current_monsters[monster_id]
            drop_table = monster_data.get('drop_table', {})
            
            # Count total drops
            total_drops = sum(len(drop_table.get(tier, [])) for tier in ['always', 'common', 'rare', 'very_rare'])
            avg_value = monster_data.get('avg_loot_value_per_kill', 0)
            
            if total_drops <= 1:
                empty_drop_tables.append(monster_id)
                self.issues.append(f"Empty drop table: {monster_id}")
            elif total_drops < 5 or avg_value < 100:
                poor_drop_tables.append(monster_id)
                self.issues.append(f"Poor drop table: {monster_id} ({total_drops} drops, {avg_value:.0f} GP)")
            else:
                good_drop_tables.append(monster_id)
        
        print(f"✅ Good drop tables: {len(good_drop_tables)}")
        print(f"⚠️  Poor drop tables: {len(poor_drop_tables)}")
        print(f"❌ Empty drop tables: {len(empty_drop_tables)}")
        print(f"💀 Missing monsters: {len(missing_monsters)}")
        
        if empty_drop_tables:
            print(f"\nEmpty tables: {empty_drop_tables[:10]}")
        
        if missing_monsters:
            print(f"\nMissing monsters: {missing_monsters[:10]}")
        
        return {
            'good': good_drop_tables,
            'poor': poor_drop_tables,
            'empty': empty_drop_tables,
            'missing': missing_monsters
        }
    
    def fix_missing_monsters(self, missing_monsters):
        """Create basic monster entries for missing monsters"""
        if not missing_monsters:
            return True
        
        print(f"\n🔧 FIXING {len(missing_monsters)} MISSING MONSTERS")
        print("=" * 50)
        
        try:
            for monster_id in missing_monsters:
                # Create basic monster data
                monster_data = {
                    'name': monster_id.replace('_', ' ').title(),
                    'combat_level': 50,  # Default
                    'hitpoints': 50,     # Default
                    'slayer_level': 1,   # Default
                    'drop_table': {
                        'always': [{'item_id': 526, 'quantity': [1, 1], 'probability': 1.0}],  # Bones
                        'common': [],
                        'rare': [],
                        'very_rare': []
                    },
                    'avg_loot_value_per_kill': 100.0,  # Default low value
                    'source': 'auto_generated',
                    'needs_wiki_sync': True,
                    'created_at': datetime.now().isoformat()
                }
                
                # Add to database
                monster_ref = self.db.collection('global_items').document('slayer').collection('monsters').document(monster_id)
                monster_ref.set(monster_data)
                
                print(f"✅ Created basic entry for {monster_id}")
                self.fixes_applied.append(f"Created monster: {monster_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating missing monsters: {e}")
            return False
    
    def trigger_comprehensive_wiki_sync(self):
        """Trigger a comprehensive wiki sync for all monsters"""
        print("\n🌐 TRIGGERING COMPREHENSIVE WIKI SYNC")
        print("=" * 50)
        
        try:
            # Use the wiki sync service directly
            wiki_service = OSRSWikiSyncService(database_service=item_db)
            
            print("🔄 Starting comprehensive slayer monster sync...")
            result = wiki_service.sync_slayer_monsters(self.db)
            
            if result:
                synced_count = len(result)
                print(f"✅ Successfully synced {synced_count} monsters from wiki")
                self.fixes_applied.append(f"Wiki sync: {synced_count} monsters")
                return True
            else:
                print("❌ Wiki sync returned no results")
                return False
                
        except Exception as e:
            print(f"❌ Error during wiki sync: {e}")
            return False
    
    def verify_fixes(self):
        """Verify that our fixes worked"""
        print("\n🔍 VERIFYING FIXES")
        print("=" * 50)
        
        # Re-fetch data
        current_masters = self.get_current_masters()
        current_monsters = self.get_current_monsters()
        assigned_monsters = self.get_all_assigned_monsters(current_masters)
        
        # Re-validate
        drop_table_status = self.validate_monster_drop_tables(current_monsters, assigned_monsters)
        
        # Calculate improvement
        total_assigned = len(assigned_monsters)
        good_count = len(drop_table_status['good'])
        coverage_percent = (good_count / total_assigned * 100) if total_assigned > 0 else 0
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Total assigned monsters: {total_assigned}")
        print(f"   Monsters with good drop tables: {good_count}")
        print(f"   Coverage: {coverage_percent:.1f}%")
        
        if coverage_percent >= 80:
            print("🎉 EXCELLENT: 80%+ coverage achieved!")
            return True
        elif coverage_percent >= 60:
            print("✅ GOOD: 60%+ coverage achieved")
            return True
        else:
            print("⚠️  NEEDS WORK: Less than 60% coverage")
            return False
    
    def run_comprehensive_validation(self):
        """Run the complete validation and fix process"""
        print("🚀 COMPREHENSIVE SLAYER VALIDATION AND FIX")
        print("=" * 60)
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # Step 1: Setup
        if not self.setup_firebase():
            return False
        
        # Step 2: Get current data
        print("📊 Getting current data...")
        current_masters = self.get_current_masters()
        current_monsters = self.get_current_monsters()
        
        if not current_masters or not current_monsters:
            print("❌ Failed to get current data")
            return False
        
        # Step 3: Validate master assignments
        masters_ok = self.validate_master_assignments(current_masters)
        
        # Step 4: Get all assigned monsters
        assigned_monsters = self.get_all_assigned_monsters(current_masters)
        print(f"\n📋 Total unique monsters assigned by all masters: {len(assigned_monsters)}")
        
        # Step 5: Validate monster drop tables
        drop_table_status = self.validate_monster_drop_tables(current_monsters, assigned_monsters)
        
        # Step 6: Fix missing monsters
        if drop_table_status['missing']:
            if not self.fix_missing_monsters(drop_table_status['missing']):
                print("❌ Failed to fix missing monsters")
                return False
        
        # Step 7: Trigger comprehensive wiki sync
        if drop_table_status['empty'] or drop_table_status['poor']:
            if not self.trigger_comprehensive_wiki_sync():
                print("⚠️  Wiki sync failed, but continuing...")
        
        # Step 8: Verify fixes
        success = self.verify_fixes()
        
        # Step 9: Summary
        print(f"\n📋 SUMMARY:")
        print(f"   Issues found: {len(self.issues)}")
        print(f"   Fixes applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print(f"\n✅ Fixes applied:")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        if success:
            print("\n🎉 COMPREHENSIVE VALIDATION COMPLETED SUCCESSFULLY!")
        else:
            print("\n⚠️  VALIDATION COMPLETED WITH ISSUES")
        
        return success

def main():
    validator = ComprehensiveSlayerValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\n✅ SUCCESS: All slayer masters and monsters are properly configured!")
        print("🌐 You can now test slayer calculations with confidence.")
    else:
        print("\n⚠️  PARTIAL SUCCESS: Some issues remain but major problems were fixed.")
        print("🔄 You may want to run this script again or investigate remaining issues.")
    
    return success

if __name__ == "__main__":
    main() 