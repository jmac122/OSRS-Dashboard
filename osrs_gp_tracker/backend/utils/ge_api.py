import requests
import time
from cachetools import TTLCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for GE prices (5 minute TTL)
price_cache = TTLCache(maxsize=500, ttl=300)

# User-Agent as required by OSRS Wiki API
USER_AGENT = "OSRS GP Tracker - Local Development App - Version 1.0"

def get_ge_price(item_id):
    """
    Fetch the latest Grand Exchange price for a specific item ID.
    
    Args:
        item_id (int): The OSRS item ID
        
    Returns:
        dict: Contains 'high', 'low', 'highTime', 'lowTime' price data or None if error
    """
    try:
        # Check cache first
        cache_key = f"item_{item_id}"
        if cache_key in price_cache:
            logger.info(f"Cache hit for item {item_id}")
            return price_cache[cache_key]
        
        # Make API request
        url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}"
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        }
        
        logger.info(f"Fetching price for item {item_id} from OSRS Wiki API")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract price data for the specific item
        if 'data' in data and str(item_id) in data['data']:
            price_data = data['data'][str(item_id)]
            
            # Cache the result
            price_cache[cache_key] = price_data
            
            logger.info(f"Successfully fetched price for item {item_id}: {price_data}")
            return price_data
        else:
            logger.warning(f"No price data found for item {item_id}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"API request failed for item {item_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching price for item {item_id}: {e}")
        return None

def get_multiple_ge_prices(item_ids):
    """
    Fetch prices for multiple items in a single request.
    
    Args:
        item_ids (list): List of item IDs
        
    Returns:
        dict: Dictionary mapping item_id to price data
    """
    try:
        # Convert to comma-separated string
        ids_str = ','.join(map(str, item_ids))
        
        url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={ids_str}"
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        }
        
        logger.info(f"Fetching prices for items {item_ids} from OSRS Wiki API")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data:
            # Cache all results
            for item_id in item_ids:
                if str(item_id) in data['data']:
                    cache_key = f"item_{item_id}"
                    price_cache[cache_key] = data['data'][str(item_id)]
            
            return data['data']
        else:
            logger.warning(f"No price data found for items {item_ids}")
            return {}
            
    except requests.RequestException as e:
        logger.error(f"API request failed for items {item_ids}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error fetching prices for items {item_ids}: {e}")
        return {}

def get_average_price(price_data):
    """
    Calculate average price from high/low values.
    
    Args:
        price_data (dict): Price data with 'high' and 'low' keys
        
    Returns:
        float: Average price or None if invalid data
    """
    if not price_data or not isinstance(price_data, dict):
        return None
    
    high = price_data.get('high')
    low = price_data.get('low')
    
    if high is not None and low is not None:
        return (high + low) / 2
    elif high is not None:
        return high
    elif low is not None:
        return low
    else:
        return None

# Common OSRS item IDs for reference
ITEM_IDS = {
    # Farming - Seeds
    'ranarr_seed': 5295,
    'snapdragon_seed': 5300,
    'torstol_seed': 5309,
    'lantadyme_seed': 5302,
    'dwarf_weed_seed': 5303,
    'cadantine_seed': 5301,
    'kwuarm_seed': 5299,
    'irit_seed': 5297,
    'avantoe_seed': 5298,
    'harralander_seed': 5294,
    
    # Farming - Herbs (grimy)
    'grimy_ranarr': 207,
    'grimy_snapdragon': 3000,
    'grimy_torstol': 219,
    'grimy_lantadyme': 2485,
    'grimy_dwarf_weed': 217,
    'grimy_cadantine': 215,
    'grimy_kwuarm': 213,
    'grimy_irit': 209,
    'grimy_avantoe': 211,
    'grimy_harralander': 205,
    
    # Farming - Compost
    'ultracompost': 21483,
    'supercompost': 6034,
    'compost': 6032,
    
    # Birdhouse - Logs
    'logs': 1511,           # Regular logs
    'oak_logs': 1521,
    'willow_logs': 1519,
    'teak_logs': 6333,
    'maple_logs': 1517,
    'mahogany_logs': 6332,
    'yew_logs': 1515,
    'magic_logs': 1513,
    'redwood_logs': 19669,
    
    # Birdhouse - Seeds (cheap options)
    'potato_seed': 5318,
    'onion_seed': 5319,
    'cabbage_seed': 5324,
    'tomato_seed': 5322,
    'barley_seed': 5305,
    
    # Birdhouse - Bird nests
    'bird_nest': 5074,
    'bird_nest_seeds': 22798,
    'bird_nest_ring': 22797,
    
    # GOTR - Runes
    'blood_rune': 565,
    'soul_rune': 566,
    'nature_rune': 561,
    'law_rune': 563,
    'death_rune': 560,
    'astral_rune': 9075,
    'cosmic_rune': 564,
    'chaos_rune': 562,
    'mind_rune': 558,
    'body_rune': 559,
    
    # GOTR - Essence and pearls
    'pure_essence': 7936,
    'guardian_essence': 26880,
    'abyssal_pearls': 26879,
    
    # Legacy items (keeping for compatibility)
    'yew_seed': 5315,
    
    # Add more as needed
}