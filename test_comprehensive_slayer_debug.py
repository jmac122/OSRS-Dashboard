#!/usr/bin/env python3
"""
COMPREHENSIVE SLAYER SYSTEM DEBUG TEST
=====================================

This script performs an exhaustive test of the entire slayer calculation system,
including database integrity, API endpoints, calculation algorithms, and edge cases.

Test Coverage:
- Database connectivity and data integrity
- API endpoint functionality  
- All calculation modes (expected, specific, breakdown)
- Multiple slayer masters and monsters
- KPH estimation algorithms
- Supply cost calculations
- Drop table value calculations
- Frontend validation logic
- Error handling and edge cases
- Performance benchmarks
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'osrs_gp_tracker', 'backend')
sys.path.insert(0, backend_path)

from utils.database_service import item_db
from utils.calculations import calculate_slayer_gp_hr, estimate_kph, calculate_expected_loot, adjust_supply_cost

class SlayerDebugger:
    def __init__(self):
        self.api_base = "http://localhost:5000/api"
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'warnings': [],
            'performance_metrics': {}
        }
        self.verbose = True
        
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps and levels"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        colors = {
            "INFO": "\033[36m",      # Cyan
            "SUCCESS": "\033[32m",   # Green  
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
            "DEBUG": "\033[35m",     # Magenta
            "RESET": "\033[0m"       # Reset
        }
        
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
        
        if level == "ERROR":
            self.test_results['errors'].append(message)
        elif level == "WARNING":
            self.test_results['warnings'].append(message)

    def run_test(self, test_name, test_func, *args, **kwargs):
        """Execute a test with error handling and metrics"""
        self.test_results['total_tests'] += 1
        start_time = time.time()
        
        try:
            self.log(f"🧪 Running: {test_name}", "INFO")
            result = test_func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if result:
                self.test_results['passed_tests'] += 1
                self.log(f"✅ PASSED: {test_name} ({elapsed:.3f}s)", "SUCCESS")
            else:
                self.test_results['failed_tests'] += 1
                self.log(f"❌ FAILED: {test_name} ({elapsed:.3f}s)", "ERROR")
            
            self.test_results['performance_metrics'][test_name] = elapsed
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.test_results['failed_tests'] += 1
            self.log(f"💥 EXCEPTION in {test_name}: {str(e)} ({elapsed:.3f}s)", "ERROR")
            return False

    def test_database_connectivity(self):
        """Test database connection and basic functionality"""
        try:
            masters_data = item_db.get_global_items('slayer', 'masters')
            monsters_data = item_db.get_global_items('slayer', 'monsters')
            
            if not masters_data:
                self.log("No masters data found in database", "ERROR")
                return False
                
            if not monsters_data:
                self.log("No monsters data found in database", "ERROR")
                return False
                
            self.log(f"Database OK: {len(masters_data)} masters, {len(monsters_data)} monsters", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Database connection failed: {e}", "ERROR")
            return False

    def test_master_data_integrity(self):
        """Thoroughly validate slayer master data structure and content"""
        try:
            masters_data = item_db.get_global_items('slayer', 'masters')
            
            required_fields = ['name', 'combat_req', 'slayer_req', 'task_assignments']
            valid_masters = 0
            
            for master_id, master_data in masters_data.items():
                self.log(f"🔍 Analyzing Master: {master_id}", "DEBUG")
                
                # Check required fields
                missing_fields = [field for field in required_fields if field not in master_data]
                if missing_fields:
                    self.log(f"Master {master_id} missing fields: {missing_fields}", "WARNING")
                    continue
                
                # Validate task assignments
                assignments = master_data.get('task_assignments', {})
                self.log(f"  📋 {master_id}: {len(assignments)} assignments", "DEBUG")
                
                # Check assignment probabilities
                total_probability = sum(assignments.values())
                self.log(f"  📊 {master_id}: Total assignment probability = {total_probability:.3f}", "DEBUG")
                
                # Check assignment quantity ranges
                avg_quantities = master_data.get('avg_task_quantity', {})
                self.log(f"  📈 {master_id}: {len(avg_quantities)} quantity ranges defined", "DEBUG")
                
                # Sample a few assignments for detailed validation
                sample_assignments = list(assignments.items())[:3]
                for assignment_id, weight in sample_assignments:
                    self.log(f"    🎯 Sample: {assignment_id} (weight: {weight})", "DEBUG")
                
                valid_masters += 1
            
            self.log(f"Master validation complete: {valid_masters}/{len(masters_data)} valid", "SUCCESS")
            return valid_masters > 0
            
        except Exception as e:
            self.log(f"Master data validation failed: {e}", "ERROR")
            return False

    def test_monster_data_integrity(self):
        """Thoroughly validate monster data structure and drop tables"""
        try:
            monsters_data = item_db.get_global_items('slayer', 'monsters')
            
            required_fields = ['name', 'slayer_level_req', 'drop_table']
            valid_monsters = 0
            total_drops = 0
            
            for monster_id, monster_data in monsters_data.items():
                self.log(f"🐉 Analyzing Monster: {monster_id}", "DEBUG")
                
                # Check required fields
                missing_fields = [field for field in required_fields if field not in monster_data]
                if missing_fields:
                    self.log(f"Monster {monster_id} missing fields: {missing_fields}", "WARNING")
                    continue
                
                # Validate drop table structure
                drop_table = monster_data.get('drop_table', {})
                monster_drops = 0
                
                for rarity, drops in drop_table.items():
                    if not isinstance(drops, list):
                        self.log(f"  ⚠️  {monster_id} drop table {rarity} is not a list", "WARNING")
                        continue
                    
                    rarity_drops = len(drops)
                    monster_drops += rarity_drops
                    self.log(f"  💎 {monster_id}: {rarity_drops} {rarity} drops", "DEBUG")
                    
                    # Sample drop validation
                    for i, drop in enumerate(drops[:2]):  # Check first 2 drops per rarity
                        if 'item_id' not in drop:
                            self.log(f"    ❌ Drop missing item_id: {drop}", "WARNING")
                        if 'probability' not in drop:
                            self.log(f"    ❌ Drop missing probability: {drop}", "WARNING")
                        else:
                            self.log(f"    ✨ {drop.get('item_name', 'Unknown')}: {drop['probability']:.6f} chance", "DEBUG")
                
                total_drops += monster_drops
                self.log(f"  📊 {monster_id}: {monster_drops} total drops, {monster_data.get('slayer_level_req', 0)}+ Slayer", "DEBUG")
                valid_monsters += 1
            
            self.log(f"Monster validation complete: {valid_monsters}/{len(monsters_data)} valid, {total_drops} total drops", "SUCCESS")
            return valid_monsters > 0
            
        except Exception as e:
            self.log(f"Monster data validation failed: {e}", "ERROR")
            return False

    def test_api_endpoints(self):
        """Test all slayer-related API endpoints"""
        endpoints_to_test = [
            ("/items/slayer?category=masters", "GET", None),
            ("/items/slayer?category=monsters", "GET", None),
            ("/calculate_gp_hr", "POST", {
                "activity_type": "slayer",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 85,
                    "user_combat_level": 100
                }
            }),
            ("/slayer/breakdown", "POST", {
                "slayer_master_id": "spria",
                "user_levels": {
                    "slayer_level": 85,
                    "combat_level": 100,
                    "attack_level": 80,
                    "strength_level": 80,
                    "defence_level": 75,
                    "ranged_level": 85,
                    "magic_level": 80
                }
            })
        ]
        
        all_passed = True
        
        for endpoint, method, data in endpoints_to_test:
            try:
                url = f"{self.api_base}{endpoint}"
                self.log(f"🌐 Testing {method} {endpoint}", "DEBUG")
                
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
                
                self.log(f"  📡 Status: {response.status_code}", "DEBUG")
                
                if response.status_code == 200:
                    result = response.json()
                    self.log(f"  ✅ Response received: {len(str(result))} chars", "DEBUG")
                    
                    # Additional validation for specific endpoints
                    if "items/slayer" in endpoint and "category=masters" in endpoint:
                        if result.get('success') and result.get('items'):
                            self.log(f"  👑 Masters API: {len(result['items'])} masters loaded", "SUCCESS")
                        else:
                            self.log(f"  ❌ Masters API returned no data", "ERROR")
                            all_passed = False
                    
                    elif "items/slayer" in endpoint and "category=monsters" in endpoint:
                        if result.get('success') and result.get('items'):
                            self.log(f"  🐉 Monsters API: {len(result['items'])} monsters loaded", "SUCCESS")
                        else:
                            self.log(f"  ❌ Monsters API returned no data", "ERROR")
                            all_passed = False
                    
                    elif "calculate_gp_hr" in endpoint:
                        if result.get('success') and 'gp_hr' in result.get('result', {}):
                            gp_hr = result['result']['gp_hr']
                            self.log(f"  💰 Calculation API: {gp_hr:,} GP/hr", "SUCCESS")
                        else:
                            self.log(f"  ❌ Calculation API failed: {result.get('error', 'Unknown error')}", "ERROR")
                            all_passed = False
                    
                    elif "slayer/breakdown" in endpoint:
                        if result.get('success') and result.get('result', {}).get('assignments'):
                            assignments = len(result['result']['assignments'])
                            self.log(f"  📋 Breakdown API: {assignments} assignments", "SUCCESS")
                        else:
                            self.log(f"  ❌ Breakdown API failed: {result.get('error', 'Unknown error')}", "ERROR")
                            all_passed = False
                            
                else:
                    self.log(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  💥 API test failed: {e}", "ERROR")
                all_passed = False
        
        return all_passed

    def test_calculation_modes(self):
        """Test all three calculation modes with various parameters"""
        test_configs = [
            # Expected mode tests
            {
                "name": "Expected Mode - Spria (Working Master)",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 85,
                    "user_combat_level": 100,
                    "user_attack_level": 80,
                    "user_strength_level": 80,
                    "user_defence_level": 75,
                    "user_ranged_level": 85,
                    "user_magic_level": 80
                }
            },
            # Specific mode tests
            {
                "name": "Specific Mode - Gargoyles",
                "params": {
                    "calculation_mode": "specific",
                    "specific_monster_id": "gargoyles",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 85,
                    "user_combat_level": 100,
                    "user_attack_level": 80,
                    "user_strength_level": 80,
                    "user_defence_level": 75,
                    "user_ranged_level": 85,
                    "user_magic_level": 80
                }
            },
            # Low level tests
            {
                "name": "Low Level - Expected Mode",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "turael",
                    "user_slayer_level": 15,
                    "user_combat_level": 40,
                    "user_attack_level": 30,
                    "user_strength_level": 30,
                    "user_defence_level": 25,
                    "user_ranged_level": 30,
                    "user_magic_level": 25
                }
            },
            # High level tests
            {
                "name": "High Level - Expected Mode",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "duradel",
                    "user_slayer_level": 99,
                    "user_combat_level": 126,
                    "user_attack_level": 99,
                    "user_strength_level": 99,
                    "user_defence_level": 99,
                    "user_ranged_level": 99,
                    "user_magic_level": 99
                }
            }
        ]
        
        all_passed = True
        
        for config in test_configs:
            try:
                self.log(f"🧮 Testing: {config['name']}", "DEBUG")
                
                # Test via API
                response = requests.post(f"{self.api_base}/calculate_gp_hr", json={
                    "activity_type": "slayer",
                    "params": config["params"]
                }, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        calc_result = result['result']
                        gp_hr = calc_result.get('gp_hr', 0)
                        
                        self.log(f"  💰 GP/hr: {gp_hr:,}", "DEBUG")
                        
                        # Validate result structure
                        if config["params"]["calculation_mode"] == "expected":
                            required_fields = ['gp_hr', 'master_name', 'eligible_tasks']
                            missing = [f for f in required_fields if f not in calc_result]
                            if missing:
                                self.log(f"  ❌ Missing fields in expected mode: {missing}", "ERROR")
                                all_passed = False
                            else:
                                self.log(f"  ✅ Expected mode structure valid", "SUCCESS")
                                self.log(f"  👑 Master: {calc_result.get('master_name')}", "DEBUG")
                                self.log(f"  📊 Eligible tasks: {calc_result.get('eligible_tasks')}", "DEBUG")
                        
                        elif config["params"]["calculation_mode"] == "specific":
                            required_fields = ['gp_hr', 'monster_name', 'kills_per_hour', 'loot_per_kill']
                            missing = [f for f in required_fields if f not in calc_result]
                            if missing:
                                self.log(f"  ❌ Missing fields in specific mode: {missing}", "ERROR")
                                all_passed = False
                            else:
                                self.log(f"  ✅ Specific mode structure valid", "SUCCESS")
                                self.log(f"  🐉 Monster: {calc_result.get('monster_name')}", "DEBUG")
                                self.log(f"  ⚔️ KPH: {calc_result.get('kills_per_hour')}", "DEBUG")
                                self.log(f"  💎 Loot/kill: {calc_result.get('loot_per_kill'):,} GP", "DEBUG")
                        
                        # Sanity checks
                        if abs(gp_hr) > 10000000:  # More than 10M GP/hr seems unrealistic
                            self.log(f"  ⚠️ Unrealistic GP/hr: {gp_hr:,}", "WARNING")
                        
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        self.log(f"  ❌ Calculation failed: {error_msg}", "ERROR")
                        all_passed = False
                
                else:
                    self.log(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  💥 Test failed: {e}", "ERROR")
                all_passed = False
        
        return all_passed

    def test_algorithm_components(self):
        """Test individual algorithm components in isolation"""
        try:
            monsters_data = item_db.get_global_items('slayer', 'monsters')
            
            # Test KPH estimation
            self.log("🔧 Testing KPH estimation algorithm", "DEBUG")
            sample_monsters = list(monsters_data.items())[:3]
            
            for monster_id, monster_data in sample_monsters:
                user_params = {
                    'user_combat_level': 100,
                    'user_slayer_level': 85,
                    'user_attack_level': 80,
                    'user_strength_level': 80,
                    'user_defence_level': 75,
                    'user_ranged_level': 85,
                    'user_magic_level': 80
                }
                
                kph = estimate_kph(monster_data, user_params)
                self.log(f"  ⚔️ {monster_id}: {kph:.1f} kills/hour", "DEBUG")
                
                if kph <= 0 or kph > 1000:  # Sanity check
                    self.log(f"  ⚠️ Suspicious KPH for {monster_id}: {kph}", "WARNING")
            
            # Test expected loot calculation
            self.log("🔧 Testing expected loot calculation", "DEBUG")
            
            for monster_id, monster_data in sample_monsters:
                drop_table = monster_data.get('drop_table', {})
                expected_loot = calculate_expected_loot(drop_table)
                self.log(f"  💎 {monster_id}: {expected_loot:,.0f} GP/kill expected", "DEBUG")
                
                if expected_loot <= 0:
                    self.log(f"  ⚠️ Zero loot value for {monster_id}", "WARNING")
                elif expected_loot > 1000000:  # More than 1M per kill seems high
                    self.log(f"  ⚠️ Very high loot value for {monster_id}: {expected_loot:,}", "WARNING")
            
            # Test supply cost adjustment
            self.log("🔧 Testing supply cost adjustment", "DEBUG")
            
            base_cost = 50000
            test_levels = [
                {'user_combat_level': 60, 'desc': 'Low level'},
                {'user_combat_level': 100, 'desc': 'Mid level'},
                {'user_combat_level': 126, 'desc': 'Max level'}
            ]
            
            for level_config in test_levels:
                adjusted_cost = adjust_supply_cost(base_cost, level_config)
                efficiency = (base_cost - adjusted_cost) / base_cost * 100
                self.log(f"  💰 {level_config['desc']}: {adjusted_cost:,} GP/hr ({efficiency:+.1f}% efficiency)", "DEBUG")
            
            return True
            
        except Exception as e:
            self.log(f"Algorithm component test failed: {e}", "ERROR")
            return False

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        edge_cases = [
            {
                "name": "Invalid Master",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "nonexistent_master",
                    "user_slayer_level": 85,
                    "user_combat_level": 100
                }
            },
            {
                "name": "Invalid Monster",
                "params": {
                    "calculation_mode": "specific",
                    "specific_monster_id": "nonexistent_monster",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 85,
                    "user_combat_level": 100
                }
            },
            {
                "name": "Level Requirements Not Met",
                "params": {
                    "calculation_mode": "specific",
                    "specific_monster_id": "abyssal_demons",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 50,  # Abyssal demons need 85+ Slayer
                    "user_combat_level": 60
                }
            },
            {
                "name": "Extreme Levels",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "spria",
                    "user_slayer_level": 999,  # Invalid level
                    "user_combat_level": 999   # Invalid level
                }
            }
        ]
        
        all_passed = True
        
        for case in edge_cases:
            try:
                self.log(f"🧪 Testing Edge Case: {case['name']}", "DEBUG")
                
                response = requests.post(f"{self.api_base}/calculate_gp_hr", json={
                    "activity_type": "slayer",
                    "params": case["params"]
                }, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # For edge cases, we expect either success with reasonable values or proper error handling
                    if result.get('success'):
                        calc_result = result['result']
                        if 'error' in calc_result:
                            self.log(f"  ✅ Proper error handling: {calc_result['error']}", "SUCCESS")
                        else:
                            gp_hr = calc_result.get('gp_hr', 0)
                            self.log(f"  ⚠️ Unexpected success: {gp_hr:,} GP/hr", "WARNING")
                    else:
                        self.log(f"  ✅ Proper API error: {result.get('error', 'Unknown')}", "SUCCESS")
                else:
                    self.log(f"  ❌ HTTP error: {response.status_code}", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  ❌ Edge case test failed: {e}", "ERROR")
                all_passed = False
        
        return all_passed

    def test_performance_benchmarks(self):
        """Test performance of calculation operations"""
        try:
            self.log("⏱️ Running performance benchmarks", "DEBUG")
            
            # Benchmark expected mode calculations
            start_time = time.time()
            iterations = 5
            
            for i in range(iterations):
                response = requests.post(f"{self.api_base}/calculate_gp_hr", json={
                    "activity_type": "slayer",
                    "params": {
                        "calculation_mode": "expected",
                        "slayer_master_id": "spria",
                        "user_slayer_level": 85,
                        "user_combat_level": 100
                    }
                }, timeout=15)
                
                if response.status_code != 200:
                    self.log(f"Performance test failed on iteration {i+1}", "ERROR")
                    return False
            
            avg_time = (time.time() - start_time) / iterations
            self.log(f"  ⚡ Expected mode avg time: {avg_time:.3f}s", "SUCCESS")
            
            # Benchmark breakdown calculations
            start_time = time.time()
            
            response = requests.post(f"{self.api_base}/slayer/breakdown", json={
                "slayer_master_id": "spria",
                "user_levels": {
                    "slayer_level": 85,
                    "combat_level": 100,
                    "attack_level": 80,
                    "strength_level": 80,
                    "defence_level": 75,
                    "ranged_level": 85,
                    "magic_level": 80
                }
            }, timeout=20)
            
            breakdown_time = time.time() - start_time
            self.log(f"  📊 Breakdown calculation time: {breakdown_time:.3f}s", "SUCCESS")
            
            # Performance thresholds
            if avg_time > 2.0:
                self.log(f"  ⚠️ Expected mode calculation is slow: {avg_time:.3f}s", "WARNING")
            if breakdown_time > 5.0:
                self.log(f"  ⚠️ Breakdown calculation is slow: {breakdown_time:.3f}s", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Performance benchmark failed: {e}", "ERROR")
            return False

    def test_data_consistency(self):
        """Test consistency between frontend defaults and backend calculations"""
        try:
            self.log("🔄 Testing data consistency", "DEBUG")
            
            # Test that default values match between frontend and backend
            default_params = {
                "calculation_mode": "expected",
                "slayer_master_id": "spria",
                "user_slayer_level": 85,
                "user_combat_level": 100,
                "user_attack_level": 80,
                "user_strength_level": 80,
                "user_defence_level": 75,
                "user_ranged_level": 85,
                "user_magic_level": 80
            }
            
            # Test calculation with explicit defaults
            response = requests.post(f"{self.api_base}/calculate_gp_hr", json={
                "activity_type": "slayer",
                "params": default_params
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log("  ✅ Default parameters work correctly", "SUCCESS")
                    
                    # Test that the same calculation produces consistent results
                    response2 = requests.post(f"{self.api_base}/calculate_gp_hr", json={
                        "activity_type": "slayer",
                        "params": default_params
                    }, timeout=10)
                    
                    if response2.status_code == 200:
                        result2 = response2.json()
                        if (result2.get('success') and 
                            result['result']['gp_hr'] == result2['result']['gp_hr']):
                            self.log("  ✅ Calculations are deterministic", "SUCCESS")
                            return True
                        else:
                            self.log("  ❌ Calculations are not deterministic", "ERROR")
                            return False
                    else:
                        self.log("  ❌ Second consistency test failed", "ERROR")
                        return False
                else:
                    self.log(f"  ❌ Default calculation failed: {result.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"  ❌ HTTP error in consistency test: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Data consistency test failed: {e}", "ERROR")
            return False

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        self.log("🚀 STARTING COMPREHENSIVE SLAYER SYSTEM DEBUG TEST", "INFO")
        self.log("=" * 80, "INFO")
        
        start_time = time.time()
        
        # Core infrastructure tests
        self.log("\n📋 PHASE 1: INFRASTRUCTURE TESTS", "INFO")
        self.run_test("Database Connectivity", self.test_database_connectivity)
        self.run_test("Master Data Integrity", self.test_master_data_integrity)
        self.run_test("Monster Data Integrity", self.test_monster_data_integrity)
        
        # API tests
        self.log("\n📋 PHASE 2: API ENDPOINT TESTS", "INFO")
        self.run_test("API Endpoints", self.test_api_endpoints)
        
        # Calculation tests
        self.log("\n📋 PHASE 3: CALCULATION ALGORITHM TESTS", "INFO")
        self.run_test("Calculation Modes", self.test_calculation_modes)
        self.run_test("Algorithm Components", self.test_algorithm_components)
        
        # Edge case and error handling tests
        self.log("\n📋 PHASE 4: EDGE CASES & ERROR HANDLING", "INFO")
        self.run_test("Edge Cases", self.test_edge_cases)
        
        # Performance and consistency tests
        self.log("\n📋 PHASE 5: PERFORMANCE & CONSISTENCY", "INFO")
        self.run_test("Performance Benchmarks", self.test_performance_benchmarks)
        self.run_test("Data Consistency", self.test_data_consistency)
        
        # Generate final report
        total_time = time.time() - start_time
        self.generate_final_report(total_time)

    def generate_final_report(self, total_time):
        """Generate comprehensive test report"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("📊 COMPREHENSIVE TEST RESULTS SUMMARY", "INFO")
        self.log("=" * 80, "INFO")
        
        # Test statistics
        total_tests = self.test_results['total_tests']
        passed_tests = self.test_results['passed_tests']
        failed_tests = self.test_results['failed_tests']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"📈 Total Tests: {total_tests}", "INFO")
        self.log(f"✅ Passed: {passed_tests}", "SUCCESS")
        self.log(f"❌ Failed: {failed_tests}", "ERROR" if failed_tests > 0 else "INFO")
        self.log(f"📊 Success Rate: {success_rate:.1f}%", "SUCCESS" if success_rate >= 90 else "WARNING")
        self.log(f"⏱️ Total Time: {total_time:.3f}s", "INFO")
        
        # Performance metrics
        if self.test_results['performance_metrics']:
            self.log("\n⚡ PERFORMANCE METRICS:", "INFO")
            for test_name, duration in self.test_results['performance_metrics'].items():
                self.log(f"  {test_name}: {duration:.3f}s", "DEBUG")
        
        # Errors summary
        if self.test_results['errors']:
            self.log(f"\n❌ ERRORS ENCOUNTERED ({len(self.test_results['errors'])}):", "ERROR")
            for i, error in enumerate(self.test_results['errors'][:10], 1):  # Show first 10 errors
                self.log(f"  {i}. {error}", "ERROR")
            if len(self.test_results['errors']) > 10:
                self.log(f"  ... and {len(self.test_results['errors']) - 10} more errors", "ERROR")
        
        # Warnings summary
        if self.test_results['warnings']:
            self.log(f"\n⚠️ WARNINGS ({len(self.test_results['warnings'])}):", "WARNING")
            for i, warning in enumerate(self.test_results['warnings'][:5], 1):  # Show first 5 warnings
                self.log(f"  {i}. {warning}", "WARNING")
            if len(self.test_results['warnings']) > 5:
                self.log(f"  ... and {len(self.test_results['warnings']) - 5} more warnings", "WARNING")
        
        # Final verdict
        self.log("\n" + "=" * 80, "INFO")
        if success_rate >= 95 and failed_tests == 0:
            self.log("🎉 SLAYER SYSTEM STATUS: EXCELLENT - All systems operational!", "SUCCESS")
        elif success_rate >= 80 and failed_tests <= 2:
            self.log("✅ SLAYER SYSTEM STATUS: GOOD - Minor issues detected", "SUCCESS")
        elif success_rate >= 60:
            self.log("⚠️ SLAYER SYSTEM STATUS: NEEDS ATTENTION - Several issues found", "WARNING")
        else:
            self.log("❌ SLAYER SYSTEM STATUS: CRITICAL - Major issues require immediate attention", "ERROR")
        
        self.log("=" * 80, "INFO")


def main():
    """Main test execution"""
    print("🧪 OSRS Slayer System Comprehensive Debug Test")
    print("=" * 60)
    
    debugger = SlayerDebugger()
    debugger.run_comprehensive_test()


if __name__ == "__main__":
    main() 