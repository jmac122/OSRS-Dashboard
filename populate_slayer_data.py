#!/usr/bin/env python3
"""
Simple script to populate Slayer data directly into Firestore for testing.
"""

import os
import sys
sys.path.append('osrs_gp_tracker/backend')

from datetime import datetime
from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.database_service import item_db

# Initialize Firebase (using the same setup as app.py)
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

def init_firebase():
    try:
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
        
        if firebase_config["project_id"]:
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        else:
            print("Firebase configuration not found!")
            return None
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        return None

def populate_hardcoded_data(db):
    """Populate hardcoded Slayer data for immediate testing"""
    print("🚀 Populating hardcoded Slayer data...")
    
    # Slayer Masters
    masters_data = {
        'nieve': {
            'name': 'Nieve',
            'location': 'Tree Gnome Stronghold',
            'combat_req': 85,
            'slayer_req': 0,
            'wiki_url': 'https://oldschool.runescape.wiki/w/Nieve',
            'task_assignments': {
                'gargoyles': 0.08,
                'abyssal_demons': 0.06,
                'greater_demons': 0.07,
                'black_demons': 0.06,
                'alchemical_hydra': 0.02,
                'cerberus': 0.02,
                'rune_dragons': 0.03,
                'nechryael': 0.05,
                'bloodvelds': 0.06,
                'hellhounds': 0.07,
                'cave_krakens': 0.04,
                'skeletal_wyverns': 0.03
            },
            'avg_task_quantity': {
                'gargoyles': [110, 170],
                'abyssal_demons': [130, 200],
                'alchemical_hydra': [95, 125],
                'greater_demons': [120, 185],
                'cerberus': [95, 125],
                'rune_dragons': [30, 50],
                'nechryael': [110, 170],
                'bloodvelds': [130, 200],
                'hellhounds': [120, 185],
                'cave_krakens': [100, 170],
                'skeletal_wyverns': [40, 80]
            },
            'last_synced': datetime.now().isoformat()
        },
        'duradel': {
            'name': 'Duradel',
            'location': 'Shilo Village',
            'combat_req': 100,
            'slayer_req': 50,
            'wiki_url': 'https://oldschool.runescape.wiki/w/Duradel',
            'task_assignments': {
                'gargoyles': 0.09,
                'abyssal_demons': 0.07,
                'greater_demons': 0.08,
                'black_demons': 0.07,
                'alchemical_hydra': 0.03,
                'cerberus': 0.03,
                'rune_dragons': 0.04,
                'nechryael': 0.06,
                'bloodvelds': 0.07,
                'hellhounds': 0.08,
                'cave_krakens': 0.05,
                'skeletal_wyverns': 0.04
            },
            'avg_task_quantity': {
                'gargoyles': [120, 185],
                'abyssal_demons': [140, 220],
                'alchemical_hydra': [95, 125],
                'greater_demons': [130, 200],
                'cerberus': [95, 125],
                'rune_dragons': [40, 60],
                'nechryael': [120, 185],
                'bloodvelds': [140, 220],
                'hellhounds': [130, 200],
                'cave_krakens': [110, 185],
                'skeletal_wyverns': [50, 90]
            },
            'last_synced': datetime.now().isoformat()
        }
    }
    
    # Monsters data
    monsters_data = {
        'gargoyles': {
            'name': 'Gargoyles',
            'wiki_slug': 'gargoyles',
            'slayer_level_req': 75,
            'combat_level': 111,
            'monster_hp': 105,
            'avg_kill_time_seconds_base': 15,
            'base_kph_range': [350, 400],
            'common_supply_cost_per_hour_base': 30000,
            'weakness': 'Crush',
            'required_items': [1596],  # Rock hammer
            'notes': 'Requires rock hammer to finish. High alchables.',
            'drop_table': {
                'always': [
                    {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}  # Bones
                ],
                'common': [
                    {'item_id': 995, 'quantity_range': [50, 150], 'probability': 0.25},    # Coins
                    {'item_id': 1149, 'quantity_range': [1, 1], 'probability': 0.15},     # Rune full helm
                    {'item_id': 1201, 'quantity_range': [1, 1], 'probability': 0.12}      # Rune kiteshield
                ],
                'rare': [
                    {'item_id': 1631, 'quantity_range': [1, 1], 'probability': 1/512}     # Granite maul
                ],
                'very_rare': []
            },
            'wiki_url': 'https://oldschool.runescape.wiki/w/Gargoyle',
            'last_synced': datetime.now().isoformat()
        },
        'abyssal_demons': {
            'name': 'Abyssal demons',
            'wiki_slug': 'abyssal_demons',
            'slayer_level_req': 85,
            'combat_level': 124,
            'monster_hp': 150,
            'avg_kill_time_seconds_base': 12,
            'base_kph_range': [400, 450],
            'common_supply_cost_per_hour_base': 40000,
            'weakness': 'Slash',
            'notes': 'Fast task with valuable whip drops.',
            'drop_table': {
                'always': [
                    {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}        # Bones
                ],
                'common': [
                    {'item_id': 995, 'quantity_range': [100, 300], 'probability': 0.2}    # Coins
                ],
                'rare': [
                    {'item_id': 4151, 'quantity_range': [1, 1], 'probability': 1/512}     # Abyssal whip
                ],
                'very_rare': []
            },
            'wiki_url': 'https://oldschool.runescape.wiki/w/Abyssal_demon',
            'last_synced': datetime.now().isoformat()
        },
        'alchemical_hydra': {
            'name': 'Alchemical Hydra',
            'wiki_slug': 'alchemical_hydra',
            'slayer_level_req': 95,
            'combat_level': 426,
            'monster_hp': 300,
            'avg_kill_time_seconds_base': 120,
            'base_kph_range': [25, 30],
            'common_supply_cost_per_hour_base': 120000,
            'weakness': 'Ranged',
            'required_items': [22114],  # Brimstone ring
            'notes': 'Requires 95 Slayer. Multiple phases with prayer switches.',
            'drop_table': {
                'always': [
                    {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}        # Bones
                ],
                'common': [
                    {'item_id': 995, 'quantity_range': [1000, 3000], 'probability': 0.2}, # Coins
                    {'item_id': 22100, 'quantity_range': [1, 1], 'probability': 0.04}     # Hydra leather
                ],
                'rare': [
                    {'item_id': 22109, 'quantity_range': [1, 1], 'probability': 0.002},   # Hydra claw (1/500)
                    {'item_id': 22103, 'quantity_range': [1, 1], 'probability': 0.002}    # Hydra tail (1/500)
                ],
                'very_rare': []
            },
            'wiki_url': 'https://oldschool.runescape.wiki/w/Alchemical_Hydra',
            'last_synced': datetime.now().isoformat()
        }
    }
    
    # Save masters
    for master_id, master_data in masters_data.items():
        try:
            item_db.add_global_item(db, 'slayer', 'masters', master_id, master_data)
            print(f"✅ Added master: {master_data['name']}")
        except Exception as e:
            print(f"❌ Error adding master {master_id}: {e}")
    
    # Save monsters
    for monster_id, monster_data in monsters_data.items():
        try:
            item_db.add_global_item(db, 'slayer', 'monsters', monster_id, monster_data)
            print(f"✅ Added monster: {monster_data['name']}")
        except Exception as e:
            print(f"❌ Error adding monster {monster_id}: {e}")
    
    print(f"🎉 Data population complete! Added {len(masters_data)} masters and {len(monsters_data)} monsters")

def main():
    print("🔥 OSRS Slayer Data Population Script")
    print("=" * 50)
    
    # Initialize Firebase
    db = init_firebase()
    if not db:
        print("Failed to initialize Firebase. Exiting.")
        return
    
    print("✅ Firebase initialized successfully")
    
    # Populate data
    populate_hardcoded_data(db)
    
    print("\n🚀 Ready to test! You can now:")
    print("1. Test the Slayer calculation endpoint")
    print("2. Update the frontend to use the new Slayer Master selection")

if __name__ == "__main__":
    main() 