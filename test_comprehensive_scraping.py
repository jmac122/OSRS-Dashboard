#!/usr/bin/env python3
"""
Test script for comprehensive Slayer monster collection
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.database_service import ItemDatabaseService
import firebase_admin
from firebase_admin import credentials, firestore

def test_comprehensive_monster_collection():
    """Test comprehensive monster collection from all Slayer Masters"""
    print("🚀 Testing Comprehensive Monster Collection...")
    
    # Initialize Firebase
    try:
        if not firebase_admin._apps:
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
            
            if firebase_config["project_id"]:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                print("✅ Firebase connected")
            else:
                print("❌ Firebase configuration not found")
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
    
    # Test parsing a single Slayer Master first (Duradel)
    print("\n🎯 Testing Duradel task parsing...")
    
    try:
        url = "https://oldschool.runescape.wiki/w/Duradel"
        soup = wiki_service._make_request(url)
        
        if soup:
            assignable_monsters = wiki_service._parse_slayer_master_tasks(soup)
            
            print(f"✅ Found {len(assignable_monsters)} assignable monsters from Duradel:")
            
            # Show first 10 monsters
            for i, (monster_id, monster_data) in enumerate(assignable_monsters.items()):
                if i < 10:
                    print(f"  {i+1:2d}. {monster_data['name']} (Slayer: {monster_data['slayer_req']}, Weight: {monster_data['assignment_weight']})")
            
            if len(assignable_monsters) > 10:
                print(f"      ... and {len(assignable_monsters) - 10} more monsters")
        
    except Exception as e:
        print(f"❌ Error testing Duradel parsing: {e}")
    
    # Test comprehensive collection from all masters
    print("\n🌍 Testing comprehensive collection from ALL Slayer Masters...")
    
    try:
        # Only sync masters to collect monsters (don't scrape loot tables yet)
        masters = wiki_service.sync_slayer_masters(db)
        
        if hasattr(wiki_service, '_all_assignable_monsters'):
            all_monsters = wiki_service._all_assignable_monsters
            
            print(f"🎉 Successfully collected monsters from {len(masters)} Slayer Masters!")
            print(f"📊 Total unique assignable monsters: {len(all_monsters)}")
            
            # Show breakdown by Slayer requirement
            slayer_breakdown = {}
            for monster_data in all_monsters.values():
                req = monster_data['slayer_req']
                slayer_breakdown[req] = slayer_breakdown.get(req, 0) + 1
            
            print("\n📈 Breakdown by Slayer requirement:")
            for req in sorted(slayer_breakdown.keys()):
                count = slayer_breakdown[req]
                print(f"  Slayer {req:2d}+: {count:2d} monsters")
            
            # Show some examples
            print(f"\n🔍 Sample monsters collected:")
            for i, (monster_id, monster_data) in enumerate(all_monsters.items()):
                if i < 20:
                    print(f"  {i+1:2d}. {monster_data['name']} (Slayer: {monster_data['slayer_req']})")
            
            if len(all_monsters) > 20:
                print(f"      ... and {len(all_monsters) - 20} more monsters")
            
            # Estimate scraping time
            estimated_time = len(all_monsters) * 2  # 2 seconds per monster
            print(f"\n⏱️  Estimated time to scrape all loot tables: {estimated_time//60}m {estimated_time%60}s")
            
        else:
            print("❌ No monsters were collected")
    
    except Exception as e:
        print(f"❌ Error testing comprehensive collection: {e}")
    
    print("\n🎉 Comprehensive monster collection test complete!")

if __name__ == "__main__":
    test_comprehensive_monster_collection() 