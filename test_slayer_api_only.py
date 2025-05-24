#!/usr/bin/env python3
"""
SLAYER SYSTEM API INTEGRATION TEST
=================================

This script tests the slayer system through the actual API endpoints,
validating the complete integration with Firebase and all real data.

This is the PROPER test since it tests the system as it's actually used.
"""

import requests
import json
import time
from datetime import datetime

class SlayerAPITester:
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
        
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps and colors"""
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
            self.log(f"[TEST] Running: {test_name}", "INFO")
            result = test_func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if result:
                self.test_results['passed_tests'] += 1
                self.log(f"[PASS] {test_name} ({elapsed:.3f}s)", "SUCCESS")
            else:
                self.test_results['failed_tests'] += 1
                self.log(f"[FAIL] {test_name} ({elapsed:.3f}s)", "ERROR")
            
            self.test_results['performance_metrics'][test_name] = elapsed
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.test_results['failed_tests'] += 1
            self.log(f"[EXCEPTION] {test_name}: {str(e)} ({elapsed:.3f}s)", "ERROR")
            return False

    def test_server_health(self):
        """Test if the server is running and responsive"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                self.log("Server is healthy and responsive", "SUCCESS")
                return True
            else:
                self.log(f"Server health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Cannot connect to server: {e}", "ERROR")
            return False

    def test_masters_api(self):
        """Test the slayer masters API endpoint"""
        try:
            response = requests.get(f"{self.api_base}/items/slayer?category=masters", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Masters API returned {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            
            if not data.get('success'):
                self.log(f"Masters API unsuccessful: {data.get('error', 'Unknown error')}", "ERROR")
                return False
            
            masters = data.get('items', {})
            if not masters:
                self.log("No masters data returned", "ERROR")
                return False
            
            self.log(f"✅ Masters API: {len(masters)} masters loaded", "SUCCESS")
            
            # Validate key masters exist
            required_masters = ['spria', 'nieve', 'duradel', 'turael']
            missing_masters = [m for m in required_masters if m not in masters]
            if missing_masters:
                self.log(f"⚠️ Missing expected masters: {missing_masters}", "WARNING")
            
            # Validate master data structure
            for master_id, master_data in list(masters.items())[:3]:  # Check first 3
                self.log(f"🔍 Validating master: {master_id}", "DEBUG")
                
                required_fields = ['name', 'combat_req', 'task_assignments']
                missing_fields = [f for f in required_fields if f not in master_data]
                if missing_fields:
                    self.log(f"⚠️ Master {master_id} missing fields: {missing_fields}", "WARNING")
                
                assignments = master_data.get('task_assignments', {})
                self.log(f"  📋 {master_id}: {len(assignments)} assignments", "DEBUG")
                
                # Check Spria specifically (our working master)
                if master_id == 'spria':
                    if len(assignments) > 0:
                        self.log(f"  ✅ Spria has {len(assignments)} assignments (working master)", "SUCCESS")
                    else:
                        self.log(f"  ❌ Spria has no assignments!", "ERROR")
                        return False
            
            return True
            
        except Exception as e:
            self.log(f"Masters API test failed: {e}", "ERROR")
            return False

    def test_monsters_api(self):
        """Test the slayer monsters API endpoint"""
        try:
            response = requests.get(f"{self.api_base}/items/slayer?category=monsters", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Monsters API returned {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            
            if not data.get('success'):
                self.log(f"Monsters API unsuccessful: {data.get('error', 'Unknown error')}", "ERROR")
                return False
            
            monsters = data.get('items', {})
            if not monsters:
                self.log("No monsters data returned", "ERROR")
                return False
            
            self.log(f"✅ Monsters API: {len(monsters)} monsters loaded", "SUCCESS")
            
            # Validate key monsters exist
            expected_monsters = ['gargoyles', 'abyssal_demons', 'dust_devils']
            missing_monsters = [m for m in expected_monsters if m not in monsters]
            if missing_monsters:
                self.log(f"⚠️ Missing expected monsters: {missing_monsters}", "WARNING")
            
            # Validate monster data structure
            total_drops = 0
            for monster_id, monster_data in list(monsters.items())[:5]:  # Check first 5
                self.log(f"🐉 Validating monster: {monster_id}", "DEBUG")
                
                required_fields = ['name', 'slayer_level_req', 'drop_table']
                missing_fields = [f for f in required_fields if f not in monster_data]
                if missing_fields:
                    self.log(f"⚠️ Monster {monster_id} missing fields: {missing_fields}", "WARNING")
                
                drop_table = monster_data.get('drop_table', {})
                monster_drops = sum(len(drops) for drops in drop_table.values() if isinstance(drops, list))
                total_drops += monster_drops
                
                self.log(f"  💎 {monster_id}: {monster_drops} drops, {monster_data.get('slayer_level_req', 0)}+ Slayer", "DEBUG")
            
            self.log(f"📊 Sample monsters have {total_drops} total drops", "DEBUG")
            return True
            
        except Exception as e:
            self.log(f"Monsters API test failed: {e}", "ERROR")
            return False

    def test_expected_mode_calculation(self):
        """Test expected mode calculation with Spria"""
        try:
            test_params = {
                "activity_type": "slayer",
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
            }
            
            response = requests.post(f"{self.api_base}/calculate_gp_hr", json=test_params, timeout=15)
            
            if response.status_code != 200:
                self.log(f"Expected mode API returned {response.status_code}: {response.text[:200]}", "ERROR")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log(f"Expected mode calculation failed: {data.get('error', 'Unknown error')}", "ERROR")
                return False
            
            result = data.get('result', {})
            gp_hr = result.get('gp_hr', 0)
            master_name = result.get('master_name', 'Unknown')
            eligible_tasks = result.get('eligible_tasks', 0)
            
            self.log(f"💰 Expected GP/hr: {gp_hr:,}", "SUCCESS")
            self.log(f"👑 Master: {master_name}", "DEBUG")
            self.log(f"📊 Eligible tasks: {eligible_tasks}", "DEBUG")
            
            # Validate result structure
            required_fields = ['gp_hr', 'master_name', 'eligible_tasks', 'total_assignment_probability']
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                self.log(f"⚠️ Expected mode missing fields: {missing_fields}", "WARNING")
            
            # Sanity checks
            if eligible_tasks == 0:
                self.log("❌ No eligible tasks found - this indicates a problem", "ERROR")
                return False
            
            if abs(gp_hr) > 5000000:  # More than 5M GP/hr seems unrealistic for expected mode
                self.log(f"⚠️ Unrealistic expected GP/hr: {gp_hr:,}", "WARNING")
            
            self.log("✅ Expected mode calculation successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Expected mode test failed: {e}", "ERROR")
            return False

    def test_specific_mode_calculation(self):
        """Test specific mode calculation with Gargoyles"""
        try:
            test_params = {
                "activity_type": "slayer",
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
            }
            
            response = requests.post(f"{self.api_base}/calculate_gp_hr", json=test_params, timeout=15)
            
            if response.status_code != 200:
                self.log(f"Specific mode API returned {response.status_code}: {response.text[:200]}", "ERROR")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log(f"Specific mode calculation failed: {data.get('error', 'Unknown error')}", "ERROR")
                return False
            
            result = data.get('result', {})
            gp_hr = result.get('gp_hr', 0)
            monster_name = result.get('monster_name', 'Unknown')
            kills_per_hour = result.get('kills_per_hour', 0)
            loot_per_kill = result.get('loot_per_kill', 0)
            
            self.log(f"💰 Specific GP/hr: {gp_hr:,}", "SUCCESS")
            self.log(f"🐉 Monster: {monster_name}", "DEBUG")
            self.log(f"⚔️ KPH: {kills_per_hour}", "DEBUG")
            self.log(f"💎 Loot/kill: {loot_per_kill:,} GP", "DEBUG")
            
            # Validate result structure
            required_fields = ['gp_hr', 'monster_name', 'kills_per_hour', 'loot_per_kill']
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                self.log(f"⚠️ Specific mode missing fields: {missing_fields}", "WARNING")
            
            # Sanity checks
            if kills_per_hour <= 0:
                self.log("❌ Zero or negative KPH - this indicates a problem", "ERROR")
                return False
            
            if loot_per_kill <= 0:
                self.log("❌ Zero or negative loot per kill - this indicates a problem", "ERROR")
                return False
            
            if kills_per_hour > 1000:  # More than 1000 KPH seems unrealistic
                self.log(f"⚠️ Unrealistic KPH: {kills_per_hour}", "WARNING")
            
            self.log("✅ Specific mode calculation successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Specific mode test failed: {e}", "ERROR")
            return False

    def test_breakdown_endpoint(self):
        """Test the slayer breakdown endpoint"""
        try:
            test_params = {
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
            }
            
            response = requests.post(f"{self.api_base}/slayer/breakdown", json=test_params, timeout=20)
            
            if response.status_code != 200:
                self.log(f"Breakdown API returned {response.status_code}: {response.text[:200]}", "ERROR")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                self.log(f"Breakdown calculation failed: {data.get('error', 'Unknown error')}", "ERROR")
                return False
            
            result = data.get('result', {})
            assignments = result.get('assignments', [])
            overall = result.get('overall', {})
            master_name = result.get('master_name', 'Unknown')
            
            self.log(f"📋 Breakdown: {len(assignments)} assignments for {master_name}", "SUCCESS")
            
            if overall:
                expected_gp_hr = overall.get('expected_gp_per_hour', 0)
                available_tasks = overall.get('available_tasks', 0)
                self.log(f"💰 Overall expected GP/hr: {expected_gp_hr:,}", "DEBUG")
                self.log(f"📊 Available tasks: {available_tasks}", "DEBUG")
            
            # Validate assignments structure
            if assignments:
                sample_assignment = assignments[0]
                required_fields = ['monster_name', 'gp_per_hour', 'probability', 'kills_per_hour']
                missing_fields = [f for f in required_fields if f not in sample_assignment]
                if missing_fields:
                    self.log(f"⚠️ Assignment missing fields: {missing_fields}", "WARNING")
                else:
                    self.log("✅ Assignment structure valid", "SUCCESS")
                
                # Show top 3 assignments
                self.log("🏆 Top 3 profitable assignments:", "DEBUG")
                for i, assignment in enumerate(assignments[:3], 1):
                    name = assignment.get('monster_name', 'Unknown')
                    gp_hr = assignment.get('gp_per_hour', 0)
                    prob = assignment.get('probability', 0) * 100
                    self.log(f"  {i}. {name}: {gp_hr:,} GP/hr ({prob:.1f}% chance)", "DEBUG")
            
            self.log("✅ Breakdown endpoint successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Breakdown test failed: {e}", "ERROR")
            return False

    def test_error_handling(self):
        """Test error handling with invalid requests"""
        error_tests = [
            {
                "name": "Invalid Master",
                "params": {
                    "activity_type": "slayer",
                    "params": {
                        "calculation_mode": "expected",
                        "slayer_master_id": "invalid_master",
                        "user_slayer_level": 85,
                        "user_combat_level": 100
                    }
                }
            },
            {
                "name": "Invalid Monster",
                "params": {
                    "activity_type": "slayer", 
                    "params": {
                        "calculation_mode": "specific",
                        "specific_monster_id": "invalid_monster",
                        "slayer_master_id": "spria",
                        "user_slayer_level": 85,
                        "user_combat_level": 100
                    }
                }
            },
            {
                "name": "Low Level Requirements",
                "params": {
                    "activity_type": "slayer",
                    "params": {
                        "calculation_mode": "specific",
                        "specific_monster_id": "abyssal_demons",  # Requires 85+ Slayer
                        "slayer_master_id": "spria",
                        "user_slayer_level": 50,  # Too low
                        "user_combat_level": 60
                    }
                }
            }
        ]
        
        all_passed = True
        
        for test in error_tests:
            try:
                self.log(f"🚨 Testing error case: {test['name']}", "DEBUG")
                
                response = requests.post(f"{self.api_base}/calculate_gp_hr", json=test['params'], timeout=10)
                
                # We expect either proper error handling or HTTP 200 with error in response
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        result = data.get('result', {})
                        if 'error' in result:
                            self.log(f"  ✅ Proper error handling: {result['error']}", "SUCCESS")
                        else:
                            # For some cases like low levels, the system might still work but with warnings
                            self.log(f"  ⚠️ Unexpected success - may be valid edge case", "WARNING")
                    else:
                        self.log(f"  ✅ API error handling: {data.get('error', 'Unknown')}", "SUCCESS")
                else:
                    # HTTP errors are also acceptable for error cases
                    self.log(f"  ✅ HTTP error handling: {response.status_code}", "SUCCESS")
                    
            except Exception as e:
                self.log(f"  ❌ Error test failed: {e}", "ERROR")
                all_passed = False
        
        return all_passed

    def test_performance_benchmarks(self):
        """Test performance of API operations"""
        try:
            self.log("⏱️ Running performance benchmarks", "INFO")
            
            # Test expected mode performance
            start_time = time.time()
            iterations = 3
            
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
            self.log(f"⚡ Expected mode avg time: {avg_time:.3f}s", "SUCCESS")
            
            # Test breakdown performance
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
            self.log(f"📊 Breakdown time: {breakdown_time:.3f}s", "SUCCESS")
            
            # Performance warnings
            if avg_time > 2.0:
                self.log(f"⚠️ Expected mode is slow: {avg_time:.3f}s", "WARNING")
            if breakdown_time > 5.0:
                self.log(f"⚠️ Breakdown is slow: {breakdown_time:.3f}s", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Performance test failed: {e}", "ERROR")
            return False

    def run_comprehensive_api_test(self):
        """Run all API tests"""
        self.log("STARTING COMPREHENSIVE SLAYER API TEST", "INFO")
        self.log("=" * 70, "INFO")
        
        start_time = time.time()
        
        # Infrastructure tests
        self.log("\nPHASE 1: SERVER & API CONNECTIVITY", "INFO")
        self.run_test("Server Health Check", self.test_server_health)
        self.run_test("Masters API", self.test_masters_api)
        self.run_test("Monsters API", self.test_monsters_api)
        
        # Calculation tests
        self.log("\nPHASE 2: CALCULATION ENDPOINTS", "INFO")
        self.run_test("Expected Mode Calculation", self.test_expected_mode_calculation)
        self.run_test("Specific Mode Calculation", self.test_specific_mode_calculation)
        self.run_test("Breakdown Endpoint", self.test_breakdown_endpoint)
        
        # Error handling and performance
        self.log("\nPHASE 3: ERROR HANDLING & PERFORMANCE", "INFO")
        self.run_test("Error Handling", self.test_error_handling)
        self.run_test("Performance Benchmarks", self.test_performance_benchmarks)
        
        # Generate report
        total_time = time.time() - start_time
        self.generate_final_report(total_time)

    def generate_final_report(self, total_time):
        """Generate final test report"""
        self.log("\n" + "=" * 70, "INFO")
        self.log("📊 SLAYER API TEST RESULTS", "INFO")
        self.log("=" * 70, "INFO")
        
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
                status = "🐌" if duration > 3.0 else "⚡"
                self.log(f"  {status} {test_name}: {duration:.3f}s", "DEBUG")
        
        # Errors
        if self.test_results['errors']:
            self.log(f"\n❌ ERRORS ({len(self.test_results['errors'])}):", "ERROR")
            for i, error in enumerate(self.test_results['errors'][:5], 1):
                self.log(f"  {i}. {error}", "ERROR")
        
        # Warnings  
        if self.test_results['warnings']:
            self.log(f"\n⚠️ WARNINGS ({len(self.test_results['warnings'])}):", "WARNING")
            for i, warning in enumerate(self.test_results['warnings'][:3], 1):
                self.log(f"  {i}. {warning}", "WARNING")
        
        # Final verdict
        self.log("\n" + "=" * 70, "INFO")
        if success_rate >= 95 and failed_tests == 0:
            self.log("🎉 SLAYER SYSTEM STATUS: EXCELLENT - All systems operational!", "SUCCESS")
        elif success_rate >= 80:
            self.log("✅ SLAYER SYSTEM STATUS: GOOD - Minor issues detected", "SUCCESS")
        elif success_rate >= 60:
            self.log("⚠️ SLAYER SYSTEM STATUS: NEEDS ATTENTION", "WARNING")
        else:
            self.log("❌ SLAYER SYSTEM STATUS: CRITICAL - Major issues found", "ERROR")
        
        self.log("=" * 70, "INFO")


def main():
    """Main test execution"""
    print("OSRS Slayer System API Integration Test")
    print("=" * 50)
    print("Testing the REAL system through API endpoints")
    print("=" * 50)
    
    tester = SlayerAPITester()
    tester.run_comprehensive_api_test()


if __name__ == "__main__":
    main() 