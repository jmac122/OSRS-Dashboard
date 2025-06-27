# Configuration settings for the OSRS GP Tracker backend

# Default configurations for new users or when user-specific config is not found.
# These were previously in app.py's DEFAULT_USER_CONFIG and get_default_config() endpoint.
# Consolidating them here. Note that there were slight differences, this version aims
# to be the single source of truth. Frontend or specific features might override these.

DEFAULT_FARMING_CONFIG = {
    "num_patches": 9,
    "avg_yield_per_patch": 8,
    "growth_time_minutes": 80,
    "herb_id": 207,  # Grimy Torstol (was Ranarr weed in one default, Torstol in another) - Standardizing to Torstol for now
    "seed_id": 5309,  # Torstol Seed (was Ranarr seed in one default)
    "compost_id": 21483  # Ultracompost
}

DEFAULT_BIRDHOUSE_CONFIG = {
    "num_birdhouses": 4,
    "run_time_minutes": 5,
    "cycle_time_minutes": 50,
    "log_id": 19669,  # Redwood logs
    "seed_id": 5318,  # Potato seed
    "seeds_per_house": 10,
    "avg_nests_per_run": 10,
    "avg_value_per_nest": 5000 # This is a simplified average, actual value varies
}

DEFAULT_GOTR_CONFIG = {
    "games_per_hour": 4,
    "avg_points_per_game": 350, # This might be better estimated or user-defined
    "essence_per_game": 150,
    "essence_id": 7936,  # Pure essence
    "avg_rune_value_per_game": 15000,  # Highly variable, placeholder
    "avg_pearl_value_per_game": 8000   # Highly variable, placeholder
}

DEFAULT_SLAYER_CONFIG = {
    # Note: Slayer defaults are more complex and often depend on master/task.
    # This is a very generic placeholder if no specific task is chosen.
    "calculation_mode": "expected", # 'expected', 'specific', 'breakdown'
    "slayer_master_id": "nieve", # A common high-level master
    "specific_monster_id": "gargoyles", # Placeholder for specific mode
    "user_slayer_level": 85,
    "user_combat_level": 100,
    "user_attack_level": 80,
    "user_strength_level": 80,
    "user_defence_level": 75,
    "user_ranged_level": 85,
    "user_magic_level": 80,
    # Old simpler slayer defaults (can be removed if new structure is preferred)
    # "monster_name": "Rune Dragons", # This was from the old DEFAULT_USER_CONFIG
    # "kills_per_hour": 40,
    # "avg_loot_value_per_kill": 37000,
    # "avg_supply_cost_per_hour": 100000
}

# Combined default configuration for all activities
# This structure is often used when initializing a new user's complete config document.
DEFAULT_USER_CONFIG_ALL_ACTIVITIES = {
    "farming": DEFAULT_FARMING_CONFIG,
    "birdhouse": DEFAULT_BIRDHOUSE_CONFIG,
    "gotr": DEFAULT_GOTR_CONFIG,
    "slayer": DEFAULT_SLAYER_CONFIG
    # Add other activities here as they are developed
}
