"""
Database Load Testing Service
=============================

Simuliert realistische Last auf die SQLite Database um Performance-Bottlenecks
und Skalierungslimits zu identifizieren.
"""

import time
import threading
import random
import json
import statistics
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import logging
from sqlmodel import Session, select, text
from app.database import engine
from app.models import Announcement, Status, StandardHours, HourException, Availability, VisitorAnalytics

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Results from a load test run"""
    test_name: str
    duration_seconds: float
    total_operations: int
    successful_operations: int
    failed_operations: int
    operations_per_second: float
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    error_rate_percent: float
    concurrent_connections: int
    errors: List[str]
    

class DatabaseLoadTester:
    """Advanced database load testing"""
    
    def __init__(self):
        self.test_data = self._prepare_test_data()
        
    def _prepare_test_data(self) -> Dict[str, Any]:
        """Prepare realistic test data patterns"""
        
        # Sample data that mimics real usage
        languages = ['de', 'th', 'en']
        page_paths = ['/', '/week', '/month', '/kiosk/single', '/kiosk/triple']
        device_types = ['mobile', 'tablet', 'desktop']
        browser_families = ['chrome', 'safari', 'firefox', 'edge']
        
        return {
            'languages': languages,
            'page_paths': page_paths,
            'device_types': device_types,
            'browser_families': browser_families,
            'status_types': ['ANWESEND', 'URLAUB', 'BILDUNGSURLAUB', 'KONGRESS'],
            'priorities': ['low', 'normal', 'high', 'urgent']
        }

    def simulate_visitor_load(self, concurrent_users: int, duration_seconds: int) -> LoadTestResult:
        """Simulate concurrent visitor load (typical homepage usage)"""
        
        print(f"🏠 Testing visitor load: {concurrent_users} concurrent users for {duration_seconds}s")
        
        results = []
        errors = []
        start_time = time.time()
        
        def simulate_visitor_session():
            """Simulate a single visitor session"""
            session_start = time.time()
            
            try:
                with Session(engine) as db_session:
                    # Typical visitor queries
                    
                    # 1. Get current status (homepage load)
                    query_start = time.time()
                    db_session.exec(select(Status).order_by(Status.created_at.desc()).limit(1)).first()
                    status_time = (time.time() - query_start) * 1000
                    
                    # 2. Get announcements
                    query_start = time.time() 
                    lang = random.choice(self.test_data['languages'])
                    db_session.exec(
                        select(Announcement)
                        .where(Announcement.active == True)
                        .where(Announcement.lang == lang)
                        .order_by(Announcement.priority.desc(), Announcement.created_at.desc())
                        .limit(5)
                    ).all()
                    announcement_time = (time.time() - query_start) * 1000
                    
                    # 3. Get opening hours
                    query_start = time.time()
                    db_session.exec(select(StandardHours).order_by(StandardHours.day_of_week)).all()
                    hours_time = (time.time() - query_start) * 1000
                    
                    # 4. Check for exceptions (holiday check)
                    query_start = time.time()
                    today = datetime.now().date()
                    db_session.exec(
                        select(HourException)
                        .where(HourException.exception_date >= today)
                        .order_by(HourException.exception_date)
                        .limit(10)
                    ).all()
                    exception_time = (time.time() - query_start) * 1000
                    
                    total_session_time = (time.time() - session_start) * 1000
                    
                    return {
                        'success': True,
                        'session_time_ms': total_session_time,
                        'query_times': {
                            'status': status_time,
                            'announcements': announcement_time,
                            'hours': hours_time,
                            'exceptions': exception_time
                        }
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'session_time_ms': (time.time() - session_start) * 1000
                }
        
        # Run concurrent sessions
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                # Submit new visitor session
                future = executor.submit(simulate_visitor_session)
                futures.append(future)
                
                time.sleep(0.1)  # Small delay between session starts
                
            # Collect results
            for future in as_completed(futures, timeout=duration_seconds + 10):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    errors.append(f"Future execution error: {str(e)}")
        
        # Calculate metrics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if successful_results:
            response_times = [r['session_time_ms'] for r in successful_results]
            
            return LoadTestResult(
                test_name="visitor_load",
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=len(successful_results),
                failed_operations=len(failed_results),
                operations_per_second=len(results) / (time.time() - start_time),
                average_response_time_ms=statistics.mean(response_times),
                min_response_time_ms=min(response_times),
                max_response_time_ms=max(response_times),
                p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else max(response_times),
                error_rate_percent=(len(failed_results) / len(results)) * 100,
                concurrent_connections=concurrent_users,
                errors=[r.get('error', '') for r in failed_results] + errors
            )
        else:
            return LoadTestResult(
                test_name="visitor_load",
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=0,
                failed_operations=len(results),
                operations_per_second=0,
                average_response_time_ms=0,
                min_response_time_ms=0,
                max_response_time_ms=0,
                p95_response_time_ms=0,
                error_rate_percent=100,
                concurrent_connections=concurrent_users,
                errors=[r.get('error', '') for r in results] + errors
            )

    def simulate_admin_load(self, concurrent_admins: int, duration_seconds: int) -> LoadTestResult:
        """Simulate concurrent admin operations"""
        
        print(f"👤 Testing admin load: {concurrent_admins} concurrent admins for {duration_seconds}s")
        
        results = []
        errors = []
        start_time = time.time()
        
        def simulate_admin_session():
            """Simulate admin operations"""
            session_start = time.time()
            
            try:
                with Session(engine) as db_session:
                    # Admin dashboard queries
                    
                    # 1. Get recent announcements for dashboard
                    query_start = time.time()
                    db_session.exec(
                        select(Announcement).order_by(Announcement.created_at.desc()).limit(5)
                    ).all()
                    dashboard_time = (time.time() - query_start) * 1000
                    
                    # 2. Check availability slots  
                    query_start = time.time()
                    today = datetime.now().date()
                    db_session.exec(
                        select(Availability)
                        .where(Availability.availability_date >= today)
                        .where(Availability.active == True)
                        .order_by(Availability.availability_date, Availability.start_time)
                    ).all()
                    availability_time = (time.time() - query_start) * 1000
                    
                    # 3. Simulate occasional update operation
                    if random.random() < 0.1:  # 10% of admin sessions do updates
                        query_start = time.time()
                        
                        # Create test announcement
                        test_announcement = Announcement(
                            lang='de',
                            title=f'Test {datetime.now().isoformat()}',
                            body='Load test announcement',
                            priority='normal',
                            category='test'
                        )
                        db_session.add(test_announcement)
                        db_session.commit()
                        
                        # Delete it again to keep database clean
                        db_session.delete(test_announcement)
                        db_session.commit()
                        
                        update_time = (time.time() - query_start) * 1000
                    else:
                        update_time = 0
                    
                    total_session_time = (time.time() - session_start) * 1000
                    
                    return {
                        'success': True,
                        'session_time_ms': total_session_time,
                        'query_times': {
                            'dashboard': dashboard_time,
                            'availability': availability_time,
                            'update': update_time
                        }
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'session_time_ms': (time.time() - session_start) * 1000
                }
        
        # Run concurrent admin sessions
        with ThreadPoolExecutor(max_workers=concurrent_admins) as executor:
            futures = []
            
            while time.time() - start_time < duration_seconds:
                future = executor.submit(simulate_admin_session)
                futures.append(future)
                time.sleep(0.5)  # Admin operations are less frequent
                
            # Collect results
            for future in as_completed(futures, timeout=duration_seconds + 10):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    errors.append(f"Admin session error: {str(e)}")
        
        # Calculate metrics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if successful_results:
            response_times = [r['session_time_ms'] for r in successful_results]
            
            return LoadTestResult(
                test_name="admin_load",
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=len(successful_results),
                failed_operations=len(failed_results),
                operations_per_second=len(results) / (time.time() - start_time),
                average_response_time_ms=statistics.mean(response_times),
                min_response_time_ms=min(response_times),
                max_response_time_ms=max(response_times),
                p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else max(response_times),
                error_rate_percent=(len(failed_results) / len(results)) * 100,
                concurrent_connections=concurrent_admins,
                errors=[r.get('error', '') for r in failed_results] + errors
            )
        else:
            return LoadTestResult(
                test_name="admin_load", 
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=0,
                failed_operations=len(results), 
                operations_per_second=0,
                average_response_time_ms=0,
                min_response_time_ms=0,
                max_response_time_ms=0,
                p95_response_time_ms=0,
                error_rate_percent=100,
                concurrent_connections=concurrent_admins,
                errors=[r.get('error', '') for r in results] + errors
            )

    def simulate_analytics_load(self, duration_seconds: int) -> LoadTestResult:
        """Simulate heavy analytics queries"""
        
        print(f"📊 Testing analytics load for {duration_seconds}s")
        
        results = []
        start_time = time.time()
        
        analytics_queries = [
            # Daily stats aggregation
            "SELECT COUNT(*) as visits, COUNT(DISTINCT session_hash) as unique_visitors FROM visitoranalytics WHERE visit_date = date('now')",
            
            # Weekly trends
            "SELECT visit_date, COUNT(*) as visits FROM visitoranalytics WHERE visit_date >= date('now', '-7 days') GROUP BY visit_date ORDER BY visit_date",
            
            # Page popularity  
            "SELECT page_path, COUNT(*) as views FROM visitoranalytics WHERE visit_date >= date('now', '-30 days') GROUP BY page_path ORDER BY views DESC",
            
            # Device breakdown
            "SELECT device_type, COUNT(*) FROM visitoranalytics WHERE visit_date >= date('now', '-7 days') GROUP BY device_type",
            
            # Language preferences
            "SELECT preferred_language, COUNT(*) FROM visitoranalytics WHERE visit_date >= date('now', '-30 days') GROUP BY preferred_language",
            
            # QR code effectiveness
            "SELECT qr_code_scan, COUNT(*) FROM visitoranalytics WHERE visit_date >= date('now', '-7 days') GROUP BY qr_code_scan",
        ]
        
        def run_analytics_query():
            """Run a single analytics query"""
            query_start = time.time()
            
            try:
                with Session(engine) as db_session:
                    query = random.choice(analytics_queries)
                    result = db_session.exec(text(query)).all()
                    
                    query_time = (time.time() - query_start) * 1000
                    
                    return {
                        'success': True,
                        'query_time_ms': query_time,
                        'rows_returned': len(result),
                        'query': query[:50] + "..." if len(query) > 50 else query
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'query_time_ms': (time.time() - query_start) * 1000
                }
        
        # Run queries continuously for specified duration
        with ThreadPoolExecutor(max_workers=5) as executor:  # Moderate concurrency for analytics
            futures = []
            
            while time.time() - start_time < duration_seconds:
                future = executor.submit(run_analytics_query)
                futures.append(future)
                time.sleep(0.2)  # Analytics queries every 200ms
                
            # Collect results
            for future in as_completed(futures, timeout=duration_seconds + 10):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'success': False, 'error': str(e), 'query_time_ms': 0})
        
        # Calculate metrics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if successful_results:
            response_times = [r['query_time_ms'] for r in successful_results]
            
            return LoadTestResult(
                test_name="analytics_load",
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=len(successful_results),
                failed_operations=len(failed_results),
                operations_per_second=len(results) / (time.time() - start_time),
                average_response_time_ms=statistics.mean(response_times),
                min_response_time_ms=min(response_times),
                max_response_time_ms=max(response_times),
                p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else max(response_times),
                error_rate_percent=(len(failed_results) / len(results)) * 100,
                concurrent_connections=5,
                errors=[r.get('error', '') for r in failed_results]
            )
        else:
            return LoadTestResult(
                test_name="analytics_load",
                duration_seconds=time.time() - start_time,
                total_operations=len(results),
                successful_operations=0,
                failed_operations=len(results),
                operations_per_second=0,
                average_response_time_ms=0,
                min_response_time_ms=0,
                max_response_time_ms=0,
                p95_response_time_ms=0,
                error_rate_percent=100,
                concurrent_connections=5,
                errors=[r.get('error', '') for r in results]
            )

    def stress_test_mixed_load(self, duration_seconds: int = 120) -> Dict[str, Any]:
        """Run comprehensive stress test with mixed workload"""
        
        print(f"🔥 Running mixed workload stress test for {duration_seconds}s")
        
        start_time = time.time()
        test_results = {}
        
        # Run different load patterns simultaneously
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit different load test scenarios
            visitor_future = executor.submit(self.simulate_visitor_load, 10, duration_seconds // 2)
            admin_future = executor.submit(self.simulate_admin_load, 2, duration_seconds // 2) 
            analytics_future = executor.submit(self.simulate_analytics_load, duration_seconds // 3)
            
            # Wait for completion
            test_results['visitor_load'] = visitor_future.result()
            test_results['admin_load'] = admin_future.result()
            test_results['analytics_load'] = analytics_future.result()
            
        # Aggregate results
        total_operations = sum(result.total_operations for result in test_results.values())
        successful_operations = sum(result.successful_operations for result in test_results.values())
        failed_operations = sum(result.failed_operations for result in test_results.values())
        
        overall_results = {
            "stress_test_summary": {
                "test_duration_seconds": time.time() - start_time,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "overall_success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0,
                "combined_operations_per_second": total_operations / (time.time() - start_time)
            },
            "individual_tests": {
                name: asdict(result) for name, result in test_results.items()
            },
            "performance_assessment": self._assess_performance(test_results)
        }
        
        return overall_results

    def _assess_performance(self, test_results: Dict[str, LoadTestResult]) -> Dict[str, Any]:
        """Assess overall performance and provide recommendations"""
        
        assessment = {
            "overall_grade": "A",  # A, B, C, D, F
            "bottlenecks": [],
            "recommendations": [],
            "capacity_limits": {}
        }
        
        for test_name, result in test_results.items():
            # Check performance thresholds
            if result.average_response_time_ms > 100:
                assessment["bottlenecks"].append(f"{test_name}: High average response time ({result.average_response_time_ms:.2f}ms)")
                assessment["overall_grade"] = max(assessment["overall_grade"], "C", key=lambda x: ord(x))
                
            if result.error_rate_percent > 5:
                assessment["bottlenecks"].append(f"{test_name}: High error rate ({result.error_rate_percent:.1f}%)")
                assessment["overall_grade"] = max(assessment["overall_grade"], "D", key=lambda x: ord(x))
                
            if result.p95_response_time_ms > 500:
                assessment["bottlenecks"].append(f"{test_name}: High P95 response time ({result.p95_response_time_ms:.2f}ms)")
                
            # Calculate capacity estimates
            if result.error_rate_percent < 1 and result.average_response_time_ms < 50:
                estimated_capacity = result.concurrent_connections * 2  # Can probably handle 2x load
            elif result.error_rate_percent < 5 and result.average_response_time_ms < 100:
                estimated_capacity = result.concurrent_connections * 1.5  # Can handle 50% more load
            else:
                estimated_capacity = result.concurrent_connections * 0.8  # At capacity limit
                
            assessment["capacity_limits"][test_name] = {
                "current_concurrent_users": result.concurrent_connections,
                "estimated_max_capacity": int(estimated_capacity),
                "safety_margin": estimated_capacity / result.concurrent_connections if result.concurrent_connections > 0 else 1
            }
        
        # Generate recommendations
        if not assessment["bottlenecks"]:
            assessment["recommendations"].append("✅ Database performance is excellent for current load")
        else:
            assessment["recommendations"].append("⚠️ Performance bottlenecks detected - see detailed analysis")
            
        # Specific recommendations based on patterns
        avg_times = [result.average_response_time_ms for result in test_results.values()]
        if any(t > 50 for t in avg_times):
            assessment["recommendations"].append("🔍 Review slow queries and add targeted indexes")
            
        error_rates = [result.error_rate_percent for result in test_results.values()]  
        if any(r > 1 for r in error_rates):
            assessment["recommendations"].append("🔧 Investigate database connection issues and timeouts")
            
        return assessment

    def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load test suite"""
        
        print("🚀 Starting comprehensive database load test...")
        
        comprehensive_results = {
            "test_start": datetime.now().isoformat(),
            "test_scenarios": {}
        }
        
        # Test scenarios with increasing load
        scenarios = [
            {"name": "light_load", "visitors": 5, "admins": 1, "duration": 30},
            {"name": "normal_load", "visitors": 15, "admins": 2, "duration": 60},  
            {"name": "heavy_load", "visitors": 30, "admins": 5, "duration": 60},
        ]
        
        for scenario in scenarios:
            print(f"\\n📋 Running scenario: {scenario['name']}")
            
            try:
                # Run visitor load
                visitor_result = self.simulate_visitor_load(
                    scenario['visitors'], 
                    scenario['duration']
                )
                
                # Run admin load
                admin_result = self.simulate_admin_load(
                    scenario['admins'],
                    scenario['duration'] // 2
                )
                
                # Run analytics load  
                analytics_result = self.simulate_analytics_load(scenario['duration'] // 3)
                
                scenario_results = {
                    "visitor_load": asdict(visitor_result),
                    "admin_load": asdict(admin_result),
                    "analytics_load": asdict(analytics_result),
                    "scenario_assessment": self._assess_performance({
                        "visitor": visitor_result,
                        "admin": admin_result, 
                        "analytics": analytics_result
                    })
                }
                
                comprehensive_results["test_scenarios"][scenario["name"]] = scenario_results
                
                print(f"   ✅ {scenario['name']} completed")
                print(f"      Visitors: {visitor_result.operations_per_second:.1f} ops/s, {visitor_result.average_response_time_ms:.2f}ms avg")
                print(f"      Admin: {admin_result.operations_per_second:.1f} ops/s, {admin_result.average_response_time_ms:.2f}ms avg")
                print(f"      Analytics: {analytics_result.operations_per_second:.1f} ops/s, {analytics_result.average_response_time_ms:.2f}ms avg")
                
            except Exception as e:
                comprehensive_results["test_scenarios"][scenario["name"]] = {
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                }
                print(f"   ❌ {scenario['name']} failed: {e}")
        
        comprehensive_results["test_completed"] = datetime.now().isoformat()
        comprehensive_results["total_test_duration"] = (datetime.now().timestamp() - 
                                                       datetime.fromisoformat(comprehensive_results["test_start"]).timestamp())
        
        return comprehensive_results


def run_load_test_suite() -> Dict[str, Any]:
    """Run complete load testing suite"""
    
    tester = DatabaseLoadTester()
    results = tester.run_comprehensive_load_test()
    
    # Save results
    report_file = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
        
    print(f"📊 Load test report saved: {report_file}")
    
    return results


if __name__ == "__main__":
    # Run load test when script is executed directly
    results = run_load_test_suite()
    
    print("\\n🎯 Load Test Summary:")
    for scenario_name, scenario_data in results["test_scenarios"].items():
        if "error" not in scenario_data:
            assessment = scenario_data["scenario_assessment"]
            print(f"   {scenario_name}: Grade {assessment['overall_grade']}")
        else:
            print(f"   {scenario_name}: FAILED")