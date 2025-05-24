#!/usr/bin/env python3
"""
Run comprehensive Slayer sync - scrapes ALL monster loot tables from ALL Slayer Masters
"""

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.database_service import ItemDatabaseService
import firebase_admin
from firebase_admin import credentials, firestore

def run_comprehensive_sync():
    """Run the full comprehensive Slayer sync"""
    print("🚀 Starting COMPREHENSIVE Slayer Sync...")
    print("📋 This will scrape loot tables for ALL monsters from ALL Slayer Masters")
    print("⏱️  Estimated time: 5-15 minutes depending on number of monsters found")
    print("=" * 70)
    
    start_time = time.time()
    
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
                print("✅ Firebase connected successfully")
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
    print("🔧 Initializing services...")
    db_service = ItemDatabaseService()
    wiki_service = OSRSWikiSyncService(database_service=db_service)
    
    try:
        print("\n" + "=" * 70)
        print("🎯 PHASE 1: Analyzing Slayer Masters and collecting assignable monsters...")
        print("=" * 70)
        
        # Run the comprehensive sync
        result = wiki_service.sync_slayer_data(db)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("🎉 COMPREHENSIVE SYNC COMPLETE!")
        print("=" * 70)
        
        if result.get('success'):
            print(f"✅ Status: SUCCESS")
            print(f"📋 Slayer Masters synced: {len(result.get('masters', {}))}")
            print(f"👹 Monsters with loot tables: {len(result.get('monsters', {}))}")
            print(f"🎯 Total assignable monsters found: {result.get('total_assignable_monsters', 0)}")
            print(f"⏱️  Total time: {duration//60:.0f}m {duration%60:.0f}s")
            
            # Show some examples of what was scraped
            monsters = result.get('monsters', {})
            if monsters:
                print(f"\n🔍 Sample monsters with scraped loot tables:")
                for i, (monster_id, monster_data) in enumerate(monsters.items()):
                    if i < 10:
                        name = monster_data.get('name', monster_id)
                        gp_per_kill = monster_data.get('avg_loot_value_per_kill', 0)
                        kph = monster_data.get('kills_per_hour', 0)
                        slayer_req = monster_data.get('slayer_level_req', 1)
                        
                        total_drops = 0
                        drop_table = monster_data.get('drop_table', {})
                        for rarity in ['always', 'common', 'rare', 'very_rare']:
                            total_drops += len(drop_table.get(rarity, []))
                        
                        print(f"  {i+1:2d}. {name}")
                        print(f"      Slayer: {slayer_req}, GP/kill: {gp_per_kill:.1f}, KPH: {kph}, Drops: {total_drops}")
                
                if len(monsters) > 10:
                    print(f"      ... and {len(monsters) - 10} more monsters with full loot data")
            
            print(f"\n💾 All data has been saved to Firebase!")
            print(f"🌐 Frontend should now have comprehensive Slayer data")
            
        else:
            print(f"❌ Status: FAILED")
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            if result.get('fallback_used'):
                print(f"⚠️  Fallback data was used instead")
                print(f"📋 Masters (fallback): {len(result.get('masters', {}))}")
                print(f"👹 Monsters (fallback): {len(result.get('monsters', {}))}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Sync interrupted by user")
        print(f"⏱️  Time elapsed: {(time.time() - start_time)//60:.0f}m {(time.time() - start_time)%60:.0f}s")
    except Exception as e:
        print(f"\n💥 Sync failed with error: {e}")
        print(f"⏱️  Time elapsed: {(time.time() - start_time)//60:.0f}m {(time.time() - start_time)%60:.0f}s")
    
    print("\n" + "=" * 70)
    print("✨ Comprehensive Slayer sync session complete!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_comprehensive_sync()
    except KeyboardInterrupt:
        print("\n👋 Sync cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}") 