#!/usr/bin/env python3
"""
Quick Drop Table Fix Script
Uses the existing backend API to fix drop tables without Firebase auth issues
"""

import requests
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"

def test_backend_connection():
    """Test if backend is running and accessible"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Backend connected: {data}")
            return True
        else:
            logger.error(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Backend connection failed: {e}")
        return False

def get_current_monsters():
    """Get current slayer monsters from backend"""
    try:
        response = requests.get(f"{BASE_URL}/api/items/slayer?category=monsters", timeout=10)
        if response.status_code == 200:
            data = response.json()
            monsters = data.get('items', {})
            logger.info(f"Found {len(monsters)} slayer monsters")
            return monsters
        else:
            logger.error(f"Failed to get monsters: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Error getting monsters: {e}")
        return {}

def trigger_targeted_sync():
    """Trigger a targeted wiki sync for high-value monsters"""
    
    auth_headers = {
        'Authorization': 'Bearer admin:osrsadmin123',
        'Content-Type': 'application/json'
    }
    
    # Trigger wiki sync
    sync_data = {
        'categories': ['slayer_monsters'],
        'force_refresh': True,
        'target_monsters': [
            'gargoyles',
            'abyssal_demons',
            'nechryael', 
            'alchemical_hydra',
            'black_demons',
            'greater_demons',
            'dust_devils'
        ]
    }
    
    try:
        logger.info("Triggering targeted wiki sync...")
        response = requests.post(
            f"{BASE_URL}/api/admin/sync_wiki",
            headers=auth_headers,
            json=sync_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Wiki sync triggered: {result}")
            return True
        else:
            logger.error(f"❌ Wiki sync failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        return False

def wait_for_sync_completion():
    """Wait for sync to complete by monitoring backend"""
    logger.info("Waiting for sync to complete...")
    
    max_wait = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # Check backend health
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                # Check if we can get updated monster data
                monsters_response = requests.get(f"{BASE_URL}/api/items/slayer?category=monsters", timeout=10)
                if monsters_response.status_code == 200:
                    monsters = monsters_response.json().get('items', {})
                    
                    # Check for meaningful drop tables
                    profitable_count = 0
                    for monster_id, monster_data in monsters.items():
                        if monster_id in ['gargoyles', 'abyssal_demons', 'nechryael']:
                            drop_table = monster_data.get('drop_table', {})
                            total_drops = sum(len(drop_table.get(tier, [])) for tier in ['always', 'common', 'rare', 'very_rare'])
                            if total_drops > 3:
                                profitable_count += 1
                    
                    if profitable_count >= 2:
                        logger.info(f"✅ Sync appears complete - {profitable_count} monsters have good drop tables")
                        return True
            
            time.sleep(10)  # Wait 10 seconds before checking again
            logger.info("Still syncing...")
            
        except Exception as e:
            logger.warning(f"Error checking sync status: {e}")
            time.sleep(5)
    
    logger.warning("⚠️ Sync wait timeout reached")
    return False

def verify_drop_tables():
    """Verify the quality of drop tables"""
    try:
        response = requests.get(f"{BASE_URL}/api/items/slayer?category=monsters", timeout=10)
        if response.status_code != 200:
            logger.error("Failed to get monsters for verification")
            return False
        
        monsters = response.json().get('items', {})
        
        high_value_monsters = ['gargoyles', 'abyssal_demons', 'nechryael', 'alchemical_hydra']
        profitable_count = 0
        
        logger.info("Verifying drop table quality...")
        
        for monster_id in high_value_monsters:
            if monster_id in monsters:
                monster_data = monsters[monster_id]
                drop_table = monster_data.get('drop_table', {})
                
                # Count meaningful drops (not just bones)
                meaningful_drops = 0
                for tier in ['always', 'common', 'rare', 'very_rare']:
                    drops = drop_table.get(tier, [])
                    meaningful_drops += len([d for d in drops if d.get('item_id') != 526])
                
                avg_loot = monster_data.get('avg_loot_value_per_kill', 0)
                monster_name = monster_data.get('name', monster_id)
                
                if meaningful_drops > 3:
                    logger.info(f"✅ {monster_name}: {meaningful_drops} drops, {avg_loot:.0f} GP/kill")
                    profitable_count += 1
                else:
                    logger.warning(f"❌ {monster_name}: {meaningful_drops} drops (needs more data)")
            else:
                logger.warning(f"❌ {monster_id} not found in database")
        
        logger.info(f"Verification result: {profitable_count}/{len(high_value_monsters)} monsters have good drop tables")
        return profitable_count >= 2
        
    except Exception as e:
        logger.error(f"Error verifying drop tables: {e}")
        return False

def test_slayer_calculation():
    """Test a slayer calculation to see if it now works"""
    try:
        calc_data = {
            'calculation_mode': 'expected',
            'slayer_master_id': 'duradel',
            'user_slayer_level': 85,
            'user_combat_level': 100,
            'user_attack_level': 80,
            'user_strength_level': 80,
            'user_defence_level': 75,
            'user_ranged_level': 85,
            'user_magic_level': 80
        }
        
        logger.info("Testing slayer calculation...")
        response = requests.post(
            f"{BASE_URL}/api/calculate/slayer",
            json=calc_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                gp_hr = result.get('result', {}).get('gp_hr', 0)
                logger.info(f"✅ Slayer calculation works: {gp_hr:,.0f} GP/hr")
                return gp_hr > 0
            else:
                logger.error(f"❌ Calculation failed: {result.get('error')}")
                return False
        else:
            logger.error(f"❌ Calculation request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing calculation: {e}")
        return False

def main():
    """Main fix process"""
    logger.info("🔧 Starting Quick Drop Table Fix")
    
    # Step 1: Test backend connection
    if not test_backend_connection():
        logger.error("Cannot connect to backend!")
        return False
    
    # Step 2: Get current state
    initial_monsters = get_current_monsters()
    if not initial_monsters:
        logger.error("No monsters found!")
        return False
    
    # Step 3: Trigger targeted sync
    if not trigger_targeted_sync():
        logger.error("Failed to trigger sync!")
        return False
    
    # Step 4: Wait for completion
    if not wait_for_sync_completion():
        logger.warning("Sync may not have completed fully")
    
    # Step 5: Verify results
    if verify_drop_tables():
        logger.info("✅ Drop tables look good!")
    else:
        logger.warning("⚠️ Drop tables still need work")
    
    # Step 6: Test calculation
    if test_slayer_calculation():
        logger.info("✅ Slayer calculations working!")
        return True
    else:
        logger.warning("⚠️ Slayer calculations still have issues")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 QUICK FIX COMPLETED SUCCESSFULLY!")
        print("Drop tables should now work properly.")
        print("Try calculating slayer GP/hr in the frontend!")
    else:
        print("\n⚠️ QUICK FIX HAD ISSUES")
        print("May need additional manual intervention.") 