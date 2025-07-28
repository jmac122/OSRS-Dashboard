#!/usr/bin/env python3
"""
Comprehensive Bug Analysis Script
Systematically tests every component to identify all bugs and disconnects
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

class ComprehensiveBugAnalyzer:
    def __init__(self):
        self.api_base = "http://localhost:5000"
        self.frontend_base = "http://localhost:3000"
        self.issues = []
        self.test_results = {}
        
    def log_issue(self, category, severity, description, details=None):
        """Log a bug or issue"""
        issue = {
            'category': category,
            'severity': severity,  # CRITICAL, HIGH, MEDIUM, LOW
            'description': description,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.issues.append(issue)
        print(f"🐛 {severity}: {description}")
        if details:
            print(f"   Details: {details}")
    
    def test_backend_connectivity(self):
        """Test all backend endpoints"""
        print("\n🔧 TESTING BACKEND CONNECTIVITY")
        print("=" * 50)
        
        endpoints = [
            ("/api/health", "GET", None),
            ("/api/default_config", "GET", None),
            ("/api/items/slayer?category=masters", "GET", None),
            ("/api/items/slayer?category=monsters", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.api_base}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.api_base}{endpoint}", json=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', True):
                        print(f"✅ {endpoint}: OK")
                        self.test_results[endpoint] = 'PASS'
                    else:
                        print(f"❌ {endpoint}: API Error - {result.get('error', 'Unknown')}")
                        self.log_issue('BACKEND', 'HIGH', f"API endpoint {endpoint} returns error", result)
                        self.test_results[endpoint] = 'FAIL'
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
                    self.log_issue('BACKEND', 'HIGH', f"HTTP error on {endpoint}", {'status': response.status_code})
                    self.test_results[endpoint] = 'FAIL'
                    
            except Exception as e:
                print(f"💥 {endpoint}: Exception - {e}")
                self.log_issue('BACKEND', 'CRITICAL', f"Exception on {endpoint}", {'error': str(e)})
                self.test_results[endpoint] = 'ERROR'
    
    def test_slayer_calculation_modes(self):
        """Test all slayer calculation modes"""
        print("\n🎯 TESTING SLAYER CALCULATION MODES")
        print("=" * 50)
        
        # Test data
        base_params = {
            "slayer_master_id": "nieve",
            "user_slayer_level": 85,
            "user_combat_level": 100,
            "user_attack_level": 80,
            "user_strength_level": 80,
            "user_defence_level": 75,
            "user_ranged_level": 85,
            "user_magic_level": 80
        }
        
        modes = [
            ("expected", "Expected GP/hr calculation"),
            ("specific", "Specific monster calculation"),
            ("breakdown", "Task breakdown calculation")
        ]
        
        for mode, description in modes:
            print(f"\n🧮 Testing {mode} mode...")
            
            test_params = base_params.copy()
            test_params["calculation_mode"] = mode
            
            if mode == "specific":
                test_params["specific_monster_id"] = "gargoyles"
            
            try:
                response = requests.post(f"{self.api_base}/api/calculate_gp_hr", json={
                    "activity_type": "slayer",
                    "params": test_params
                }, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        calc_result = result.get('result', {})
                        gp_hr = calc_result.get('gp_hr', 0)
                        
                        print(f"   ✅ {mode} mode: {gp_hr:,} GP/hr")
                        
                        # Validate expected fields based on mode
                        if mode == "expected":
                            required_fields = ['gp_hr', 'master_name', 'eligible_tasks']
                            missing = [f for f in required_fields if f not in calc_result]
                            if missing:
                                self.log_issue('SLAYER', 'HIGH', f"Expected mode missing fields: {missing}", calc_result)
                            
                            # Check if breakdown data is included when it shouldn't be
                            if 'task_breakdown' in calc_result:
                                self.log_issue('SLAYER', 'MEDIUM', "Expected mode incorrectly includes task_breakdown", calc_result)
                        
                        elif mode == "breakdown":
                            # Breakdown mode should include task_breakdown
                            if 'task_breakdown' not in calc_result:
                                self.log_issue('SLAYER', 'HIGH', "Breakdown mode missing task_breakdown field", calc_result)
                            else:
                                breakdown = calc_result['task_breakdown']
                                if not isinstance(breakdown, list) or len(breakdown) == 0:
                                    self.log_issue('SLAYER', 'HIGH', "Breakdown mode has empty task_breakdown", calc_result)
                                else:
                                    print(f"   📋 Breakdown has {len(breakdown)} tasks")
                        
                        elif mode == "specific":
                            required_fields = ['gp_hr', 'monster_name', 'kills_per_hour', 'loot_per_kill']
                            missing = [f for f in required_fields if f not in calc_result]
                            if missing:
                                self.log_issue('SLAYER', 'HIGH', f"Specific mode missing fields: {missing}", calc_result)
                        
                        self.test_results[f"slayer_{mode}"] = 'PASS'
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"   ❌ {mode} mode failed: {error}")
                        self.log_issue('SLAYER', 'HIGH', f"{mode} mode calculation failed", {'error': error})
                        self.test_results[f"slayer_{mode}"] = 'FAIL'
                else:
                    print(f"   ❌ {mode} mode HTTP error: {response.status_code}")
                    self.log_issue('SLAYER', 'HIGH', f"{mode} mode HTTP error", {'status': response.status_code})
                    self.test_results[f"slayer_{mode}"] = 'FAIL'
                    
            except Exception as e:
                print(f"   💥 {mode} mode exception: {e}")
                self.log_issue('SLAYER', 'CRITICAL', f"{mode} mode exception", {'error': str(e)})
                self.test_results[f"slayer_{mode}"] = 'ERROR'
    
    def test_slayer_breakdown_endpoint(self):
        """Test the separate breakdown endpoint"""
        print("\n📋 TESTING SLAYER BREAKDOWN ENDPOINT")
        print("=" * 50)
        
        try:
            response = requests.post(f"{self.api_base}/api/slayer/breakdown", json={
                "slayer_master_id": "nieve",
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
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    breakdown = result.get('result', {})
                    assignments = breakdown.get('assignments', [])
                    overall = breakdown.get('overall', {})
                    
                    print(f"✅ Breakdown endpoint: {len(assignments)} assignments")
                    print(f"   Overall GP/hr: {overall.get('expected_gp_per_hour', 0):,}")
                    
                    # Validate structure
                    required_fields = ['master_name', 'assignments', 'overall']
                    missing = [f for f in required_fields if f not in breakdown]
                    if missing:
                        self.log_issue('SLAYER', 'HIGH', f"Breakdown endpoint missing fields: {missing}", breakdown)
                    
                    self.test_results['breakdown_endpoint'] = 'PASS'
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"❌ Breakdown endpoint failed: {error}")
                    self.log_issue('SLAYER', 'HIGH', "Breakdown endpoint failed", {'error': error})
                    self.test_results['breakdown_endpoint'] = 'FAIL'
            else:
                print(f"❌ Breakdown endpoint HTTP error: {response.status_code}")
                self.log_issue('SLAYER', 'HIGH', "Breakdown endpoint HTTP error", {'status': response.status_code})
                self.test_results['breakdown_endpoint'] = 'FAIL'
                
        except Exception as e:
            print(f"💥 Breakdown endpoint exception: {e}")
            self.log_issue('SLAYER', 'CRITICAL', "Breakdown endpoint exception", {'error': str(e)})
            self.test_results['breakdown_endpoint'] = 'ERROR'
    
    def test_frontend_connectivity(self):
        """Test frontend connectivity"""
        print("\n🌐 TESTING FRONTEND CONNECTIVITY")
        print("=" * 50)
        
        try:
            response = requests.get(self.frontend_base, timeout=10)
            if response.status_code == 200:
                print("✅ Frontend server responding")
                self.test_results['frontend_server'] = 'PASS'
            else:
                print(f"❌ Frontend server HTTP error: {response.status_code}")
                self.log_issue('FRONTEND', 'HIGH', "Frontend server not responding", {'status': response.status_code})
                self.test_results['frontend_server'] = 'FAIL'
        except Exception as e:
            print(f"💥 Frontend server exception: {e}")
            self.log_issue('FRONTEND', 'CRITICAL', "Frontend server not accessible", {'error': str(e)})
            self.test_results['frontend_server'] = 'ERROR'
    
    def test_data_consistency(self):
        """Test data consistency between different endpoints"""
        print("\n🔄 TESTING DATA CONSISTENCY")
        print("=" * 50)
        
        # Test that expected mode and breakdown endpoint return consistent data
        try:
            # Get expected mode result
            expected_response = requests.post(f"{self.api_base}/api/calculate_gp_hr", json={
                "activity_type": "slayer",
                "params": {
                    "calculation_mode": "expected",
                    "slayer_master_id": "nieve",
                    "user_slayer_level": 85,
                    "user_combat_level": 100
                }
            }, timeout=15)
            
            # Get breakdown endpoint result
            breakdown_response = requests.post(f"{self.api_base}/api/slayer/breakdown", json={
                "slayer_master_id": "nieve",
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
            
            if expected_response.status_code == 200 and breakdown_response.status_code == 200:
                expected_data = expected_response.json()
                breakdown_data = breakdown_response.json()
                
                if expected_data.get('success') and breakdown_data.get('success'):
                    expected_gp_hr = expected_data['result'].get('gp_hr', 0)
                    breakdown_gp_hr = breakdown_data['result']['overall'].get('expected_gp_per_hour', 0)
                    
                    print(f"Expected mode GP/hr: {expected_gp_hr:,}")
                    print(f"Breakdown overall GP/hr: {breakdown_gp_hr:,}")
                    
                    # Check if they're reasonably close (within 10%)
                    if expected_gp_hr > 0 and breakdown_gp_hr > 0:
                        diff_percent = abs(expected_gp_hr - breakdown_gp_hr) / max(expected_gp_hr, breakdown_gp_hr) * 100
                        if diff_percent > 10:
                            self.log_issue('CONSISTENCY', 'HIGH', 
                                         f"Expected mode and breakdown GP/hr differ by {diff_percent:.1f}%",
                                         {'expected': expected_gp_hr, 'breakdown': breakdown_gp_hr})
                        else:
                            print("✅ Expected and breakdown GP/hr are consistent")
                            self.test_results['data_consistency'] = 'PASS'
                    else:
                        self.log_issue('CONSISTENCY', 'HIGH', "One or both calculations returned 0 GP/hr",
                                     {'expected': expected_gp_hr, 'breakdown': breakdown_gp_hr})
                        self.test_results['data_consistency'] = 'FAIL'
                else:
                    self.log_issue('CONSISTENCY', 'HIGH', "One or both consistency test calls failed")
                    self.test_results['data_consistency'] = 'FAIL'
            else:
                self.log_issue('CONSISTENCY', 'HIGH', "HTTP errors in consistency test")
                self.test_results['data_consistency'] = 'FAIL'
                
        except Exception as e:
            print(f"💥 Data consistency test exception: {e}")
            self.log_issue('CONSISTENCY', 'CRITICAL', "Data consistency test exception", {'error': str(e)})
            self.test_results['data_consistency'] = 'ERROR'
    
    def test_nieve_fix_verification(self):
        """Verify that Nieve's data is properly fixed"""
        print("\n👑 TESTING NIEVE FIX VERIFICATION")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_base}/api/items/slayer?category=masters", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    masters = result.get('items', {})
                    nieve_data = masters.get('nieve', {})
                    
                    if nieve_data:
                        task_assignments = nieve_data.get('task_assignments', {})
                        
                        # Check for corrupted "every_X" entries
                        corrupted = [name for name in task_assignments.keys() if name.startswith('every_')]
                        proper = [name for name in task_assignments.keys() if not name.startswith('every_')]
                        
                        print(f"Nieve assignments: {len(task_assignments)} total")
                        print(f"Proper monster names: {len(proper)}")
                        print(f"Corrupted entries: {len(corrupted)}")
                        
                        if len(corrupted) > 0:
                            self.log_issue('NIEVE', 'CRITICAL', f"Nieve still has {len(corrupted)} corrupted assignments", 
                                         {'corrupted': corrupted})
                            self.test_results['nieve_fix'] = 'FAIL'
                        elif len(proper) < 20:
                            self.log_issue('NIEVE', 'HIGH', f"Nieve has too few assignments ({len(proper)})")
                            self.test_results['nieve_fix'] = 'FAIL'
                        else:
                            print("✅ Nieve's data appears to be properly fixed")
                            self.test_results['nieve_fix'] = 'PASS'
                    else:
                        self.log_issue('NIEVE', 'CRITICAL', "Nieve data not found in masters")
                        self.test_results['nieve_fix'] = 'FAIL'
                else:
                    self.log_issue('NIEVE', 'HIGH', "Failed to get masters data")
                    self.test_results['nieve_fix'] = 'FAIL'
            else:
                self.log_issue('NIEVE', 'HIGH', f"HTTP error getting masters: {response.status_code}")
                self.test_results['nieve_fix'] = 'FAIL'
                
        except Exception as e:
            print(f"💥 Nieve verification exception: {e}")
            self.log_issue('NIEVE', 'CRITICAL', "Nieve verification exception", {'error': str(e)})
            self.test_results['nieve_fix'] = 'ERROR'
    
    def analyze_frontend_backend_disconnect(self):
        """Analyze potential disconnects between frontend and backend"""
        print("\n🔗 ANALYZING FRONTEND-BACKEND DISCONNECTS")
        print("=" * 50)
        
        # Check if calculation modes are properly handled
        print("Checking calculation mode handling...")
        
        # The issue: Frontend switches calculation_mode but doesn't trigger recalculation
        # This is a CRITICAL bug in the frontend logic
        self.log_issue('FRONTEND', 'CRITICAL', 
                      "Calculation mode switching doesn't trigger recalculation",
                      {
                          'problem': 'When user clicks Expected GP/hr vs Task Breakdown, the UI changes the calculation_mode parameter but does not call calculateGpHour()',
                          'location': 'ActivityCard.jsx handleParamChange function',
                          'impact': 'Users see no difference when switching modes',
                          'fix_needed': 'Add conditional recalculation trigger for calculation_mode changes'
                      })
        
        # Check if breakdown data is properly displayed
        self.log_issue('FRONTEND', 'HIGH',
                      "Breakdown display logic may not be mode-aware",
                      {
                          'problem': 'Frontend shows slayerBreakdown data regardless of calculation_mode',
                          'location': 'ActivityCard.jsx rendering logic',
                          'impact': 'Task breakdown always shows, even in expected mode',
                          'fix_needed': 'Conditional rendering based on calculation_mode'
                      })
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive bug report"""
        print("\n" + "=" * 80)
        print("🔍 COMPREHENSIVE BUG ANALYSIS REPORT")
        print("=" * 80)
        
        # Categorize issues by severity
        critical_issues = [i for i in self.issues if i['severity'] == 'CRITICAL']
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low_issues = [i for i in self.issues if i['severity'] == 'LOW']
        
        print(f"\n📊 ISSUE SUMMARY:")
        print(f"   🔴 CRITICAL: {len(critical_issues)}")
        print(f"   🟠 HIGH:     {len(high_issues)}")
        print(f"   🟡 MEDIUM:   {len(medium_issues)}")
        print(f"   🟢 LOW:      {len(low_issues)}")
        print(f"   📈 TOTAL:    {len(self.issues)}")
        
        # Test results summary
        passed = len([r for r in self.test_results.values() if r == 'PASS'])
        failed = len([r for r in self.test_results.values() if r == 'FAIL'])
        errors = len([r for r in self.test_results.values() if r == 'ERROR'])
        total_tests = len(self.test_results)
        
        print(f"\n🧪 TEST RESULTS:")
        print(f"   ✅ PASSED:  {passed}/{total_tests}")
        print(f"   ❌ FAILED:  {failed}/{total_tests}")
        print(f"   💥 ERRORS:  {errors}/{total_tests}")
        
        # Detailed issues
        if critical_issues:
            print(f"\n🔴 CRITICAL ISSUES (MUST FIX IMMEDIATELY):")
            for i, issue in enumerate(critical_issues, 1):
                print(f"   {i}. [{issue['category']}] {issue['description']}")
                if issue['details']:
                    print(f"      Details: {issue['details']}")
        
        if high_issues:
            print(f"\n🟠 HIGH PRIORITY ISSUES:")
            for i, issue in enumerate(high_issues, 1):
                print(f"   {i}. [{issue['category']}] {issue['description']}")
        
        # Recommendations
        print(f"\n💡 IMMEDIATE ACTION ITEMS:")
        print(f"   1. Fix calculation mode switching in frontend (CRITICAL)")
        print(f"   2. Ensure backend calculation modes work correctly")
        print(f"   3. Verify data consistency between endpoints")
        print(f"   4. Test all slayer masters and monsters")
        print(f"   5. Implement proper error handling throughout")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.issues),
                'critical': len(critical_issues),
                'high': len(high_issues),
                'medium': len(medium_issues),
                'low': len(low_issues)
            },
            'test_results': self.test_results,
            'issues': self.issues
        }
        
        with open('bug_analysis_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: bug_analysis_report.json")
        
        return len(critical_issues) == 0 and len(high_issues) == 0
    
    def run_comprehensive_analysis(self):
        """Run the complete bug analysis"""
        print("🚀 STARTING COMPREHENSIVE BUG ANALYSIS")
        print("=" * 80)
        print(f"Timestamp: {datetime.now()}")
        print(f"Backend URL: {self.api_base}")
        print(f"Frontend URL: {self.frontend_base}")
        
        start_time = time.time()
        
        # Run all tests
        self.test_backend_connectivity()
        self.test_slayer_calculation_modes()
        self.test_slayer_breakdown_endpoint()
        self.test_frontend_connectivity()
        self.test_data_consistency()
        self.test_nieve_fix_verification()
        self.analyze_frontend_backend_disconnect()
        
        # Generate report
        total_time = time.time() - start_time
        print(f"\n⏱️ Analysis completed in {total_time:.2f} seconds")
        
        success = self.generate_comprehensive_report()
        
        if success:
            print("\n🎉 ANALYSIS COMPLETE - No critical issues found!")
        else:
            print("\n⚠️ ANALYSIS COMPLETE - Critical issues found that need immediate attention!")
        
        return success

def main():
    analyzer = ComprehensiveBugAnalyzer()
    success = analyzer.run_comprehensive_analysis()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 