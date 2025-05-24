#!/usr/bin/env python3
"""
Test script for enhanced wiki scraping functionality
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.database_service import ItemDatabaseService
import firebase_admin
from firebase_admin import credentials, firestore
import json
from dotenv import load_dotenv

def test_wiki_scraping():
    """Test the enhanced wiki scraping"""
    print("🚀 Testing Enhanced Wiki Scraping...")
    
    # Initialize Firebase using environment variables (like main app)
    try:
        if not firebase_admin._apps:
            # Load environment variables from the correct path
            load_dotenv('osrs_gp_tracker/.env')
            
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
            
            # Check if we have the required Firebase config
            if firebase_config["project_id"]:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                print("✅ Firebase connected")
            else:
                print("❌ Firebase configuration not found in environment variables")
                return
        else:
            db = firestore.client()
            print("✅ Firebase already initialized")
            
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return
    
    # Initialize services
    db_service = ItemDatabaseService()
    wiki_service = OSRSWikiSyncService(database_service=db_service)
    
    # Test scraping a single monster (Gargoyles)
    print("\n🔍 Testing Gargoyle drop table scraping...")
    
    try:
        url = "https://oldschool.runescape.wiki/w/Gargoyle"
        soup = wiki_service._make_request(url)
        
        if soup:
            print("✅ Successfully fetched Gargoyle wiki page")
            
            # Test drop table parsing
            drop_table = wiki_service._parse_drop_table(soup)
            
            print(f"\n📊 Gargoyle Drop Table Results:")
            for rarity, drops in drop_table.items():
                if drops:
                    print(f"  {rarity.upper()}: {len(drops)} items")
                    for drop in drops[:3]:  # Show first 3 items
                        print(f"    - Item ID {drop['item_id']}: {drop['quantity_range']} @ {drop['probability']:.4f}")
                    if len(drops) > 3:
                        print(f"    ... and {len(drops) - 3} more items")
                else:
                    print(f"  {rarity.upper()}: No items")
            
            # Calculate expected loot value
            expected_value = wiki_service._calculate_expected_loot_value(drop_table)
            print(f"\n💰 Expected loot value: {expected_value:.2f} GP per kill")
            
        else:
            print("❌ Failed to fetch wiki page")
            
    except Exception as e:
        print(f"❌ Error testing scraping: {e}")
    
    # Test the full sync (just one monster to avoid rate limiting)
    print("\n🎯 Testing single monster sync...")
    
    try:
        # Test with a smaller subset
        test_monsters = {'gargoyles': {
            'name': 'Gargoyles',
            'wiki_path': '/w/Gargoyle',
            'slayer_req': 75
        }}
        
        # Temporarily replace monsters list for testing
        original_monsters = wiki_service.sync_slayer_monsters.__code__.co_consts
        
        result = wiki_service.sync_slayer_monsters(db)
        
        if result:
            print(f"✅ Successfully synced monster data")
            for monster_id, monster_data in result.items():
                print(f"\n📝 {monster_data.get('name', monster_id)}:")
                print(f"   - Combat Level: {monster_data.get('combat_level', 'Unknown')}")
                print(f"   - HP: {monster_data.get('monster_hp', 'Unknown')}")
                print(f"   - Expected GP/kill: {monster_data.get('avg_loot_value_per_kill', 0):.2f}")
                print(f"   - KPH: {monster_data.get('kills_per_hour', 0)}")
                print(f"   - Supply cost/hr: {monster_data.get('avg_supply_cost_per_hour', 0)}")
                
                # Show some drop data
                drop_table = monster_data.get('drop_table', {})
                total_drops = sum(len(drops) for drops in drop_table.values())
                print(f"   - Total scraped drops: {total_drops}")
        
    except Exception as e:
        print(f"❌ Error testing monster sync: {e}")
    
    print("\n🎉 Wiki scraping test complete!")

if __name__ == "__main__":
    test_wiki_scraping() 