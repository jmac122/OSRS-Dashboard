#!/usr/bin/env python3
"""
Simple test for Gargoyle drop table parsing
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService

def test_gargoyle_drops():
    """Test Gargoyle drop table parsing"""
    print("Testing Gargoyle drop table parsing...")
    
    wiki_service = OSRSWikiSyncService()
    
    try:
        url = "https://oldschool.runescape.wiki/w/Gargoyle"
        soup = wiki_service._make_request(url)
        
        if soup:
            print("Successfully fetched Gargoyle page")
            
            # Test the actual parsing
            drop_table = wiki_service._parse_drop_table(soup)
            
            total_drops = sum(len(drops) for drops in drop_table.values())
            print(f"Parsed {total_drops} total drops")
            
            for rarity, drops in drop_table.items():
                if drops:
                    print(f"{rarity}: {len(drops)} items")
                    for drop in drops[:5]:  # Show first 5
                        item_id = drop.get('item_id', 'UNKNOWN')
                        quantity = drop.get('quantity_range', [0,0])
                        prob = drop.get('probability', 0)
                        print(f"  - Item {item_id}: {quantity} @ {prob:.6f}")
            
            # Calculate expected value
            expected_value = wiki_service._calculate_expected_loot_value(drop_table)
            print(f"Expected loot value: {expected_value:.2f} GP per kill")
            
        else:
            print("Failed to fetch page")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gargoyle_drops() 