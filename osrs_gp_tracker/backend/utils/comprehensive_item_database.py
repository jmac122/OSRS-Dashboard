#!/usr/bin/env python3
"""
Comprehensive OSRS Item Database Service
Fetches and caches item IDs from OSRS Wiki API and complete database
"""

import requests
import json
import os
import time
import logging
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class OSRSItemDatabase:
    def __init__(self, cache_file='osrs_items_cache.json'):
        self.cache_file = Path(__file__).parent / cache_file
        self.complete_db_file = Path(__file__).parent / 'complete_osrs_items.json'
        self.items_cache = {}
        self.complete_database = {}
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSRS-GP-Tracker/1.0 (Educational/Personal Use)'
        })
        
        # Load complete database first (if available)
        self.load_complete_database()
        
        # Load existing cache
        self.load_cache()
        
        # Merge complete database into cache
        if self.complete_database:
            self.items_cache.update(self.complete_database)
            logger.info(f"Merged {len(self.complete_database)} items from complete database")
        
        # Known critical items that we need immediately (fallback)
        self.critical_items = {
            # Coins and basics
            'coins': 995,
            'bones': 526,
            'big bones': 532,
            'dragon bones': 536,
            
            # Farming essentials
            'ranarr seed': 5295,
            'grimy ranarr weed': 207,
            'ultracompost': 21483,
            'potato seed': 5318,
            
            # Logs
            'logs': 1511,
            'redwood logs': 19669,
            
            # Runes
            'nature rune': 561,
            'death rune': 560,
            'blood rune': 565,
            'pure essence': 7936,
            
            # Common drops
            'abyssal whip': 4151,
            'granite maul': 1631,
            'rune boots': 4131,
            'loop half of key': 985,
            'tooth half of key': 987,
        }
        
        # Merge critical items (only if not already present)
        for name, item_id in self.critical_items.items():
            if name not in self.items_cache:
                self.items_cache[name] = item_id
    
    def load_complete_database(self):
        """Load the complete OSRS item database if available"""
        try:
            if self.complete_db_file.exists():
                with open(self.complete_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'items' in data:
                    self.complete_database = data['items']
                    metadata = data.get('metadata', {})
                    total_items = metadata.get('total_items', len(self.complete_database))
                    logger.info(f"Loaded complete database with {total_items} items")
                else:
                    logger.warning("Complete database file format is invalid")
            else:
                logger.info("Complete database not found, will use fallback methods")
        except Exception as e:
            logger.error(f"Error loading complete database: {e}")
            self.complete_database = {}
    
    def load_cache(self):
        """Load items from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Handle both old and new cache formats
                    if isinstance(cache_data, dict):
                        if 'items' in cache_data:
                            self.items_cache = cache_data['items']
                        else:
                            self.items_cache = cache_data
                    else:
                        self.items_cache = {}
                logger.info(f"Loaded {len(self.items_cache)} items from cache")
            else:
                logger.info("No cache file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.items_cache = {}
    
    def save_cache(self):
        """Save items to cache file"""
        try:
            cache_data = {
                'metadata': {
                    'total_items': len(self.items_cache),
                    'last_updated': time.time(),
                    'has_complete_db': bool(self.complete_database)
                },
                'items': self.items_cache
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.items_cache)} items to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def normalize_item_name(self, name: str) -> str:
        """Normalize item name for consistent lookup"""
        return name.lower().strip().replace('_', ' ')
    
    def get_item_id(self, item_name: str) -> Optional[int]:
        """Get item ID by name, using complete database first, then cache, then API"""
        normalized_name = self.normalize_item_name(item_name)
        
        # Check cache first (which includes complete database)
        if normalized_name in self.items_cache:
            return self.items_cache[normalized_name]
        
        # If we have a complete database, we should trust it's comprehensive
        if self.complete_database:
            logger.warning(f"Item not found in complete database: {item_name}")
            return None
        
        # Fallback: Try to fetch from Wiki API (old behavior)
        logger.info(f"Falling back to Wiki API for: {item_name}")
        item_id = self.fetch_item_id_from_wiki(normalized_name)
        
        if item_id:
            # Cache the result
            self.items_cache[normalized_name] = item_id
            self.save_cache()
            return item_id
        
        logger.warning(f"Could not find item ID for: {item_name}")
        return None
    
    def fetch_item_id_from_wiki(self, item_name: str) -> Optional[int]:
        """Fetch item ID from OSRS Wiki API (fallback method)"""
        try:
            # Use the Wiki's exchange namespace API
            search_url = "https://oldschool.runescape.wiki/api.php"
            params = {
                'action': 'opensearch',
                'search': item_name,
                'limit': 5,
                'namespace': 0,
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            if len(search_results) >= 4 and search_results[1]:
                # Try the first result
                page_title = search_results[1][0]
                return self.get_item_id_from_page(page_title)
            
        except Exception as e:
            logger.error(f"Error fetching item ID for {item_name}: {e}")
        
        return None
    
    def get_item_id_from_page(self, page_title: str) -> Optional[int]:
        """Extract item ID from a wiki page"""
        try:
            page_url = "https://oldschool.runescape.wiki/api.php"
            params = {
                'action': 'parse',
                'page': page_title,
                'format': 'json',
                'prop': 'wikitext'
            }
            
            response = self.session.get(page_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'parse' in data and 'wikitext' in data['parse']:
                wikitext = data['parse']['wikitext']['*']
                
                # Look for item ID in infobox
                import re
                id_patterns = [
                    r'\|\s*id\s*=\s*(\d+)',
                    r'\|\s*itemid\s*=\s*(\d+)',
                    r'\|\s*item_id\s*=\s*(\d+)',
                ]
                
                for pattern in id_patterns:
                    match = re.search(pattern, wikitext, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
            
        except Exception as e:
            logger.error(f"Error parsing page {page_title}: {e}")
        
        return None
    
    def bulk_populate_items(self, item_names: List[str]) -> Dict[str, Optional[int]]:
        """Populate multiple items efficiently"""
        results = {}
        
        for item_name in item_names:
            item_id = self.get_item_id(item_name)
            results[item_name] = item_id
            
            # Small delay to be respectful to the API (only if using fallback)
            if not self.complete_database:
                time.sleep(0.1)
        
        return results
    
    def search_items(self, partial_name: str, limit: int = 10) -> List[Dict[str, any]]:
        """Search for items by partial name"""
        normalized_search = self.normalize_item_name(partial_name)
        matches = []
        
        for item_name, item_id in self.items_cache.items():
            if normalized_search in item_name:
                matches.append({
                    'name': item_name,
                    'id': item_id,
                    'display_name': item_name.title()
                })
                
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        return {
            'total_items': len(self.items_cache),
            'has_complete_database': bool(self.complete_database),
            'complete_db_items': len(self.complete_database),
            'cache_file': str(self.cache_file),
            'complete_db_file': str(self.complete_db_file),
            'complete_db_exists': self.complete_db_file.exists()
        }
    
    def rebuild_complete_database(self):
        """Trigger a rebuild of the complete database"""
        logger.info("🔄 Triggering complete database rebuild...")
        
        try:
            # Import and run the database builder
            import sys
            import os
            
            # Add the parent directory to path to import the builder
            parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, parent_dir)
            
            from build_complete_item_database import CompleteItemDatabaseBuilder
            
            builder = CompleteItemDatabaseBuilder()
            success = builder.run_complete_build()
            
            if success:
                # Reload the complete database
                self.load_complete_database()
                
                # Update cache with new data
                if self.complete_database:
                    self.items_cache.update(self.complete_database)
                    self.save_cache()
                    
                logger.info("✅ Complete database rebuild successful")
                return True
            else:
                logger.error("❌ Complete database rebuild failed")
                return False
                
        except Exception as e:
            logger.error(f"Error rebuilding complete database: {e}")
            return False

# Global instance
item_database = OSRSItemDatabase() 