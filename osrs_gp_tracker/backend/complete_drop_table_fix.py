#!/usr/bin/env python3
"""
Complete Drop Table Fix
Fixes empty/incomplete drop tables for all monsters using wiki sync
"""

import sys
import os
import logging
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

# Import our centralized Firebase initialization
from utils.firebase_init import initialize_firebase
from utils.comprehensive_item_database import OSRSItemDatabase
from utils.osrs_wiki_sync_service import OSRSWikiSyncService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_firebase():
    """Initialize Firebase using our centralized utility"""
    logger.info("Initializing Firebase connection...")
    db = initialize_firebase()
    
    if db is None:
        logger.error("Failed to initialize Firebase! Cannot proceed.")
        return None
    
    logger.info("✅ Firebase initialized successfully")
    return db

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
    from utils.comprehensive_item_database import item_database
    
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
    from utils.database_service import item_db
    import time
    
    logger.info("Re-syncing high-value monsters using wiki sync service...")
    
    try:
        # Use the wiki sync service to sync all slayer monsters
        wiki_service = OSRSWikiSyncService(item_db)
        
        logger.info("Running comprehensive slayer monster sync...")
        sync_results = wiki_service.sync_slayer_monsters(db)
        
        if sync_results:
            logger.info(f"✅ Successfully synced {len(sync_results)} monsters")
            
            # Check specific high-value monsters
            priority_monsters = [
                'gargoyles', 'abyssal_demons', 'nechryael', 'alchemical_hydra',
                'black_demons', 'greater_demons', 'dust_devils', 'kurask',
                'bloodvelds', 'cave_horrors'
            ]
            
            for monster_id in priority_monsters:
                if monster_id in sync_results:
                    monster_data = sync_results[monster_id]
                    drop_table = monster_data.get('drop_table', {})
                    total_drops = sum(len(drop_table.get(tier, [])) for tier in ['always', 'common', 'rare', 'very_rare'])
                    avg_value = monster_data.get('avg_loot_value_per_kill', 0)
                    logger.info(f"   {monster_id}: {total_drops} drops, {avg_value:.0f} GP/kill")
                else:
                    logger.warning(f"   {monster_id}: Not found in sync results")
        else:
            logger.error("❌ Wiki sync returned no results")
            
    except Exception as e:
        logger.error(f"Error during wiki sync: {e}")
        logger.info("Attempting fallback approach...")
        
        # Fallback: trigger the admin API sync endpoint
        try:
            import requests
            response = requests.post("http://localhost:5000/api/admin/sync_wiki", 
                                   json={"sync_type": "slayer"}, 
                                   timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("✅ Successfully triggered wiki sync via API")
                else:
                    logger.error(f"API sync failed: {result.get('error')}")
            else:
                logger.error(f"API sync request failed: {response.status_code}")
                
        except Exception as api_error:
            logger.error(f"Fallback API sync also failed: {api_error}")
    
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
    db = setup_firebase()
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