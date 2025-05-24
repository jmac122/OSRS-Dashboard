"""
OSRS GP/hour calculation functions for different activities.
Each function takes a params dictionary and returns calculated GP/hour.
"""

from .ge_api import get_ge_price, get_average_price, ITEM_IDS
import logging

logger = logging.getLogger(__name__)

def calculate_farming_gp_hr(params):
    """
    Calculate GP/hour for herb farming (e.g., Torstol).
    
    Expected params:
    - seed_id: Item ID for the seed
    - herb_id: Item ID for the harvested herb
    - compost_id: Item ID for compost used
    - avg_yield_per_patch: Average herbs yielded per patch
    - num_patches: Number of patches farmed
    - growth_time_minutes: Time for herbs to grow (default 80 for Torstol)
    """
    try:
        # Default values
        default_params = {
            'seed_id': ITEM_IDS.get('torstol_seed', 5309),
            'herb_id': ITEM_IDS.get('grimy_torstol', 207),
            'compost_id': ITEM_IDS.get('ultracompost', 21483),
            'avg_yield_per_patch': 8,
            'num_patches': 9,
            'growth_time_minutes': 80
        }
        
        # Merge with provided params
        calc_params = {**default_params, **params}
        
        # Get current GE prices
        seed_price_data = get_ge_price(calc_params['seed_id'])
        herb_price_data = get_ge_price(calc_params['herb_id'])
        compost_price_data = get_ge_price(calc_params['compost_id'])
        
        if not all([seed_price_data, herb_price_data, compost_price_data]):
            logger.warning("Could not fetch all required prices for farming calculation")
            return {"error": "Unable to fetch required item prices", "gp_hr": 0}
        
        # Calculate average prices
        seed_price = get_average_price(seed_price_data)
        herb_price = get_average_price(herb_price_data)
        compost_price = get_average_price(compost_price_data)
        
        # Calculate costs and revenue
        total_seed_cost = calc_params['num_patches'] * seed_price
        total_compost_cost = calc_params['num_patches'] * compost_price
        total_costs = total_seed_cost + total_compost_cost
        
        total_herbs_yielded = calc_params['num_patches'] * calc_params['avg_yield_per_patch']
        total_revenue = total_herbs_yielded * herb_price
        
        # Calculate profit per cycle
        profit_per_cycle = total_revenue - total_costs
        
        # Convert to GP/hour
        growth_time_hours = calc_params['growth_time_minutes'] / 60
        gp_hr = profit_per_cycle / growth_time_hours
        
        return {
            "gp_hr": round(gp_hr),
            "profit_per_cycle": round(profit_per_cycle),
            "costs": {
                "seeds": round(total_seed_cost),
                "compost": round(total_compost_cost),
                "total": round(total_costs)
            },
            "revenue": round(total_revenue),
            "cycle_time_hours": growth_time_hours,
            "prices_used": {
                "seed": round(seed_price),
                "herb": round(herb_price),
                "compost": round(compost_price)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in farming calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

def calculate_birdhouse_gp_hr(params):
    """
    Calculate GP/hour for birdhouse runs.
    
    Expected params:
    - log_id: Item ID for logs used
    - seed_id: Item ID for cheap seeds (10 for low level, 5 for high level)
    - avg_nests_per_run: Average nests received per run
    - avg_value_per_nest: Average GP value per nest
    - run_time_minutes: Active time per run in minutes
    - cycle_time_minutes: Total cycle time between runs (default 50)
    """
    try:
        # Default values for redwood birdhouses
        default_params = {
            'log_id': ITEM_IDS.get('redwood_logs', 19669),
            'seed_id': 5318,  # Potato seed (cheap)
            'avg_nests_per_run': 10,
            'avg_value_per_nest': 5000,  # Simplified average
            'run_time_minutes': 5,
            'cycle_time_minutes': 50,
            'num_birdhouses': 4,
            'seeds_per_house': 10
        }
        
        calc_params = {**default_params, **params}
        
        # Get current GE prices
        log_price_data = get_ge_price(calc_params['log_id'])
        seed_price_data = get_ge_price(calc_params['seed_id'])
        
        if not all([log_price_data, seed_price_data]):
            logger.warning("Could not fetch all required prices for birdhouse calculation")
            return {"error": "Unable to fetch required item prices", "gp_hr": 0}
        
        log_price = get_average_price(log_price_data)
        seed_price = get_average_price(seed_price_data)
        
        # Calculate costs per run
        log_cost_per_run = calc_params['num_birdhouses'] * log_price
        seed_cost_per_run = calc_params['num_birdhouses'] * calc_params['seeds_per_house'] * seed_price
        total_costs_per_run = log_cost_per_run + seed_cost_per_run
        
        # Calculate revenue per run
        revenue_per_run = calc_params['avg_nests_per_run'] * calc_params['avg_value_per_nest']
        
        # Calculate profit per run
        profit_per_run = revenue_per_run - total_costs_per_run
        
        # Convert to GP/hour
        total_cycle_time_hours = (calc_params['run_time_minutes'] + calc_params['cycle_time_minutes']) / 60
        gp_hr = profit_per_run / total_cycle_time_hours
        
        return {
            "gp_hr": round(gp_hr),
            "profit_per_run": round(profit_per_run),
            "costs": {
                "logs": round(log_cost_per_run),
                "seeds": round(seed_cost_per_run),
                "total": round(total_costs_per_run)
            },
            "revenue": round(revenue_per_run),
            "cycle_time_hours": total_cycle_time_hours,
            "prices_used": {
                "logs": round(log_price),
                "seeds": round(seed_price)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in birdhouse calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

def calculate_gotr_gp_hr(params):
    """
    Calculate GP/hour for Guardians of the Rift (GOTR).
    
    Expected params:
    - essence_id: Item ID for pure essence
    - games_per_hour: Number of games per hour
    - avg_points_per_game: Average points earned per game
    - avg_rune_value_per_game: Average value of runes crafted per game
    - avg_pearl_value_per_game: Average value from abyssal pearls per game
    - essence_per_game: Pure essence used per game
    """
    try:
        default_params = {
            'essence_id': ITEM_IDS.get('pure_essence', 7936),
            'games_per_hour': 4,
            'avg_points_per_game': 350,
            'avg_rune_value_per_game': 15000,  # Simplified
            'avg_pearl_value_per_game': 8000,  # Simplified
            'essence_per_game': 150
        }
        
        calc_params = {**default_params, **params}
        
        # Get pure essence price
        essence_price_data = get_ge_price(calc_params['essence_id'])
        
        if not essence_price_data:
            logger.warning("Could not fetch essence price for GOTR calculation")
            return {"error": "Unable to fetch essence price", "gp_hr": 0}
        
        essence_price = get_average_price(essence_price_data)
        
        # Calculate costs per game
        essence_cost_per_game = calc_params['essence_per_game'] * essence_price
        
        # Calculate revenue per game
        revenue_per_game = calc_params['avg_rune_value_per_game'] + calc_params['avg_pearl_value_per_game']
        
        # Calculate profit per game
        profit_per_game = revenue_per_game - essence_cost_per_game
        
        # Convert to GP/hour
        gp_hr = profit_per_game * calc_params['games_per_hour']
        
        return {
            "gp_hr": round(gp_hr),
            "profit_per_game": round(profit_per_game),
            "costs": {
                "essence_per_game": round(essence_cost_per_game),
                "essence_per_hour": round(essence_cost_per_game * calc_params['games_per_hour'])
            },
            "revenue_per_game": round(revenue_per_game),
            "revenue_per_hour": round(revenue_per_game * calc_params['games_per_hour']),
            "games_per_hour": calc_params['games_per_hour'],
            "prices_used": {
                "essence": round(essence_price)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in GOTR calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

def calculate_slayer_gp_hr(params):
    """
    Calculate GP/hour for slayer tasks.
    
    Expected params:
    - monster_name: Name of the monster for reference
    - kills_per_hour: Number of kills per hour
    - avg_loot_value_per_kill: Average loot value per kill
    - avg_supply_cost_per_hour: Average cost of supplies per hour
    """
    try:
        default_params = {
            'monster_name': 'Rune Dragons',
            'kills_per_hour': 40,
            'avg_loot_value_per_kill': 37000,
            'avg_supply_cost_per_hour': 100000
        }
        
        calc_params = {**default_params, **params}
        
        # Calculate revenue per hour
        revenue_per_hour = calc_params['kills_per_hour'] * calc_params['avg_loot_value_per_kill']
        
        # Calculate profit per hour
        gp_hr = revenue_per_hour - calc_params['avg_supply_cost_per_hour']
        
        return {
            "gp_hr": round(gp_hr),
            "monster_name": calc_params['monster_name'],
            "kills_per_hour": calc_params['kills_per_hour'],
            "revenue_per_hour": round(revenue_per_hour),
            "supply_cost_per_hour": round(calc_params['avg_supply_cost_per_hour']),
            "avg_loot_per_kill": round(calc_params['avg_loot_value_per_kill'])
        }
        
    except Exception as e:
        logger.error(f"Error in slayer calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

# Dictionary mapping activity types to calculation functions
CALCULATION_FUNCTIONS = {
    'farming': calculate_farming_gp_hr,
    'birdhouse': calculate_birdhouse_gp_hr,
    'gotr': calculate_gotr_gp_hr,
    'slayer': calculate_slayer_gp_hr
}

def calculate_activity_gp_hr(activity_type, params):
    """
    Main function to calculate GP/hour for any activity type.
    
    Args:
        activity_type (str): The type of activity ('farming', 'birdhouse', 'gotr', 'slayer')
        params (dict): Parameters specific to the activity
        
    Returns:
        dict: Calculation results including GP/hour
    """
    if activity_type not in CALCULATION_FUNCTIONS:
        return {"error": f"Unknown activity type: {activity_type}", "gp_hr": 0}
    
    calculation_func = CALCULATION_FUNCTIONS[activity_type]
    return calculation_func(params) 