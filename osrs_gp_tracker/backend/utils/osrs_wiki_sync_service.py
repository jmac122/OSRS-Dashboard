#!/usr/bin/env python3
"""
OSRS Wiki Sync Service for extracting detailed Slayer data.
"""

import requests
import time
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from .ge_api import get_ge_price, get_average_price

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSRSWikiSyncService:
    def __init__(self, database_service=None):
        """Initialize the wiki sync service"""
        self.database_service = database_service
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSRS-GP-Tracker/1.0 (Educational/Personal Use)'
        })
        
        # Known item ID mappings for common items
        self.known_item_ids = {
            'coins': 995,
            'bones': 526,
            'big bones': 532,
            'dragon bones': 536,
            'rune full helm': 1149,
            'rune platebody': 1127,
            'rune kiteshield': 1201,
            'rune scimitar': 1333,
            'granite maul': 1631,
            'abyssal whip': 4151,
            # Hydra items
            'hydra leather': 22100,
            'hydra tail': 22103,
            'hydra claw': 22109,
            'brimstone ring': 22114,
            # Other valuable drops
            'dragon chainbody': 3140,
            'draconic visage': 11286,
            'shield left half': 2366,
            'dragon spear': 1249,
            # Common rune items
            'rune longsword': 1289,
            'rune battleaxe': 1373,
            'rune mace': 1432,
            'rune dagger': 1213,
            'rune sword': 1289,
            'rune med helm': 1147,
            'rune chainbody': 1113,
            'rune platelegs': 1079,
            'rune plateskirt': 1093,
            'rune boots': 4131,
            'rune 2h sword': 1319,
            # Adamant items
            'adamant platebody': 1123,
            'adamant platelegs': 1073,
            'adamant boots': 4129,
            # Mithril/Steel/Iron items
            'mithril platebody': 1121,
            'steel platebody': 1119,
            'iron platebody': 1115,
            # Mystic robes
            'mystic robe top (dark)': 4101,
            'mystic robe bottom (dark)': 4103,
            'mystic hat (dark)': 4099,
            'mystic gloves (dark)': 4105,
            'mystic boots (dark)': 4107,
            # Common gems
            'uncut diamond': 1617,
            'uncut ruby': 1619,
            'uncut emerald': 1621,
            'uncut sapphire': 1623,
            # Common herbs
            'grimy ranarr weed': 207,
            'grimy snapdragon': 3051,
            'grimy torstol': 219,
            'grimy dwarf weed': 217,
            # Common resources
            'coal': 453,
            'iron ore': 440,
            'gold ore': 444,
            'gold bar': 2357,
            'steel bar': 2353,
            'mithril ore': 447,
            'mithril bar': 2359,
            'adamantite ore': 449,
            'runite ore': 451,
            'pure essence': 7936,
            # Common food/supplies
            'sharks': 385,
            'monkfish': 7946,
            'lobster': 379,
            # Common runes
            'nature rune': 561,
            'death rune': 560,
            'blood rune': 565,
            'chaos rune': 562,
            'fire rune': 554,
            # Talismans
            'chaos talisman': 1452,
            'nature talisman': 1462,
            # Key halves
            'loop half of key': 985,
            'tooth half of key': 987,
            # Special items
            'rune javelin': 830,
            'rune spear': 1247,
            'brimstone key': 22520,
            'clue scroll (hard)': 2722,
            'brittle key': 22557,
            # Cerberus drops
            'primordial crystal': 13231,
            'pegasian crystal': 13229,
            'eternal crystal': 13227,
            'smouldering stone': 13233,
            # Vorkath drops
            'dragonbone necklace': 22111,
            'vorkaths head': 21907,
            'skeletal visage': 22006,
            # Zulrah drops
            'tanzanite fang': 12922,
            'magic fang': 12932,
            'serpentine visage': 12927,
            'uncut onyx': 6571,
            # Nechryael drops
            'rune boots': 4131,
            'death rune': 560,
            # Common seeds
            'ranarr seed': 5295,
            'snapdragon seed': 5300,
            'torstol seed': 5304
        }
        
        # Base wiki URL
        self.wiki_base = "https://oldschool.runescape.wiki"
    
    def _make_request(self, url: str, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """Make a respectful request to the wiki"""
        try:
            time.sleep(delay)  # Rate limiting
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"✅ Successfully fetched: {url}")
            return soup
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch {url}: {str(e)}")
            return None
    
    def _parse_probability(self, prob_text: str) -> float:
        """Convert probability text like '1/512' to decimal"""
        try:
            prob_text = prob_text.strip().lower().replace(',', '')  # Remove commas
            
            # Handle fraction format (1/512)
            if '/' in prob_text:
                numerator, denominator = prob_text.split('/')
                return float(numerator) / float(denominator)
            
            # Handle percentage format (12.5%)
            if '%' in prob_text:
                return float(prob_text.replace('%', '')) / 100
            
            # Handle decimal format (0.125)
            return float(prob_text)
            
        except (ValueError, ZeroDivisionError):
            logger.warning(f"Could not parse probability: {prob_text}")
            return 0.0
    
    def _parse_quantity_range(self, quantity_text: str) -> List[int]:
        """Parse quantity text like '10-15' or '1' into [min, max]"""
        try:
            quantity_text = quantity_text.strip().replace(',', '')
            
            # Handle range format (10-15)
            if '-' in quantity_text or '–' in quantity_text:
                parts = re.split(r'[-–]', quantity_text)
                return [int(parts[0]), int(parts[1])]
            
            # Handle single value
            value = int(quantity_text)
            return [value, value]
            
        except (ValueError, IndexError):
            logger.warning(f"Could not parse quantity: {quantity_text}")
            return [1, 1]
    
    def _get_item_id(self, item_name: str) -> Optional[int]:
        """Get item ID from name, using known mappings or wiki lookup"""
        item_name_lower = item_name.lower().strip()
        
        # Check known mappings first
        if item_name_lower in self.known_item_ids:
            return self.known_item_ids[item_name_lower]
        
        # For now, return None for unknown items
        # Could implement wiki API lookup here later
        logger.warning(f"Unknown item ID for: {item_name}")
        return None
    
    def _parse_drop_table(self, soup: BeautifulSoup) -> Dict[str, List]:
        """Parse drop table from wiki page HTML"""
        drop_table = {
            'always': [],
            'common': [],
            'rare': [],
            'very_rare': []
        }
        
        try:
            # OSRS wiki uses specific patterns for drop tables
            # Look for sections with "Drops" heading
            drops_headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(r'Drops?', re.I))
            
            if drops_headings:
                logger.info(f"Found {len(drops_headings)} 'Drops' headings")
                
                # Look for tables after drops headings
                for heading in drops_headings:
                    # Find the next table after this heading
                    next_element = heading.find_next_sibling()
                    while next_element:
                        if next_element.name == 'table' and 'wikitable' in next_element.get('class', []):
                            logger.info(f"Found drop table after heading: {heading.get_text()}")
                            self._parse_wiki_drop_table(next_element, drop_table)
                            break
                        elif next_element.name in ['h2', 'h3', 'h4']:
                            break  # Hit next section, stop looking
                        next_element = next_element.find_next_sibling()
            
            # Also look for tables with specific drop-related headers
            all_wikitables = soup.find_all('table', class_='wikitable')
            
            for table in all_wikitables:
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                    header_text = ' '.join(headers)
                    
                    # Check if this table has drop-related headers
                    drop_keywords = ['item', 'quantity', 'rarity', 'drop rate', 'probability', 'chance']
                    if any(keyword in header_text for keyword in drop_keywords):
                        logger.info(f"Found potential drop table with headers: {headers}")
                        self._parse_wiki_drop_table(table, drop_table)
            
            # If still no drops found, add basic fallback
            total_drops = sum(len(drops) for drops in drop_table.values())
            if total_drops == 0:
                logger.warning("No drops found in wiki page, adding basic drops")
                drop_table['always'] = [
                    {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}  # Bones
                ]
                drop_table['common'] = [
                    {'item_id': 995, 'quantity_range': [50, 200], 'probability': 0.3}  # Coins
                ]
            
        except Exception as e:
            logger.error(f"Error parsing drop table: {e}")
            # Fallback to basic drops
            drop_table['always'] = [
                {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}  # Bones
            ]
        
        return drop_table
    
    def _parse_wiki_drop_table(self, table, drop_table: Dict[str, List]):
        """Parse a specific wikitable that contains drops"""
        try:
            rows = table.find_all('tr')[1:]  # Skip header row
            current_rarity = 'common'  # Default rarity
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:  # Need at least 3 columns for OSRS wiki format
                    continue
                
                # Check if this row indicates a rarity section
                row_text = row.get_text().strip().lower()
                if 'always' in row_text or 'guaranteed' in row_text:
                    current_rarity = 'always'
                    continue
                elif 'common' in row_text:
                    current_rarity = 'common'
                    continue
                elif 'uncommon' in row_text or 'rare' in row_text:
                    current_rarity = 'rare'
                    continue
                elif 'very rare' in row_text or 'very_rare' in row_text:
                    current_rarity = 'very_rare'
                    continue
                
                try:
                    # OSRS wiki structure: [image, item_name, quantity, rarity, price, high_alch]
                    # Extract item name from second cell (index 1) since first is usually empty/image
                    item_cell = cells[1] if len(cells) > 1 else cells[0]
                    item_links = item_cell.find_all('a')
                    if item_links:
                        item_name = item_links[0].get_text().strip()
                    else:
                        item_name = item_cell.get_text().strip()
                    
                    # Skip header-like text or empty items
                    if (item_name.lower() in ['item', 'drop', 'name', 'quantity', 'rarity', 'chance'] or 
                        not item_name or item_name == ''):
                        continue
                    
                    # Extract quantity from third cell (index 2)
                    if len(cells) >= 3:
                        quantity_text = cells[2].get_text().strip()
                        # Handle special cases
                        if quantity_text.lower() in ['nothing', '', 'varies']:
                            continue
                        quantity_range = self._parse_quantity_range(quantity_text)
                    else:
                        quantity_range = [1, 1]
                    
                    # Extract probability from rarity column (index 3) or other cells
                    probability = 0.05  # Default
                    
                    # First try the rarity column (index 3)
                    if len(cells) >= 4:
                        rarity_text = cells[3].get_text().strip()
                        prob_match = re.search(r'1/[\d,]+|[\d.]+%|[\d.]+/[\d,]+', rarity_text)
                        if prob_match:
                            probability = self._parse_probability(prob_match.group())
                        elif 'common' in rarity_text.lower():
                            probability = 0.1
                        elif 'uncommon' in rarity_text.lower():
                            probability = 0.05
                        elif 'rare' in rarity_text.lower():
                            probability = 0.01
                        elif 'very rare' in rarity_text.lower():
                            probability = 0.001
                    
                    # If no probability found, search all cells for fraction patterns
                    if probability == 0.05:  # Still default
                        for cell in cells:
                            cell_text = cell.get_text().strip()
                            # Look for patterns like "1/512", "1/1,024", etc.
                            prob_match = re.search(r'1/[\d,]+', cell_text)
                            if prob_match:
                                prob_str = prob_match.group().replace(',', '')
                                probability = self._parse_probability(prob_str)
                                break
                    
                    # Get item ID - try multiple name variations
                    item_id = self._get_item_id(item_name)
                    if not item_id:
                        # Try without parentheses
                        clean_name = re.sub(r'\([^)]*\)', '', item_name).strip()
                        item_id = self._get_item_id(clean_name)
                    
                    if item_id:
                        drop_entry = {
                            'item_id': item_id,
                            'quantity_range': quantity_range,
                            'probability': probability
                        }
                        drop_table[current_rarity].append(drop_entry)
                        logger.debug(f"Added drop: {item_name} (ID: {item_id}) - {quantity_range} @ {probability:.4f}")
                    else:
                        logger.debug(f"Skipped unknown item: {item_name}")
                
                except Exception as e:
                    logger.debug(f"Could not parse drop row: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error parsing wiki table: {e}")
    
    def _calculate_expected_loot_value(self, drop_table: dict) -> float:
        """Calculate expected loot value per kill from drop table"""
        total_expected_value = 0.0
        
        for rarity_tier in ['always', 'common', 'rare', 'very_rare']:
            drops = drop_table.get(rarity_tier, [])
            
            for drop in drops:
                item_id = drop.get('item_id')
                quantity_range = drop.get('quantity_range', [1, 1])
                probability = drop.get('probability', 0)
                
                if not item_id:
                    continue
                
                # Get current GE price (with fallback for unknown items)
                try:
                    price_data = get_ge_price(item_id)
                    if price_data:
                        item_price = get_average_price(price_data)
                    else:
                        # Fallback prices for common items
                        fallback_prices = {
                            526: 5,      # Bones
                            995: 1,      # Coins
                            1149: 20000, # Rune full helm
                            1201: 18000, # Rune kiteshield
                            1631: 120000, # Granite maul
                            4151: 2500000, # Abyssal whip
                            22100: 15000,  # Hydra leather
                            22109: 180000000, # Hydra claw
                            22103: 45000000   # Hydra tail
                        }
                        item_price = fallback_prices.get(item_id, 100)
                        logger.warning(f"Using fallback price for item {item_id}: {item_price}")
                except Exception as e:
                    logger.warning(f"Could not fetch price for item {item_id}: {e}")
                    continue
                
                avg_quantity = sum(quantity_range) / 2
                expected_value = item_price * avg_quantity * probability
                total_expected_value += expected_value
        
        return total_expected_value
    
    def sync_slayer_masters(self, db_client) -> Dict[str, dict]:
        """Sync Slayer Master data from wiki"""
        logger.info("🎯 Starting Slayer Masters sync...")
        
        masters_data = {}
        all_assignable_monsters = {}  # Collect all monsters from all masters
        
        # Known slayer masters with their wiki pages
        masters = {
            'turael': {
                'name': 'Turael',
                'wiki_path': '/w/Turael',
                'location': 'Burthorpe',
                'combat_req': 0,
                'slayer_req': 0
            },
            'spria': {
                'name': 'Spria',
                'wiki_path': '/w/Spria',
                'location': 'Draynor Village',
                'combat_req': 0,
                'slayer_req': 0
            },
            'mazchna': {
                'name': 'Mazchna',
                'wiki_path': '/w/Mazchna',
                'location': 'Canifis',
                'combat_req': 20,
                'slayer_req': 0
            },
            'vannaka': {
                'name': 'Vannaka',
                'wiki_path': '/w/Vannaka',
                'location': 'Edgeville Dungeon',
                'combat_req': 40,
                'slayer_req': 0
            },
            'chaeldar': {
                'name': 'Chaeldar',
                'wiki_path': '/w/Chaeldar',
                'location': 'Zanaris',
                'combat_req': 70,
                'slayer_req': 0
            },
            'nieve': {
                'name': 'Nieve',
                'wiki_path': '/w/Nieve',
                'location': 'Tree Gnome Stronghold',
                'combat_req': 85,
                'slayer_req': 0
            },
            'duradel': {
                'name': 'Duradel',
                'wiki_path': '/w/Duradel',
                'location': 'Shilo Village',
                'combat_req': 100,
                'slayer_req': 50
            }
        }
        
        for master_id, master_info in masters.items():
            try:
                url = f"{self.wiki_base}{master_info['wiki_path']}"
                soup = self._make_request(url)
                
                if not soup:
                    continue
                
                # Initialize master data
                master_data = {
                    'name': master_info['name'],
                    'location': master_info['location'],
                    'combat_req': master_info['combat_req'],
                    'slayer_req': master_info['slayer_req'],
                    'wiki_url': url,
                    'task_assignments': {},
                    'avg_task_quantity': {},
                    'last_synced': datetime.now().isoformat()
                }
                
                # Parse actual task assignment table from wiki
                logger.info(f"🔍 Parsing task assignments for {master_info['name']}...")
                assignable_monsters = self._parse_slayer_master_tasks(soup)
                
                if assignable_monsters:
                    # Convert to assignment probabilities (from weights)
                    total_weight = sum(monster['assignment_weight'] for monster in assignable_monsters.values())
                    
                    assignments = {}
                    quantities = {}
                    
                    for monster_id, monster_data in assignable_monsters.items():
                        # Calculate probability from weight
                        probability = monster_data['assignment_weight'] / total_weight if total_weight > 0 else 0
                        assignments[monster_id] = probability
                        quantities[monster_id] = monster_data['task_amount_range']
                        
                        # Add to global monster collection
                        all_assignable_monsters[monster_id] = monster_data
                    
                    master_data['task_assignments'] = assignments
                    master_data['avg_task_quantity'] = quantities
                    
                    logger.info(f"✅ Found {len(assignable_monsters)} assignable monsters for {master_info['name']}")
                else:
                    logger.warning(f"No task assignments found for {master_info['name']}, using fallback data")
                    # Use simplified fallback data if parsing fails
                    if master_id in ['nieve', 'duradel']:
                        assignments = {
                            'gargoyles': 0.08, 'abyssal_demons': 0.06,
                            'greater_demons': 0.07, 'black_demons': 0.06,
                            'alchemical_hydra': 0.02, 'cerberus': 0.02,
                            'rune_dragons': 0.03, 'nechryael': 0.05
                        }
                    else:
                        assignments = {
                            'cows': 0.15, 'spiders': 0.12, 'rats': 0.10,
                            'bats': 0.08, 'bears': 0.07
                        }
                    
                    master_data['task_assignments'] = assignments
                    master_data['avg_task_quantity'] = {
                        monster: [50, 100] for monster in assignments.keys()
                    }
                
                masters_data[master_id] = master_data
                
                # Save to database
                if self.database_service:
                    self.database_service.add_global_item(
                        db_client, 'slayer', 'masters', master_id, master_data
                    )
                    logger.info(f"✅ Saved master: {master_info['name']}")
                
            except Exception as e:
                logger.error(f"❌ Error processing master {master_id}: {str(e)}")
                continue
        
        # Store the collected monsters for use in sync_slayer_monsters
        self._all_assignable_monsters = all_assignable_monsters
        
        logger.info(f"🎯 Slayer Masters sync complete: {len(masters_data)} masters")
        logger.info(f"📋 Total unique assignable monsters found: {len(all_assignable_monsters)}")
        
        return masters_data
    
    def sync_slayer_monsters(self, db_client) -> Dict[str, dict]:
        """Sync detailed monster data from wiki"""
        logger.info("👹 Starting Slayer Monsters sync...")
        
        monsters_data = {}
        
        # Use dynamically collected monsters from Slayer Masters if available
        if hasattr(self, '_all_assignable_monsters') and self._all_assignable_monsters:
            monsters = self._all_assignable_monsters
            logger.info(f"🎯 Using {len(monsters)} monsters collected from Slayer Master pages")
        else:
            # Fallback to key profitable monsters if no dynamic collection available
            logger.warning("No dynamic monster collection available, using fallback list")
            monsters = {
                'gargoyles': {
                    'name': 'Gargoyles',
                    'wiki_path': '/w/Gargoyle',
                    'slayer_req': 75
                },
                'abyssal_demons': {
                    'name': 'Abyssal demons',
                    'wiki_path': '/w/Abyssal_demon',
                    'slayer_req': 85
                },
                'alchemical_hydra': {
                    'name': 'Alchemical Hydra',
                    'wiki_path': '/w/Alchemical_Hydra',
                    'slayer_req': 95
                },
                'nechryael': {
                    'name': 'Nechryael',
                    'wiki_path': '/w/Nechryael',
                    'slayer_req': 80
                },
                'rune_dragons': {
                    'name': 'Rune dragons',
                    'wiki_path': '/w/Rune_dragon',
                    'slayer_req': 1
                },
                'cerberus': {
                    'name': 'Cerberus',
                    'wiki_path': '/w/Cerberus',
                    'slayer_req': 91
                },
                'vorkath': {
                    'name': 'Vorkath',
                    'wiki_path': '/w/Vorkath',
                    'slayer_req': 1
                },
                'zulrah': {
                    'name': 'Zulrah',
                    'wiki_path': '/w/Zulrah',
                    'slayer_req': 1
                }
            }
        
        total_monsters = len(monsters)
        processed_count = 0
        
        for monster_id, monster_info in monsters.items():
            try:
                processed_count += 1
                url = f"{self.wiki_base}{monster_info['wiki_path']}"
                
                logger.info(f"🔍 Processing {processed_count}/{total_monsters}: {monster_info['name']}")
                
                # Add rate limiting for large numbers of monsters
                if total_monsters > 10:
                    time.sleep(2.0)  # 2 second delay for large collections
                else:
                    time.sleep(1.0)  # 1 second delay for small collections
                
                soup = self._make_request(url, delay=0)  # Skip additional delay in _make_request
                
                if not soup:
                    logger.warning(f"❌ Failed to fetch page for {monster_info['name']}")
                    continue
                
                # Initialize monster data
                monster_data = {
                    'name': monster_info['name'],
                    'wiki_slug': monster_id,
                    'slayer_level_req': monster_info.get('slayer_req', 1),
                    'wiki_url': url,
                    'drop_table': {
                        'always': [],
                        'common': [],
                        'rare': [],
                        'very_rare': []
                    },
                    'last_synced': datetime.now().isoformat()
                }
                
                # Extract basic stats from infobox
                infobox = soup.find('table', class_='infobox-monster')
                if infobox:
                    # Extract combat level
                    combat_row = infobox.find('tr', string=re.compile(r'Combat level', re.I))
                    if combat_row:
                        combat_cell = combat_row.find_next_sibling('tr')
                        if combat_cell:
                            combat_text = combat_cell.get_text().strip()
                            try:
                                monster_data['combat_level'] = int(re.search(r'\d+', combat_text).group())
                            except:
                                pass
                    
                    # Extract hitpoints
                    hp_row = infobox.find('tr', string=re.compile(r'Hitpoints', re.I))
                    if hp_row:
                        hp_cell = hp_row.find_next_sibling('tr')
                        if hp_cell:
                            hp_text = hp_cell.get_text().strip()
                            try:
                                monster_data['monster_hp'] = int(re.search(r'\d+', hp_text).group())
                            except:
                                pass
                
                # Parse actual drop table from wiki page
                logger.info(f"🔍 Scraping drop table for {monster_info['name']}...")
                scraped_drop_table = self._parse_drop_table(soup)
                monster_data['drop_table'] = scraped_drop_table
                
                # Add known combat stats and estimates
                combat_stats = {
                    'alchemical_hydra': {
                        'combat_level': 426,
                        'monster_hp': 1200,
                        'avg_kill_time_seconds_base': 120,
                        'base_kph_range': [25, 30],
                        'common_supply_cost_per_hour_base': 120000,
                        'weakness': 'Ranged',
                        'required_items': [22114],
                        'notes': 'Requires 95 Slayer. Multiple phases with prayer switches.'
                    },
                    'gargoyles': {
                        'combat_level': 111,
                        'monster_hp': 105,
                        'avg_kill_time_seconds_base': 15,
                        'base_kph_range': [350, 400],
                        'common_supply_cost_per_hour_base': 30000,
                        'weakness': 'Crush',
                        'required_items': [1596],
                        'notes': 'Requires rock hammer to finish. High alchables.'
                    },
                    'abyssal_demons': {
                        'combat_level': 124,
                        'monster_hp': 150,
                        'avg_kill_time_seconds_base': 12,
                        'base_kph_range': [400, 450],
                        'common_supply_cost_per_hour_base': 40000,
                        'weakness': 'Slash',
                        'notes': 'Fast task with valuable whip drops.'
                    },
                    'nechryael': {
                        'combat_level': 115,
                        'monster_hp': 105,
                        'avg_kill_time_seconds_base': 18,
                        'base_kph_range': [200, 250],
                        'common_supply_cost_per_hour_base': 35000,
                        'weakness': 'Slash',
                        'notes': 'Multi-combat area available.'
                    },
                    'rune_dragons': {
                        'combat_level': 380,
                        'monster_hp': 330,
                        'avg_kill_time_seconds_base': 90,
                        'base_kph_range': [35, 45],
                        'common_supply_cost_per_hour_base': 100000,
                        'weakness': 'Stab',
                        'notes': 'High defence, valuable drops.'
                    },
                    'cerberus': {
                        'combat_level': 318,
                        'monster_hp': 600,
                        'avg_kill_time_seconds_base': 180,
                        'base_kph_range': [15, 25],
                        'common_supply_cost_per_hour_base': 150000,
                        'weakness': 'Slash',
                        'notes': 'Boss requiring 91 Slayer.'
                    },
                    'vorkath': {
                        'combat_level': 732,
                        'monster_hp': 750,
                        'avg_kill_time_seconds_base': 150,
                        'base_kph_range': [20, 28],
                        'common_supply_cost_per_hour_base': 80000,
                        'weakness': 'Ranged',
                        'notes': 'Dragon boss with valuable drops.'
                    },
                    'zulrah': {
                        'combat_level': 725,
                        'monster_hp': 500,
                        'avg_kill_time_seconds_base': 120,
                        'base_kph_range': [25, 35],
                        'common_supply_cost_per_hour_base': 70000,
                        'weakness': 'Magic/Ranged',
                        'notes': 'Snake boss with unique drops.'
                    }
                }
                
                # Add known stats for this monster
                if monster_id in combat_stats:
                    monster_data.update(combat_stats[monster_id])
                else:
                    # Use estimation for unknown monsters
                    estimated_metrics = self._estimate_combat_metrics(monster_data)
                    monster_data.update({
                        'avg_kill_time_seconds_base': estimated_metrics['estimated_kill_time_seconds'],
                        'base_kph_range': [estimated_metrics['estimated_kills_per_hour'] - 10, 
                                         estimated_metrics['estimated_kills_per_hour'] + 10],
                        'common_supply_cost_per_hour_base': estimated_metrics['estimated_supply_cost_per_hour'],
                        'notes': f'Estimated metrics based on combat level {monster_data.get("combat_level", "unknown")} and Slayer req {monster_data.get("slayer_level_req", 1)}.'
                    })
                
                # If scraping didn't find good drop data, add some basic fallbacks
                if not any(monster_data['drop_table'].values()):
                    logger.warning(f"No drops found for {monster_info['name']}, adding fallback drops")
                    monster_data['drop_table']['always'] = [
                        {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}  # Bones
                    ]
                    monster_data['drop_table']['common'] = [
                        {'item_id': 995, 'quantity_range': [50, 200], 'probability': 0.3}  # Coins
                    ]
                
                monsters_data[monster_id] = monster_data
                
                # Calculate required validation fields
                expected_loot = self._calculate_expected_loot_value(monster_data['drop_table'])
                base_kph = sum(monster_data.get('base_kph_range', [30, 40])) / 2
                supply_cost = monster_data.get('common_supply_cost_per_hour_base', 50000)
                
                # Add required fields for validation
                monster_data.update({
                    'avg_loot_value_per_kill': expected_loot,
                    'kills_per_hour': base_kph,
                    'avg_supply_cost_per_hour': supply_cost
                })
                
                logger.info(f"💰 {monster_info['name']}: {expected_loot:.1f} GP/kill, {base_kph:.1f} KPH, {supply_cost} supply cost/hr")
                
                # Save to database
                if self.database_service:
                    self.database_service.add_global_item(
                        db_client, 'slayer', 'monsters', monster_id, monster_data
                    )
                    logger.info(f"✅ Saved monster: {monster_info['name']}")
                
            except Exception as e:
                logger.error(f"❌ Error processing monster {monster_id}: {str(e)}")
                continue
        
        logger.info(f"👹 Slayer Monsters sync complete: {len(monsters_data)} monsters")
        return monsters_data
    
    def sync_slayer_data(self, db_client):
        """
        Comprehensive sync of Slayer Masters and Monsters data from OSRS Wiki
        Now scrapes ALL assignable monsters from all Slayer Masters
        """
        logger.info("🚀 Starting comprehensive Slayer data sync...")
        logger.info("📋 This will scrape ALL assignable monsters from ALL Slayer Masters")
        
        try:
            # Sync masters first to collect all assignable monsters
            logger.info("🎯 Step 1: Syncing Slayer Masters and collecting assignable monsters...")
            masters = self.sync_slayer_masters(db_client)
            logger.info(f"✅ Synced {len(masters)} Slayer Masters")
            
            # Check how many unique monsters were collected
            total_monsters = len(getattr(self, '_all_assignable_monsters', {}))
            logger.info(f"📊 Collected {total_monsters} unique assignable monsters across all masters")
            
            if total_monsters > 50:
                logger.warning(f"⚠️  Large monster collection detected ({total_monsters} monsters)")
                logger.warning("⏱️  This may take 5-10 minutes with rate limiting...")
            
            # Then sync monsters with calculated loot values from the collected list
            logger.info("👹 Step 2: Scraping loot tables for all assignable monsters...")
            monsters = self.sync_slayer_monsters(db_client)
            logger.info(f"✅ Synced {len(monsters)} Slayer Monsters with loot tables")
            
            # Create comprehensive sync log
            sync_log = {
                'sync_type': 'slayer_comprehensive_all_monsters',
                'timestamp': datetime.now().isoformat(),
                'masters_synced': len(masters),
                'monsters_synced': len(monsters),
                'total_assignable_monsters_found': total_monsters,
                'status': 'completed',
                'data_source': 'wiki_scraped_comprehensive'
            }
            
            if self.database_service:
                self.database_service.add_sync_log(db_client, sync_log)
            
            logger.info(f"🎉 Comprehensive Slayer sync completed successfully!")
            logger.info(f"   📋 Masters: {len(masters)}")
            logger.info(f"   👹 Monsters with loot tables: {len(monsters)}")
            logger.info(f"   🎯 Total assignable monsters found: {total_monsters}")
            
            return {
                'success': True,
                'masters': masters,
                'monsters': monsters,
                'total_assignable_monsters': total_monsters,
                'sync_log': sync_log
            }
            
        except Exception as e:
            logger.error(f"💥 Comprehensive Slayer sync failed: {str(e)}")
            # Fallback to hardcoded data if scraping fails
            logger.info("⚠️  Falling back to hardcoded data for development...")
            masters, monsters = self.sync_hardcoded_data(db_client)
            
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True,
                'masters': masters,
                'monsters': monsters
            }

    def sync_hardcoded_data(self, db_client):
        """Sync hardcoded Slayer data for testing"""
        logger.info("🚀 Syncing hardcoded Slayer data...")
        
        # Slayer Masters
        masters_data = {
            'nieve': {
                'name': 'Nieve',
                'location': 'Tree Gnome Stronghold',
                'combat_req': 85,
                'slayer_req': 0,
                'wiki_url': 'https://oldschool.runescape.wiki/w/Nieve',
                'task_assignments': {
                    'gargoyles': 0.08,
                    'abyssal_demons': 0.06,
                    'alchemical_hydra': 0.02,
                    'greater_demons': 0.07,
                    'nechryael': 0.05
                },
                'avg_task_quantity': {
                    'gargoyles': [110, 170],
                    'abyssal_demons': [130, 200],
                    'alchemical_hydra': [95, 125],
                    'greater_demons': [120, 185],
                    'nechryael': [110, 170]
                },
                'last_synced': datetime.now().isoformat()
            },
            'duradel': {
                'name': 'Duradel',
                'location': 'Shilo Village',
                'combat_req': 100,
                'slayer_req': 50,
                'wiki_url': 'https://oldschool.runescape.wiki/w/Duradel',
                'task_assignments': {
                    'gargoyles': 0.09,
                    'abyssal_demons': 0.07,
                    'alchemical_hydra': 0.03,
                    'greater_demons': 0.08,
                    'nechryael': 0.06
                },
                'avg_task_quantity': {
                    'gargoyles': [120, 185],
                    'abyssal_demons': [140, 220],
                    'alchemical_hydra': [95, 125],
                    'greater_demons': [130, 200],
                    'nechryael': [120, 185]
                },
                'last_synced': datetime.now().isoformat()
            }
        }
        
        # Monsters data
        monsters_data = {
            'gargoyles': {
                'name': 'Gargoyles',
                'wiki_slug': 'gargoyles',
                'slayer_level_req': 75,
                'combat_level': 111,
                'monster_hp': 105,
                'avg_kill_time_seconds_base': 15,
                'base_kph_range': [350, 400],
                'common_supply_cost_per_hour_base': 30000,
                'weakness': 'Crush',
                'required_items': [1596],
                'notes': 'Requires rock hammer to finish. High alchables.',
                'drop_table': {
                    'always': [
                        {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}
                    ],
                    'common': [
                        {'item_id': 995, 'quantity_range': [50, 150], 'probability': 0.25},
                        {'item_id': 1149, 'quantity_range': [1, 1], 'probability': 0.15},
                        {'item_id': 1201, 'quantity_range': [1, 1], 'probability': 0.12}
                    ],
                    'rare': [
                        {'item_id': 1631, 'quantity_range': [1, 1], 'probability': 1/512}
                    ],
                    'very_rare': []
                },
                'wiki_url': 'https://oldschool.runescape.wiki/w/Gargoyle',
                'last_synced': datetime.now().isoformat()
            },
            'abyssal_demons': {
                'name': 'Abyssal demons',
                'wiki_slug': 'abyssal_demons',
                'slayer_level_req': 85,
                'combat_level': 124,
                'monster_hp': 150,
                'avg_kill_time_seconds_base': 12,
                'base_kph_range': [400, 450],
                'common_supply_cost_per_hour_base': 40000,
                'weakness': 'Slash',
                'notes': 'Fast task with valuable whip drops.',
                'drop_table': {
                    'always': [
                        {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}
                    ],
                    'common': [
                        {'item_id': 995, 'quantity_range': [100, 300], 'probability': 0.2}
                    ],
                    'rare': [
                        {'item_id': 4151, 'quantity_range': [1, 1], 'probability': 1/512}
                    ],
                    'very_rare': []
                },
                'wiki_url': 'https://oldschool.runescape.wiki/w/Abyssal_demon',
                'last_synced': datetime.now().isoformat()
            },
            'alchemical_hydra': {
                'name': 'Alchemical Hydra',
                'wiki_slug': 'alchemical_hydra',
                'slayer_level_req': 95,
                'combat_level': 426,
                'monster_hp': 300,
                'avg_kill_time_seconds_base': 120,
                'base_kph_range': [25, 30],
                'common_supply_cost_per_hour_base': 120000,
                'weakness': 'Ranged',
                'required_items': [22114],
                'notes': 'Requires 95 Slayer. Multiple phases with prayer switches.',
                'drop_table': {
                    'always': [
                        {'item_id': 526, 'quantity_range': [1, 1], 'probability': 1.0}
                    ],
                    'common': [
                        {'item_id': 995, 'quantity_range': [1000, 3000], 'probability': 0.2},
                        {'item_id': 22100, 'quantity_range': [1, 1], 'probability': 0.04}
                    ],
                    'rare': [
                        {'item_id': 22109, 'quantity_range': [1, 1], 'probability': 0.002},
                        {'item_id': 22103, 'quantity_range': [1, 1], 'probability': 0.002}
                    ],
                    'very_rare': []
                },
                'wiki_url': 'https://oldschool.runescape.wiki/w/Alchemical_Hydra',
                'last_synced': datetime.now().isoformat()
            }
        }
        
        # Save masters
        for master_id, master_data in masters_data.items():
            try:
                if self.database_service:
                    self.database_service.add_global_item(
                        db_client, 'slayer', 'masters', master_id, master_data
                    )
                    logger.info(f"✅ Added master: {master_data['name']}")
            except Exception as e:
                logger.error(f"❌ Error adding master {master_id}: {e}")
        
        # Save monsters
        for monster_id, monster_data in monsters_data.items():
            try:
                if self.database_service:
                    self.database_service.add_global_item(
                        db_client, 'slayer', 'monsters', monster_id, monster_data
                    )
                    logger.info(f"✅ Added monster: {monster_data['name']}")
            except Exception as e:
                logger.error(f"❌ Error adding monster {monster_id}: {e}")
        
        logger.info(f"🎉 Hardcoded data sync complete!")
        return masters_data, monsters_data

    def _parse_slayer_master_tasks(self, soup: BeautifulSoup) -> Dict[str, dict]:
        """Parse task assignment table from Slayer Master wiki page"""
        assignable_monsters = {}
        
        try:
            # Find the tasks table (usually has headers like "Monster", "Amount", "Weight")
            tables = soup.find_all('table', class_='wikitable')
            
            for table in tables:
                header_row = table.find('tr')
                if not header_row:
                    continue
                    
                headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
                # Check if this looks like a task assignment table
                if not any(keyword in ' '.join(headers) for keyword in ['monster', 'amount', 'weight', 'task']):
                    continue
                
                logger.info(f"Found task assignment table with headers: {headers}")
                
                # Parse each row
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    
                    try:
                        # Extract monster name (usually first column)
                        monster_cell = cells[0]
                        monster_name = monster_cell.get_text().strip()
                        
                        # Skip empty or header-like rows
                        if not monster_name or monster_name.lower() in ['monster', 'task', 'amount']:
                            continue
                        
                        # Try to extract the wiki link for the monster
                        monster_link = monster_cell.find('a')
                        wiki_path = None
                        if monster_link and monster_link.get('href'):
                            wiki_path = monster_link.get('href')
                        
                        # Create monster slug (simplified name for our database)
                        monster_slug = monster_name.lower().replace(' ', '_').replace("'", "").replace('-', '_')
                        
                        # Extract amount range (usually second column)
                        amount_text = cells[1].get_text().strip() if len(cells) > 1 else "50-100"
                        amount_range = self._parse_quantity_range(amount_text)
                        
                        # Extract weight (usually last column with numbers)
                        weight = 5  # Default weight
                        for cell in reversed(cells):
                            cell_text = cell.get_text().strip()
                            if cell_text.isdigit():
                                weight = int(cell_text)
                                break
                        
                        # Estimate Slayer requirement from links or name patterns
                        slayer_req = self._estimate_slayer_requirement(monster_name)
                        
                        assignable_monsters[monster_slug] = {
                            'name': monster_name,
                            'wiki_path': wiki_path or f'/w/{monster_name.replace(" ", "_")}',
                            'slayer_req': slayer_req,
                            'task_amount_range': amount_range,
                            'assignment_weight': weight
                        }
                        
                        logger.debug(f"Added assignable monster: {monster_name} -> {monster_slug}")
                        
                    except Exception as e:
                        logger.debug(f"Could not parse task row: {e}")
                        continue
                
                break  # Found and parsed the main task table
        
        except Exception as e:
            logger.error(f"Error parsing Slayer Master tasks: {e}")
        
        return assignable_monsters
    
    def _estimate_slayer_requirement(self, monster_name: str) -> int:
        """Estimate Slayer requirement based on monster name"""
        name_lower = monster_name.lower()
        
        # Known Slayer requirements
        slayer_reqs = {
            'aberrant spectre': 60, 'abyssal demon': 85, 'ankou': 1,
            'basilisk': 40, 'bloodveld': 50, 'cave crawler': 10,
            'dust devil': 65, 'gargoyle': 75, 'greater demon': 1,
            'hellhound': 1, 'iron dragon': 1, 'kalphite': 1,
            'kurask': 70, 'nechryael': 80, 'turoth': 55,
            'tzhaar': 1, 'waterfiend': 1, 'wyrm': 62,
            'drake': 84, 'hydra': 95, 'alchemical hydra': 95,
            'cerberus': 91, 'kraken': 87, 'thermonuclear smoke devil': 93,
            'cave kraken': 87, 'smoke devil': 93, 'dark beast': 90,
            'abyssal sire': 85, 'dagannoth': 1, 'black demon': 1,
            'blue dragon': 1, 'red dragon': 1, 'black dragon': 1,
            'steel dragon': 1, 'mithril dragon': 1, 'adamant dragon': 1,
            'rune dragon': 1, 'fire giant': 1, 'suqah': 1,
            'troll': 1, 'aviansie': 1, 'spiritual warrior': 68,
            'spiritual ranger': 63, 'spiritual mage': 83
        }
        
        # Check for exact matches or partial matches
        for monster, req in slayer_reqs.items():
            if monster in name_lower:
                return req
        
        # Default to 1 if unknown
        return 1 

    def _estimate_combat_metrics(self, monster_data: dict) -> dict:
        """Estimate realistic KPH and supply costs for monsters not in hardcoded stats"""
        combat_level = monster_data.get('combat_level', 100)
        monster_hp = monster_data.get('monster_hp', 100)
        slayer_req = monster_data.get('slayer_level_req', 1)
        
        # Base kill time estimation (in seconds)
        # Higher level monsters take longer
        base_kill_time = 10  # Minimum kill time
        
        # Adjust based on combat level
        if combat_level >= 400:  # Boss level
            base_kill_time = 120
        elif combat_level >= 300:  # High level monsters
            base_kill_time = 60
        elif combat_level >= 200:  # Mid-high level
            base_kill_time = 30
        elif combat_level >= 100:  # Mid level
            base_kill_time = 20
        else:  # Low level
            base_kill_time = 10
        
        # Adjust based on HP
        if monster_hp >= 500:
            base_kill_time *= 1.5
        elif monster_hp >= 300:
            base_kill_time *= 1.2
        elif monster_hp >= 150:
            base_kill_time *= 1.1
        
        # Adjust based on Slayer requirement (higher req = more specialized/slower)
        if slayer_req >= 90:
            base_kill_time *= 1.3
        elif slayer_req >= 75:
            base_kill_time *= 1.15
        elif slayer_req >= 50:
            base_kill_time *= 1.05
        
        # Calculate KPH from kill time
        kills_per_hour = 3600 / base_kill_time
        
        # Supply cost estimation
        base_supply_cost = 20000  # Base cost per hour
        
        # Higher level monsters require more supplies
        if combat_level >= 400:
            base_supply_cost = 100000
        elif combat_level >= 300:
            base_supply_cost = 70000
        elif combat_level >= 200:
            base_supply_cost = 50000
        elif combat_level >= 100:
            base_supply_cost = 35000
        else:
            base_supply_cost = 20000
        
        # Adjust for Slayer requirement (specialized gear/supplies)
        if slayer_req >= 90:
            base_supply_cost *= 1.5
        elif slayer_req >= 75:
            base_supply_cost *= 1.25
        elif slayer_req >= 50:
            base_supply_cost *= 1.1
        
        return {
            'estimated_kill_time_seconds': base_kill_time,
            'estimated_kills_per_hour': round(kills_per_hour),
            'estimated_supply_cost_per_hour': round(base_supply_cost)
        } 