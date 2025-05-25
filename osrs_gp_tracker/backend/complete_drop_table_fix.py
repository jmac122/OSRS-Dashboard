#!/usr/bin/env python3
"""
Complete Drop Table Fix Script
Cleans up and re-populates all slayer monster drop tables with proper item data
"""

import os
import sys
import logging
import time
from datetime import datetime

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.database_service import item_db
from utils.osrs_wiki_sync_service import OSRSWikiSyncService
from utils.comprehensive_item_database import item_database
import firebase_admin
from firebase_admin import credentials, firestore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drop_table_fix.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Try to get existing app
        app = firebase_admin.get_app()
        logger.info("Using existing Firebase app")
        return firestore.client(app)
    except ValueError:
        # No app exists, create one
        try:
            # Use service account key if available
            cred_path = os.path.join(current_dir, 'firebase-service-account.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                app = firebase_admin.initialize_app(cred)
                logger.info("Initialized Firebase with service account")
            else:
                # Use default credentials (e.g., from environment)
                app = firebase_admin.initialize_app()
                logger.info("Initialized Firebase with default credentials")
            
            return firestore.client(app)
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return None

def get_current_monsters(db):
    """Get all current slayer monsters from database"""
    try:
        monsters_ref = db.collection('global_items').document('slayer').collection('monsters')
        docs = monsters_ref.stream()
        
        monsters = {}
        for doc in docs:
            data = doc.to_dict()
            monsters[doc.id] = data
            
        logger.info(f"Found {len(monsters)} slayer monsters in database")
        return monsters
        
    except Exception as e:
        logger.error(f"Error getting current monsters: {e}")
        return {}

def clear_empty_drop_tables(db, monsters):
    """Clear monsters with empty or minimal drop tables"""
    cleared_count = 0
    
    for monster_id, monster_data in monsters.items():
        drop_table = monster_data.get('drop_table', {})
        
        # Check if drop table is effectively empty
        total_drops = 0
        for tier in ['always', 'common', 'rare', 'very_rare']:
            drops = drop_table.get(tier, [])
            # Only count drops that aren't just bones
            valuable_drops = [d for d in drops if d.get('item_id') != 526]
            total_drops += len(valuable_drops)
        
        if total_drops <= 1:  # Only bones or empty
            logger.info(f"Clearing empty drop table for {monster_data.get('name', monster_id)}")
            
            # Clear the drop table
            monster_ref = db.collection('global_items').document('slayer').collection('monsters').document(monster_id)
            monster_ref.update({
                'drop_table': {
                    'always': [],
                    'common': [],
                    'rare': [],
                    'very_rare': []
                },
                'avg_loot_value_per_kill': 60.0,  # Reset to default
                'last_synced': datetime.now().isoformat(),
                'needs_resync': True
            })
            cleared_count += 1
    
    logger.info(f"Cleared {cleared_count} empty drop tables")

def test_item_database():
    """Test the comprehensive item database with known problematic items"""
    test_items = [
        'limpwurt seed',
        'strawberry seed', 
        'watermelon seed',
        'potato cactus seed',
        'cactus seed',
        'marrentill seed',
        'harralander seed',
        'granite maul',
        'abyssal whip',
        'rune boots',
        'death rune',
        'nature rune',
        'coins'
    ]
    
    logger.info("Testing comprehensive item database...")
    success_count = 0
    
    for item_name in test_items:
        item_id = item_database.get_item_id(item_name)
        if item_id:
            logger.info(f"✅ {item_name}: {item_id}")
            success_count += 1
        else:
            logger.error(f"❌ {item_name}: NOT FOUND")
    
    logger.info(f"Item database test: {success_count}/{len(test_items)} items found")
    return success_count == len(test_items)

def resync_high_value_monsters(db):
    """Re-sync specific high-value monsters that should be profitable"""
    
    priority_monsters = [
        'gargoyles',
        'abyssal_demons', 
        'nechryael',
        'alchemical_hydra',
        'black_demons',
        'greater_demons',
        'dust_devils',
        'kurask',
        'bloodvelds',
        'cave_horrors'
    ]
    
    wiki_service = OSRSWikiSyncService(item_db)
    
    logger.info(f"Re-syncing {len(priority_monsters)} high-value monsters...")
    
    for monster_id in priority_monsters:
        try:
            logger.info(f"Syncing {monster_id}...")
            
            # Construct wiki URL
            wiki_url = f"https://oldschool.runescape.wiki/w/{monster_id.replace('_', ' ').title()}"
            
            # Try to sync the monster
            monster_data = wiki_service.extract_monster_data(wiki_url, monster_id)
            
            if monster_data:
                # Save to database
                monster_ref = db.collection('global_items').document('slayer').collection('monsters').document(monster_id)
                monster_data['updated_at'] = datetime.now()
                monster_data['last_synced'] = datetime.now().isoformat()
                monster_data['source'] = 'wiki_resync'
                
                monster_ref.set(monster_data, merge=True)
                logger.info(f"✅ Successfully synced {monster_id}")
                
                # Check drop table quality
                drop_table = monster_data.get('drop_table', {})
                total_drops = sum(len(drop_table.get(tier, [])) for tier in ['always', 'common', 'rare', 'very_rare'])
                logger.info(f"   Drop table has {total_drops} total drops")
                
            else:
                logger.warning(f"❌ Failed to sync {monster_id}")
            
            # Small delay to be respectful
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error syncing {monster_id}: {e}")
    
    logger.info("High-value monster re-sync complete")

def verify_drop_tables(db):
    """Verify that drop tables now have proper data"""
    try:
        monsters_ref = db.collection('global_items').document('slayer').collection('monsters')
        docs = monsters_ref.stream()
        
        profitable_count = 0
        empty_count = 0
        
        for doc in docs:
            data = doc.to_dict()
            monster_name = data.get('name', doc.id)
            
            drop_table = data.get('drop_table', {})
            total_drops = sum(len(drop_table.get(tier, [])) for tier in ['always', 'common', 'rare', 'very_rare'])
            avg_loot = data.get('avg_loot_value_per_kill', 0)
            
            if total_drops > 3 and avg_loot > 1000:  # Has meaningful drops
                profitable_count += 1
                logger.info(f"✅ {monster_name}: {total_drops} drops, {avg_loot:.0f} GP/kill")
            elif total_drops <= 1:
                empty_count += 1
                logger.warning(f"❌ {monster_name}: {total_drops} drops (still empty)")
            else:
                logger.info(f"⚠️  {monster_name}: {total_drops} drops, {avg_loot:.0f} GP/kill")
        
        logger.info(f"Verification complete: {profitable_count} profitable monsters, {empty_count} still empty")
        return profitable_count, empty_count
        
    except Exception as e:
        logger.error(f"Error verifying drop tables: {e}")
        return 0, 0

def main():
    """Main fix process"""
    logger.info("🔧 Starting Complete Drop Table Fix Process")
    
    # Step 1: Test item database
    logger.info("Step 1: Testing comprehensive item database...")
    if not test_item_database():
        logger.error("Item database test failed! Cannot proceed.")
        return False
    
    # Step 2: Initialize Firebase
    logger.info("Step 2: Initializing Firebase connection...")
    db = initialize_firebase()
    if not db:
        logger.error("Failed to initialize Firebase! Cannot proceed.")
        return False
    
    # Step 3: Get current monsters
    logger.info("Step 3: Getting current monsters from database...")
    current_monsters = get_current_monsters(db)
    if not current_monsters:
        logger.error("No monsters found in database!")
        return False
    
    # Step 4: Clear empty drop tables
    logger.info("Step 4: Clearing empty drop tables...")
    clear_empty_drop_tables(db, current_monsters)
    
    # Step 5: Re-sync high-value monsters
    logger.info("Step 5: Re-syncing high-value monsters...")
    resync_high_value_monsters(db)
    
    # Step 6: Verify results
    logger.info("Step 6: Verifying drop table quality...")
    profitable_count, empty_count = verify_drop_tables(db)
    
    # Final report
    logger.info("🎉 Drop Table Fix Process Complete!")
    logger.info(f"   - {profitable_count} monsters with good drop tables")
    logger.info(f"   - {empty_count} monsters still need work")
    
    if profitable_count >= 5:
        logger.info("✅ SUCCESS: Sufficient profitable monsters available")
        return True
    else:
        logger.warning("⚠️  PARTIAL: More work needed on drop tables")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 DROP TABLE FIX COMPLETED SUCCESSFULLY!")
        print("You can now test slayer calculations - they should show positive GP/hr values.")
    else:
        print("\n⚠️  DROP TABLE FIX COMPLETED WITH ISSUES")
        print("Some monsters may still have incomplete drop tables.") 