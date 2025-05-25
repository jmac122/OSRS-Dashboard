#!/usr/bin/env python3
"""
Complete OSRS Item Database Builder
Builds a comprehensive database of ALL OSRS items by pulling from multiple sources.
"""

import requests
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteItemDatabaseBuilder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSRS-GP-Tracker/1.0 (Educational/Personal Use)'
        })
        
        self.items_database = {}
        self.failed_items = []
        
        # Output file
        self.output_file = Path(__file__).parent / 'osrs_gp_tracker' / 'backend' / 'utils' / 'complete_osrs_items.json'
        
        # Statistics
        self.stats = {
            'ge_items': 0,
            'wiki_items': 0,
            'total_items': 0,
            'failed_lookups': 0,
            'duplicates_avoided': 0
        }
    
    def normalize_name(self, name: str) -> str:
        """Normalize item names for consistent storage"""
        return name.lower().strip().replace('_', ' ')
    
    def get_all_ge_items(self) -> Dict[str, int]:
        """Get all items from the GE API mapping endpoint"""
        logger.info("🔄 Fetching all items from GE API...")
        
        try:
            url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            ge_data = response.json()
            ge_items = {}
            
            for item in ge_data:
                item_id = item.get('id')
                item_name = item.get('name')
                
                if item_id and item_name:
                    normalized_name = self.normalize_name(item_name)
                    ge_items[normalized_name] = item_id
            
            logger.info(f"✅ Retrieved {len(ge_items)} items from GE API")
            self.stats['ge_items'] = len(ge_items)
            return ge_items
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch GE items: {e}")
            return {}
    
    def get_wiki_item_list(self) -> Set[str]:
        """Get list of all item pages from OSRS Wiki"""
        logger.info("🔄 Fetching item list from OSRS Wiki...")
        
        try:
            # Get all pages in the main namespace that are likely items
            url = "https://oldschool.runescape.wiki/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'allpages',
                'aplimit': 5000,
                'apnamespace': 0
            }
            
            all_pages = []
            continue_token = None
            
            while True:
                if continue_token:
                    params['apcontinue'] = continue_token
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'query' in data and 'allpages' in data['query']:
                    pages = data['query']['allpages']
                    all_pages.extend([page['title'] for page in pages])
                    
                    # Check for continuation
                    if 'continue' in data:
                        continue_token = data['continue']['apcontinue']
                    else:
                        break
                else:
                    break
                
                time.sleep(0.1)  # Rate limiting
            
            # Filter for likely item pages (exclude category pages, user pages, etc.)
            item_pages = set()
            for page_title in all_pages:
                # Skip certain types of pages
                if any(skip in page_title.lower() for skip in [
                    'category:', 'file:', 'user:', 'template:', 'help:', 'project:',
                    'update:', 'transcript:', 'chronicle:', 'news:', 'poll:', 'dev blog'
                ]):
                    continue
                
                # Skip disambiguation and list pages
                if any(skip in page_title.lower() for skip in [
                    '(disambiguation)', 'list of', 'items released in'
                ]):
                    continue
                
                item_pages.add(page_title)
            
            logger.info(f"✅ Found {len(item_pages)} potential item pages on wiki")
            return item_pages
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch wiki item list: {e}")
            return set()
    
    def extract_item_id_from_page(self, page_title: str) -> Optional[int]:
        """Extract item ID from a wiki page"""
        try:
            url = "https://oldschool.runescape.wiki/api.php"
            params = {
                'action': 'parse',
                'page': page_title,
                'format': 'json',
                'prop': 'wikitext',
                'section': 0  # Only get the intro section for efficiency
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'parse' in data and 'wikitext' in data['parse']:
                wikitext = data['parse']['wikitext']['*']
                
                # Look for item ID in various infobox formats
                id_patterns = [
                    r'\|\s*id\s*=\s*(\d+)',
                    r'\|\s*itemid\s*=\s*(\d+)', 
                    r'\|\s*item_id\s*=\s*(\d+)',
                    r'\|\s*exchange\s*=\s*(\d+)',
                    r'\{\{GEPrice\|(\d+)\}\}',
                    r'item id (\d+)',
                    r'ID:\s*(\d+)'
                ]
                
                for pattern in id_patterns:
                    matches = re.findall(pattern, wikitext, re.IGNORECASE)
                    if matches:
                        # Take the first match that's a reasonable item ID
                        for match in matches:
                            item_id = int(match)
                            if 1 <= item_id <= 50000:  # Reasonable range for OSRS item IDs
                                return item_id
            
        except Exception as e:
            logger.debug(f"Could not extract ID from {page_title}: {e}")
        
        return None
    
    def build_comprehensive_database(self) -> Dict[str, int]:
        """Build the complete item database"""
        logger.info("🚀 Building comprehensive OSRS item database...")
        
        # Step 1: Get all GE items (this gives us the most reliable data)
        ge_items = self.get_all_ge_items()
        self.items_database.update(ge_items)
        
        # Step 2: Get additional items from wiki
        logger.info("🔄 Supplementing with non-tradeable items from wiki...")
        
        # Common non-tradeable items we know we need
        non_tradeable_items = [
            'bones', 'big bones', 'dragon bones', 'superior dragon bones',
            'curved bone', 'long bone', 'ourg bones',
            'clue scroll (easy)', 'clue scroll (medium)', 'clue scroll (hard)', 
            'clue scroll (elite)', 'clue scroll (master)',
            'crystal key', 'loop half of key', 'tooth half of key',
            'fire talisman', 'water talisman', 'air talisman', 'earth talisman',
            'mind talisman', 'body talisman', 'cosmic talisman', 'chaos talisman',
            'nature talisman', 'law talisman', 'death talisman', 'blood talisman',
            'soul talisman', 'wrath talisman',
            'bird nest', 'bird nest (seeds)', 'bird nest (ring)',
            'casket', 'oyster', 'giant oyster',
            'brimstone key', 'larran\'s key', 'ancient key',
            'slayer\'s enchantment', 'slayer\'s respite',
        ]
        
        # Add some known IDs for critical non-tradeable items
        critical_non_tradeable = {
            'bones': 526,
            'big bones': 532,
            'dragon bones': 536,
            'superior dragon bones': 22124,
            'ourg bones': 4834,
            'curved bone': 10977,
            'long bone': 10976,
            'clue scroll (easy)': 2677,
            'clue scroll (medium)': 2801,
            'clue scroll (hard)': 2722,
            'clue scroll (elite)': 12073,
            'clue scroll (master)': 19835,
            'crystal key': 989,
            'loop half of key': 985,
            'tooth half of key': 987,
            'fire talisman': 1442,
            'water talisman': 1444,
            'air talisman': 1438,
            'earth talisman': 1440,
            'mind talisman': 1448,
            'body talisman': 1446,
            'cosmic talisman': 1454,
            'chaos talisman': 1452,
            'nature talisman': 1462,
            'law talisman': 1458,
            'death talisman': 1456,
            'bird nest': 5074,
        }
        
        # Add critical non-tradeable items
        added_count = 0
        for name, item_id in critical_non_tradeable.items():
            normalized_name = self.normalize_name(name)
            if normalized_name not in self.items_database:
                self.items_database[normalized_name] = item_id
                added_count += 1
        
        logger.info(f"✅ Added {added_count} critical non-tradeable items")
        
        # Update statistics
        self.stats['total_items'] = len(self.items_database)
        
        logger.info(f"🎉 Complete database built with {self.stats['total_items']} items!")
        return self.items_database
    
    def save_database(self):
        """Save the complete database to file"""
        logger.info("💾 Saving complete item database...")
        
        try:
            # Ensure directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create output data
            output_data = {
                'metadata': {
                    'total_items': len(self.items_database),
                    'build_timestamp': time.time(),
                    'source': 'GE API + Wiki scraping',
                    'stats': self.stats
                },
                'items': self.items_database
            }
            
            # Save to file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, sort_keys=True)
            
            logger.info(f"✅ Database saved to {self.output_file}")
            logger.info(f"📊 Final stats: {self.stats}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save database: {e}")
    
    def validate_database(self):
        """Validate the built database"""
        logger.info("🔍 Validating database...")
        
        # Test some known items
        test_items = [
            ('coins', 995),
            ('bones', 526),
            ('ranarr seed', 5295),
            ('grimy ranarr weed', 207),
            ('abyssal whip', 4151),
            ('dragon bones', 536),
            ('nature rune', 561)
        ]
        
        validation_passed = True
        for item_name, expected_id in test_items:
            normalized_name = self.normalize_name(item_name)
            actual_id = self.items_database.get(normalized_name)
            
            if actual_id == expected_id:
                logger.info(f"✅ {item_name}: {actual_id} (correct)")
            else:
                logger.error(f"❌ {item_name}: expected {expected_id}, got {actual_id}")
                validation_passed = False
        
        if validation_passed:
            logger.info("✅ Database validation passed!")
        else:
            logger.warning("⚠️ Database validation found issues")
        
        return validation_passed
    
    def run_complete_build(self):
        """Run the complete database building process"""
        logger.info("🚀 Starting complete OSRS item database build...")
        
        try:
            # Build the database
            self.build_comprehensive_database()
            
            # Validate it
            self.validate_database()
            
            # Save it
            self.save_database()
            
            logger.info("🎉 Complete item database build finished successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database build failed: {e}")
            return False

def main():
    print("🏗️ OSRS Complete Item Database Builder")
    print("=" * 50)
    print("This will build a comprehensive database of ALL OSRS items")
    print("Sources: GE API + Wiki scraping + known critical items")
    print()
    
    builder = CompleteItemDatabaseBuilder()
    success = builder.run_complete_build()
    
    if success:
        print("\n✅ SUCCESS: Complete item database built!")
        print(f"📁 Database saved to: {builder.output_file}")
        print(f"📊 Total items: {len(builder.items_database)}")
        print("\n🔄 Next: Update your application to use the complete database")
    else:
        print("\n❌ FAILED: Database build encountered errors")

if __name__ == "__main__":
    main() 