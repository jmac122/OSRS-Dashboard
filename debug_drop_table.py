#!/usr/bin/env python3
"""
Debug script to examine actual HTML structure of monster drop tables
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.osrs_wiki_sync_service import OSRSWikiSyncService

def debug_drop_table_parsing():
    """Debug drop table parsing for a specific monster"""
    print("🔍 Debugging Drop Table Parsing...")
    
    wiki_service = OSRSWikiSyncService()
    
    # Test with Gargoyles (known to have detailed drop table)
    print("\n🎯 Testing Gargoyle drop table structure...")
    
    try:
        url = "https://oldschool.runescape.wiki/w/Gargoyle"
        soup = wiki_service._make_request(url)
        
        if soup:
            print("✅ Successfully fetched Gargoyle page")
            
            # Look for all tables on the page
            all_tables = soup.find_all('table')
            print(f"📊 Found {len(all_tables)} total tables on page")
            
            # Check for tables with drop-related class names
            drop_tables = soup.find_all(['table', 'div'], class_=lambda x: x and ('droptable' in x.lower() if x else False))
            print(f"🎲 Found {len(drop_tables)} tables with 'droptable' in class")
            
            # Check all wikitables
            wiki_tables = soup.find_all('table', class_='wikitable')
            print(f"📋 Found {len(wiki_tables)} wikitables")
            
            # Examine the first few wikitables to see structure
            for i, table in enumerate(wiki_tables[:3]):
                print(f"\n📋 WikiTable {i+1}:")
                
                # Get table headers
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
                    print(f"   Headers: {headers}")
                    
                    # Check if this looks like a drop table
                    header_text = ' '.join(headers).lower()
                    is_drop_table = any(keyword in header_text for keyword in ['item', 'quantity', 'rarity', 'drop'])
                    print(f"   Looks like drop table: {is_drop_table}")
                    
                    if is_drop_table:
                        # Show first few rows
                        rows = table.find_all('tr')[1:4]  # Skip header, show next 3
                        for j, row in enumerate(rows):
                            cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                            print(f"   Row {j+1}: {cells}")
            
            # Test the actual parsing
            print(f"\n🔧 Testing actual drop table parsing...")
            drop_table = wiki_service._parse_drop_table(soup)
            
            total_drops = sum(len(drops) for drops in drop_table.values())
            print(f"📊 Parsed {total_drops} total drops")
            
            for rarity, drops in drop_table.items():
                if drops:
                    print(f"   {rarity}: {len(drops)} items")
                    for drop in drops[:3]:  # Show first 3
                        print(f"     - Item {drop.get('item_id', 'UNKNOWN')}: {drop.get('quantity_range', [0,0])} @ {drop.get('probability', 0):.4f}")
            
            # Calculate expected value
            expected_value = wiki_service._calculate_expected_loot_value(drop_table)
            print(f"\n💰 Expected loot value: {expected_value:.2f} GP per kill")
            
        else:
            print("❌ Failed to fetch page")
            
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🎉 Drop table debugging complete!")

if __name__ == "__main__":
    debug_drop_table_parsing() 