"""
OSRS GP/hour calculation functions for different activities.
Each function takes a params dictionary and returns calculated GP/hour.
"""

from .ge_api import get_ge_price, get_average_price, ITEM_IDS
from .database_service import item_db
import logging

logger = logging.getLogger(__name__)

def calculate_farming_gp_hr(params):
    """
    Calculate GP/hour for herb farming (e.g., Torstol).
    
    Expected params:
    - seed_id: Item ID for the seed (name will be resolved to ID)
    - herb_id: Item ID for the harvested herb (name will be resolved to ID)
    - compost_id: Item ID for compost used (name will be resolved to ID)
    - avg_yield_per_patch: Average herbs yielded per patch
    - num_patches: Number of patches farmed
    - growth_time_minutes: Time for herbs to grow (default 80 for Torstol)
    """
    from .comprehensive_item_database import item_database # Import here to avoid circular dependency if any
    try:
        # Default values
        default_params = {
            'seed_id': item_database.get_item_id('torstol seed') or 5309,
            'herb_id': item_database.get_item_id('grimy torstol') or 219,
            'compost_id': item_database.get_item_id('ultracompost') or 21483,
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
    from .comprehensive_item_database import item_database # Import here
    try:
        # Default values for redwood birdhouses
        default_params = {
            'log_id': item_database.get_item_id('redwood logs') or 19669,
            'seed_id': item_database.get_item_id('potato seed') or 5318,  # Potato seed (cheap)
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
    - primary_rune_id: (Optional) Item ID for specific rune type to focus on
    - estimated_runes_per_game: (Optional) Estimated runes of that type per game
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
        rune_value_per_game = calc_params['avg_rune_value_per_game']
        
        # If specific rune type is provided, calculate based on current market price
        if calc_params.get('primary_rune_id') and calc_params.get('estimated_runes_per_game'):
            rune_price_data = get_ge_price(calc_params['primary_rune_id'])
            if rune_price_data:
                rune_price = get_average_price(rune_price_data)
                rune_value_per_game = calc_params['estimated_runes_per_game'] * rune_price
        
        revenue_per_game = rune_value_per_game + calc_params['avg_pearl_value_per_game']
        
        # Calculate profit per game
        profit_per_game = revenue_per_game - essence_cost_per_game
        
        # Convert to GP/hour
        gp_hr = profit_per_game * calc_params['games_per_hour']
        
        result = {
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
        
        # Add rune price if specific rune was used
        if calc_params.get('primary_rune_id') and calc_params.get('estimated_runes_per_game'):
            rune_price_data = get_ge_price(calc_params['primary_rune_id'])
            if rune_price_data:
                rune_price = get_average_price(rune_price_data)
                result["prices_used"]["primary_rune"] = round(rune_price)
                result["runes_per_game"] = calc_params['estimated_runes_per_game']
        
        return result
        
    except Exception as e:
        logger.error(f"Error in GOTR calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

def calculate_slayer_gp_hr(params, user_params=None):
    """
    Calculate GP/hour for slayer tasks using comprehensive master assignment data.
    
    Expected params:
    - calculation_mode: 'expected' (default), 'specific', or 'breakdown'
    - slayer_master_id: ID of the selected slayer master ('nieve', 'duradel', etc.)
    - specific_monster_id: (only for 'specific' mode) ID of the specific monster
    - user_slayer_level: User's current slayer level (default 85)
    - user_combat_level: User's combat level (default 100)
    - user_attack_level: User's attack level (default 80)
    - user_strength_level: User's strength level (default 80)
    - user_defence_level: User's defence level (default 75)
    - user_ranged_level: User's ranged level (default 85)
    - user_magic_level: User's magic level (default 80)
    
    user_params (dict): User overrides from Firestore
    """
    try:
        # Default parameters
        default_params = {
            'calculation_mode': 'expected',
            'slayer_master_id': 'spria',
            'user_slayer_level': 85,
            'user_combat_level': 100,
            'user_attack_level': 80,
            'user_strength_level': 80,
            'user_defence_level': 75,
            'user_ranged_level': 85,
            'user_magic_level': 80
        }
        
        calc_params = {**default_params, **params}
        calculation_mode = calc_params.get('calculation_mode', 'expected')
        
        # Handle specific monster calculation
        if calculation_mode == 'specific':
            specific_monster_id = calc_params.get('specific_monster_id')
            if not specific_monster_id:
                return {"error": "Specific monster ID required for specific mode", "gp_hr": 0}
            
            return calculate_specific_monster_gp_hr(specific_monster_id, calc_params, user_params)
        
        # For 'expected' and 'breakdown' modes, calculate master assignment average
        # Get master data from database
        master_data = item_db.get_global_items('slayer', 'masters')
        master_info = master_data.get(calc_params['slayer_master_id'])
        
        if not master_info:
            logger.warning(f"Slayer master not found: {calc_params['slayer_master_id']}")
            return {"error": "Slayer master data not found", "gp_hr": 0}
        
        # Check if user meets master requirements
        if (calc_params['user_combat_level'] < master_info.get('combat_req', 0) or 
            calc_params['user_slayer_level'] < master_info.get('slayer_req', 0)):
            return {
                "error": f"User doesn't meet requirements for {master_info['name']}", 
                "gp_hr": 0,
                "requirements": {
                    "combat_required": master_info.get('combat_req', 0),
                    "slayer_required": master_info.get('slayer_req', 0),
                    "user_combat": calc_params['user_combat_level'],
                    "user_slayer": calc_params['user_slayer_level']
                }
            }
        
        # Get monster data from database
        monster_data = item_db.get_global_items('slayer', 'monsters')
        
        # Calculate weighted GP/hour across all possible assignments
        total_weighted_gp_hr = 0
        total_probability = 0
        task_details = []
        
        task_assignments = master_info.get('task_assignments', {})
        avg_task_quantities = master_info.get('avg_task_quantity', {})
        
        for monster_slug, assignment_probability in task_assignments.items():
            try:
                # Get monster info
                monster_info = monster_data.get(monster_slug)
                
                if not monster_info:
                    logger.warning(f"Monster data not found: {monster_slug}")
                    continue
                
                # Check if user meets slayer level requirement for this monster
                if calc_params['user_slayer_level'] < monster_info.get('slayer_level_req', 1):
                    logger.info(f"User doesn't meet slayer req for {monster_slug}")
                    continue
                
                # Estimate KPH based on user stats
                estimated_kph = estimate_kph(monster_info, calc_params, user_params)
                
                # Calculate expected loot per kill from drop table
                expected_loot_per_kill = calculate_expected_loot(monster_info.get('drop_table', {}))
                
                # Get task quantity range
                task_quantity_range = avg_task_quantities.get(monster_slug, [100, 150])
                avg_task_quantity = sum(task_quantity_range) / 2
                
                # Calculate task time (including travel/banking overhead)
                base_task_time_hours = avg_task_quantity / estimated_kph
                travel_banking_time_hours = 0.1  # 6 minutes overhead
                total_task_time_hours = base_task_time_hours + travel_banking_time_hours
                
                # Calculate supply costs
                base_supply_cost = monster_info.get('common_supply_cost_per_hour_base', 50000)
                adjusted_supply_cost = adjust_supply_cost(base_supply_cost, calc_params, user_params)
                task_supply_cost = adjusted_supply_cost * total_task_time_hours
                
                # Calculate task value
                task_revenue = expected_loot_per_kill * avg_task_quantity
                task_profit = task_revenue - task_supply_cost
                task_gp_hr = task_profit / total_task_time_hours
                
                # Weight by assignment probability
                weighted_gp_hr = task_gp_hr * assignment_probability
                total_weighted_gp_hr += weighted_gp_hr
                total_probability += assignment_probability
                
                # Store task details for breakdown mode
                if calculation_mode == 'breakdown':
                    task_details.append({
                        'monster_name': monster_info.get('name', monster_slug),
                        'assignment_probability': assignment_probability,
                        'estimated_kph': round(estimated_kph, 1),
                        'expected_loot_per_kill': round(expected_loot_per_kill),
                        'avg_task_quantity': round(avg_task_quantity),
                        'task_time_hours': round(total_task_time_hours, 2),
                        'task_gp_hr': round(task_gp_hr),
                        'weighted_contribution': round(weighted_gp_hr)
                    })
                
            except Exception as e:
                logger.error(f"Error processing monster {monster_slug}: {e}")
                continue
        
        # Calculate final GP/hour
        final_gp_hr = total_weighted_gp_hr / total_probability if total_probability > 0 else 0
        
        result = {
            "gp_hr": round(final_gp_hr),
            "master_name": master_info.get('name', 'Unknown'),
            "total_assignment_probability": round(total_probability, 3),
            "eligible_tasks": len([t for t in task_details if t.get('task_gp_hr', 0) > 0]),
            "user_levels": {
                "slayer": calc_params['user_slayer_level'],
                "combat": calc_params['user_combat_level']
            }
        }
        
        # Add breakdown details if requested
        if calculation_mode == 'breakdown':
            result["task_breakdown"] = sorted(task_details, key=lambda x: x['weighted_contribution'], reverse=True)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced slayer calculation: {e}")
        return {"error": str(e), "gp_hr": 0}

def calculate_specific_monster_gp_hr(monster_id, calc_params, user_params=None):
    """
    Calculate GP/hour for a specific monster.
    """
    try:
        # Get monster data from database
        monster_data = item_db.get_global_items('slayer', 'monsters')
        monster_info = monster_data.get(monster_id)
        
        if not monster_info:
            logger.warning(f"Monster not found: {monster_id}")
            return {"error": f"Monster '{monster_id}' not found", "gp_hr": 0}
        
        # Check if user meets slayer level requirement
        slayer_req = monster_info.get('slayer_level_req', 1)
        if calc_params['user_slayer_level'] < slayer_req:
            return {
                "error": f"Insufficient Slayer level for {monster_info.get('name', monster_id)}", 
                "gp_hr": 0,
                "requirements": {
                    "slayer_required": slayer_req,
                    "user_slayer": calc_params['user_slayer_level']
                }
            }
        
        # Estimate KPH based on user stats
        estimated_kph = estimate_kph(monster_info, calc_params, user_params)
        
        # Calculate expected loot per kill from drop table
        expected_loot_per_kill = calculate_expected_loot(monster_info.get('drop_table', {}))
        
        # Calculate supply costs
        base_supply_cost = monster_info.get('common_supply_cost_per_hour_base', 50000)
        adjusted_supply_cost = adjust_supply_cost(base_supply_cost, calc_params, user_params)
        
        # Calculate GP/hour
        hourly_revenue = estimated_kph * expected_loot_per_kill
        gp_hr = hourly_revenue - adjusted_supply_cost
        
        return {
            "gp_hr": round(gp_hr),
            "monster_name": monster_info.get('name', monster_id),
            "kills_per_hour": round(estimated_kph, 1),
            "loot_per_kill": round(expected_loot_per_kill),
            "hourly_revenue": round(hourly_revenue),
            "supply_cost_per_hour": round(adjusted_supply_cost),
            "user_levels": {
                "slayer": calc_params['user_slayer_level'],
                "combat": calc_params['user_combat_level']
            },
            "requirements": {
                "slayer_required": slayer_req,
                "combat_required": monster_info.get('combat_level_req', 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating specific monster GP/hr: {e}")
        return {"error": str(e), "gp_hr": 0}

def estimate_kph(monster_info, user_params, user_overrides=None):
    """
    Estimate kills per hour based on monster stats and user levels.
    """
    try:
        base_kph_range = monster_info.get('base_kph_range', [30, 40])
        base_kph = sum(base_kph_range) / 2
        
        # Check for user override first
        monster_slug = monster_info.get('wiki_slug', '')
        override_key = f"kph_{monster_slug}"
        if user_overrides and override_key in user_overrides:
            return float(user_overrides[override_key])
        
        # Level-based adjustments
        user_combat = user_params.get('user_combat_level', 126)
        user_slayer = user_params.get('user_slayer_level', 99)
        monster_combat = monster_info.get('combat_level', 100)
        monster_slayer_req = monster_info.get('slayer_level_req', 1)
        
        # Combat level efficiency factor (0.6 to 1.1)
        combat_efficiency = min(1.1, max(0.6, (user_combat / max(monster_combat, 80))))
        
        # Slayer level efficiency (small bonus for being well above requirement)
        slayer_bonus = 1.0 + min(0.1, (user_slayer - monster_slayer_req) / 200)
        
        # Weakness bonus (if user has high levels in the right combat style)
        weakness_bonus = 1.0
        weakness = monster_info.get('weakness', '').lower()
        if 'melee' in weakness or 'slash' in weakness or 'crush' in weakness:
            melee_avg = (user_params.get('user_attack_level', 99) + 
                        user_params.get('user_strength_level', 99)) / 2
            weakness_bonus = 1.0 + (melee_avg - 70) / 300
        elif 'ranged' in weakness:
            ranged_level = user_params.get('user_ranged_level', 99)
            weakness_bonus = 1.0 + (ranged_level - 70) / 300
        elif 'magic' in weakness:
            magic_level = user_params.get('user_magic_level', 99)
            weakness_bonus = 1.0 + (magic_level - 70) / 300
        
        # Apply adjustments
        adjusted_kph = base_kph * combat_efficiency * slayer_bonus * weakness_bonus
        
        # Clamp to reasonable bounds (50% to 150% of base)
        min_kph = base_kph * 0.5
        max_kph = base_kph * 1.5
        
        return max(min_kph, min(max_kph, adjusted_kph))
        
    except Exception as e:
        logger.error(f"Error estimating KPH: {e}")
        return 30  # Fallback

def calculate_expected_loot(drop_table):
    """
    Calculate expected loot value per kill from drop table.
    """
    try:
        total_expected_value = 0
        
        for rarity_tier in ['always', 'common', 'rare', 'very_rare']:
            drops = drop_table.get(rarity_tier, [])
            
            for drop in drops:
                item_id = drop.get('item_id')
                quantity_range = drop.get('quantity_range', [1, 1])
                probability = drop.get('probability', 0)
                
                if not item_id:
                    continue
                
                # Get current GE price
                price_data = get_ge_price(item_id)
                if not price_data:
                    logger.warning(f"Could not fetch price for item {item_id}")
                    continue
                
                item_price = get_average_price(price_data)
                avg_quantity = sum(quantity_range) / 2
                
                expected_value = item_price * avg_quantity * probability
                total_expected_value += expected_value
        
        return total_expected_value
        
    except Exception as e:
        logger.error(f"Error calculating expected loot: {e}")
        return 1000  # Fallback value

def adjust_supply_cost(base_cost, user_params, user_overrides=None):
    """
    Adjust supply costs based on user efficiency and overrides.
    """
    try:
        # Check for user override
        if user_overrides and 'supply_cost_multiplier' in user_overrides:
            return base_cost * float(user_overrides['supply_cost_multiplier'])
        
        # Efficiency adjustments based on levels
        user_combat = user_params.get('user_combat_level', 126)
        
        # Higher combat = more efficient, lower supply costs
        efficiency_factor = max(0.7, min(1.3, 1.0 - (user_combat - 90) / 200))
        
        return base_cost * efficiency_factor
        
    except Exception as e:
        logger.error(f"Error adjusting supply cost: {e}")
        return base_cost

def calculate_activity_gp_hr(activity_type, params):
    """
    Main dispatcher function for calculating GP/hour for different activities.
    
    Args:
        activity_type (str): Type of activity ('farming', 'birdhouse', 'gotr')
        params (dict): Activity-specific parameters
    
    Returns:
        dict: Calculation results with GP/hour and breakdown
    """
    try:
        if activity_type == 'farming':
            return calculate_farming_gp_hr(params)
        elif activity_type == 'birdhouse':
            return calculate_birdhouse_gp_hr(params)
        elif activity_type == 'gotr':
            return calculate_gotr_gp_hr(params)
        elif activity_type == 'slayer':
            return calculate_slayer_gp_hr(params)
        else:
            return {"error": f"Unknown activity type: {activity_type}", "gp_hr": 0}
    
    except Exception as e:
        logger.error(f"Error calculating GP/hour for {activity_type}: {e}")
        return {"error": str(e), "gp_hr": 0}

def get_slayer_task_breakdown(slayer_master_id, user_levels, user_id=None):
    """
    Get detailed breakdown of Slayer assignments for a specific master and user levels.
    
    Args:
        slayer_master_id (str): ID of the Slayer master
        user_levels (dict): User's skill levels
        user_id (str, optional): User ID for overrides
    
    Returns:
        dict: Breakdown of task assignments with probabilities and GP/hour estimates
    """
    try:
        # Get master data using the correct method
        masters_data = item_db.get_global_items('slayer', 'masters')
        master_data = masters_data.get(slayer_master_id)
        if not master_data:
            return {"error": f"Slayer master '{slayer_master_id}' not found"}
        
        # Get all monsters data using the correct method
        monsters_data = item_db.get_global_items('slayer', 'monsters')
        if not monsters_data:
            return {"error": "No monster data found"}
        
        # Get user overrides if available
        user_overrides = {}
        if user_id:
            try:
                user_overrides = item_db.get_user_overrides(user_id) or {}
            except Exception as e:
                logger.warning(f"Could not fetch user overrides for {user_id}: {e}")
        
        # Filter eligible assignments based on user levels and master assignments
        eligible_assignments = []
        total_weight = 0
        
        master_assignments = master_data.get('task_assignments', {})
        
        for assignment_id, assignment_weight in master_assignments.items():
            monster_data = monsters_data.get(assignment_id)
            if not monster_data:
                logger.warning(f"Monster data not found: {assignment_id}")
                continue
            
            # Check if user meets requirements
            slayer_req = monster_data.get('slayer_level_req', 1)
            combat_req = monster_data.get('combat_level_req', 1)
            
            user_slayer = user_levels.get('slayer_level', 1)
            user_combat = user_levels.get('combat_level', 3)
            
            if user_slayer >= slayer_req and user_combat >= combat_req:
                # Calculate GP/hour for this monster
                monster_params = {
                    'monster_id': assignment_id,
                    'user_slayer_level': user_slayer,
                    'user_combat_level': user_combat,
                    'user_attack_level': user_levels.get('attack_level', 1),
                    'user_strength_level': user_levels.get('strength_level', 1),
                    'user_defence_level': user_levels.get('defence_level', 1),
                    'user_ranged_level': user_levels.get('ranged_level', 1),
                    'user_magic_level': user_levels.get('magic_level', 1),
                }
                
                # Calculate stats for this assignment
                kills_per_hour = estimate_kph(monster_data, monster_params, user_overrides)
                avg_loot_value = calculate_expected_loot(monster_data.get('drop_table', {}))
                supply_cost = adjust_supply_cost(
                    monster_data.get('common_supply_cost_per_hour_base', 50000), 
                    monster_params, 
                    user_overrides
                )
                
                # Calculate GP/hour for this specific monster
                gp_per_hour = (kills_per_hour * avg_loot_value) - supply_cost
                
                # Estimate task completion details
                avg_task_quantities = master_data.get('avg_task_quantity', {})
                task_quantity_range = avg_task_quantities.get(assignment_id, [100, 150])
                avg_task_length = sum(task_quantity_range) / 2
                time_per_task_hours = avg_task_length / kills_per_hour if kills_per_hour > 0 else 1
                gp_per_task = gp_per_hour * time_per_task_hours
                
                assignment_info = {
                    'monster_name': monster_data.get('name', assignment_id),
                    'monster_id': assignment_id,
                    'weight': assignment_weight,
                    'probability': 0,  # Will be calculated after getting total weight
                    'slayer_requirement': slayer_req,
                    'combat_requirement': combat_req,
                    'kills_per_hour': round(kills_per_hour, 1),
                    'avg_loot_value_per_kill': round(avg_loot_value),
                    'supply_cost_per_hour': round(supply_cost),
                    'gp_per_hour': round(gp_per_hour),
                    'avg_task_length': round(avg_task_length),
                    'time_per_task_hours': round(time_per_task_hours, 2),
                    'gp_per_task': round(gp_per_task),
                    'requirements': f"{slayer_req} Slayer, {combat_req} Combat"
                }
                
                eligible_assignments.append(assignment_info)
                total_weight += assignment_weight
        
        # Calculate probabilities
        for assignment in eligible_assignments:
            if total_weight > 0:
                assignment['probability'] = assignment['weight'] / total_weight
            else:
                assignment['probability'] = 0
        
        # Calculate overall expected values
        if eligible_assignments:
            # Weighted average calculations
            expected_gp_per_hour = sum(
                assignment['gp_per_hour'] * assignment['probability'] 
                for assignment in eligible_assignments
            )
            
            avg_gp_per_task = sum(
                assignment['gp_per_task'] * assignment['probability'] 
                for assignment in eligible_assignments
            )
            
            avg_time_per_task = sum(
                assignment['time_per_task_hours'] * assignment['probability'] 
                for assignment in eligible_assignments
            )
            
            tasks_per_hour = 1 / avg_time_per_task if avg_time_per_task > 0 else 0
            
            overall_summary = {
                'expected_gp_per_hour': round(expected_gp_per_hour),
                'avg_gp_per_task': round(avg_gp_per_task),
                'tasks_per_hour': round(tasks_per_hour, 2),
                'available_tasks': len(eligible_assignments),
                'total_possible_tasks': len(master_assignments)
            }
        else:
            overall_summary = {
                'expected_gp_per_hour': 0,
                'avg_gp_per_task': 0,
                'tasks_per_hour': 0,
                'available_tasks': 0,
                'total_possible_tasks': len(master_assignments)
            }
        
        # Sort assignments by GP/hour (descending)
        eligible_assignments.sort(key=lambda x: x['gp_per_hour'], reverse=True)
        
        return {
            'master_name': master_data.get('name', slayer_master_id),
            'master_id': slayer_master_id,
            'user_levels': user_levels,
            'assignments': eligible_assignments,
            'overall': overall_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting Slayer breakdown: {e}")
        return {"error": str(e)} 