#!/usr/bin/env python3
"""
Database Optimization Script
============================

Umfassendes Database-Optimierungs-Script für das QR-Info-Portal.
Führt Performance-Optimierungen, Index-Erstellung, und Health-Checks durch.
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database_optimizer import DatabaseOptimizer, optimize_database
from app.services.backup_manager import BackupManager, PostgreSQLMigrator
from app.services.database_health import DatabaseHealthMonitor


def run_full_optimization(database_path: str) -> Dict[str, Any]:
    """Run complete database optimization"""
    
    print("🚀 Starting comprehensive database optimization...")
    
    results = {
        "started_at": datetime.now().isoformat(),
        "operations": {}
    }
    
    # 1. Create backup before optimization
    print("\n📦 Creating backup before optimization...")
    try:
        backup_manager = BackupManager(database_path)
        backup_info = backup_manager.create_backup("pre_optimization")
        results["operations"]["backup"] = {
            "success": True,
            "backup_file": backup_info.name,
            "size_mb": backup_info.size_mb
        }
        print(f"✅ Backup created: {backup_info.name} ({backup_info.size_mb:.2f}MB)")
    except Exception as e:
        results["operations"]["backup"] = {"success": False, "error": str(e)}
        print(f"❌ Backup failed: {e}")
        return results
    
    # 2. Run database optimization
    print("\n⚡ Running database optimization...")
    try:
        optimization_results = optimize_database(database_path)
        results["operations"]["optimization"] = optimization_results
        print("✅ Database optimization completed")
    except Exception as e:
        results["operations"]["optimization"] = {"success": False, "error": str(e)}
        print(f"❌ Optimization failed: {e}")
    
    # 3. Health check
    print("\n🏥 Running health check...")
    try:
        health_monitor = DatabaseHealthMonitor()
        health_check = health_monitor.run_health_check()
        results["operations"]["health_check"] = health_check
        print(f"✅ Health check completed: {health_check['overall_status']}")
    except Exception as e:
        results["operations"]["health_check"] = {"success": False, "error": str(e)}
        print(f"❌ Health check failed: {e}")
    
    # 4. Performance baseline
    print("\n📊 Collecting performance baseline...")
    try:
        optimizer = DatabaseOptimizer(f"sqlite:///{database_path}")
        performance_metrics = optimizer.get_performance_metrics()
        results["operations"]["performance_baseline"] = performance_metrics
        print("✅ Performance baseline collected")
    except Exception as e:
        results["operations"]["performance_baseline"] = {"success": False, "error": str(e)}
        print(f"❌ Performance baseline failed: {e}")
    
    results["completed_at"] = datetime.now().isoformat()
    results["success"] = all(
        op.get("success", True) for op in results["operations"].values()
    )
    
    return results


def run_benchmark_test(database_path: str, duration_seconds: int = 60) -> Dict[str, Any]:
    """Run database performance benchmark"""
    
    print(f"🏃‍♂️ Running {duration_seconds}s performance benchmark...")
    
    optimizer = DatabaseOptimizer(f"sqlite:///{database_path}")
    
    # Common queries to benchmark
    benchmark_queries = [
        # Homepage queries
        "SELECT * FROM announcement WHERE active = 1 AND lang = 'de' ORDER BY priority DESC, created_at DESC LIMIT 5",
        "SELECT * FROM status ORDER BY created_at DESC LIMIT 1",
        "SELECT * FROM standardhours ORDER BY day_of_week",
        "SELECT * FROM hourexception WHERE exception_date >= date('now') ORDER BY exception_date LIMIT 10",
        
        # Analytics queries
        "SELECT COUNT(*) FROM visitoranalytics WHERE visit_date = date('now')",
        "SELECT page_path, COUNT(*) as views FROM visitoranalytics WHERE visit_date >= date('now', '-7 days') GROUP BY page_path",
        
        # Admin queries
        "SELECT COUNT(*) FROM changelog WHERE created_at >= datetime('now', '-1 day')",
        "SELECT * FROM availability WHERE availability_date >= date('now') AND active = 1 ORDER BY availability_date, start_time",
    ]
    
    start_time = time.time()
    end_time = start_time + duration_seconds
    
    query_results = []
    total_queries = 0
    
    while time.time() < end_time:
        for query in benchmark_queries:
            try:
                metrics = optimizer.monitor_query_performance(query)
                query_results.append({
                    "query": query[:50] + "..." if len(query) > 50 else query,
                    "execution_time_ms": metrics.execution_time_ms,
                    "used_index": metrics.used_index,
                    "rows_returned": metrics.rows_returned
                })
                total_queries += 1
                
            except Exception as e:
                query_results.append({
                    "query": query[:50] + "...",
                    "error": str(e)
                })
                
        time.sleep(0.1)  # Small delay between runs
        
    # Calculate benchmark statistics
    successful_queries = [q for q in query_results if "error" not in q]
    execution_times = [q["execution_time_ms"] for q in successful_queries]
    
    benchmark_results = {
        "benchmark_duration_seconds": duration_seconds,
        "total_queries_executed": total_queries,
        "successful_queries": len(successful_queries),
        "failed_queries": total_queries - len(successful_queries),
        "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
        "min_execution_time_ms": min(execution_times) if execution_times else 0,
        "max_execution_time_ms": max(execution_times) if execution_times else 0,
        "queries_per_second": total_queries / duration_seconds,
        "slow_queries": len([t for t in execution_times if t > 100]),
        "query_samples": query_results[:20]  # First 20 query results
    }
    
    print(f"✅ Benchmark completed:")
    print(f"   - {total_queries} queries in {duration_seconds}s ({benchmark_results['queries_per_second']:.2f} QPS)")
    print(f"   - Average execution time: {benchmark_results['average_execution_time_ms']:.2f}ms")
    print(f"   - Slow queries (>100ms): {benchmark_results['slow_queries']}")
    
    return benchmark_results


def generate_migration_package(database_path: str, output_dir: str) -> Dict[str, Any]:
    """Generate PostgreSQL migration package"""
    
    print("📦 Generating PostgreSQL migration package...")
    
    migrator = PostgreSQLMigrator(database_path)
    package_info = migrator.create_migration_package(output_dir)
    
    if package_info.get("success"):
        print(f"✅ Migration package created: {package_info['package_dir']}")
        print("📋 Package contents:")
        for file_type, file_path in package_info["files"].items():
            print(f"   - {file_type}: {file_path}")
    else:
        print(f"❌ Migration package failed: {package_info.get('error')}")
        
    return package_info


def main():
    """Main optimization script"""
    
    parser = argparse.ArgumentParser(description="QR-Info-Portal Database Optimizer")
    parser.add_argument("--database", default="data/portal.db", help="Database file path")
    parser.add_argument("--optimize", action="store_true", help="Run full optimization")
    parser.add_argument("--benchmark", type=int, metavar="SECONDS", help="Run performance benchmark")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--create-backup", help="Create backup with specified type")
    parser.add_argument("--list-backups", action="store_true", help="List all available backups")
    parser.add_argument("--migrate-postgresql", help="Generate PostgreSQL migration package (specify output dir)")
    parser.add_argument("--export-report", help="Export detailed performance report to file")
    
    args = parser.parse_args()
    
    database_path = args.database
    
    if not os.path.exists(database_path):
        print(f"❌ Database file not found: {database_path}")
        sys.exit(1)
    
    print(f"🎯 QR-Info-Portal Database Optimizer")
    print(f"📁 Database: {database_path}")
    print(f"📊 Size: {os.path.getsize(database_path) / (1024*1024):.2f} MB")
    print()
    
    if args.optimize:
        results = run_full_optimization(database_path)
        
        # Save results
        report_file = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Full report saved: {report_file}")
        
    elif args.benchmark:
        results = run_benchmark_test(database_path, args.benchmark)
        
        # Save benchmark results
        benchmark_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(benchmark_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Benchmark results saved: {benchmark_file}")
        
    elif args.health_check:
        health_monitor = DatabaseHealthMonitor()
        health_results = health_monitor.run_health_check()
        
        print("🏥 Database Health Check Results:")
        print(f"   Overall Status: {health_results['overall_status']}")
        print("   Individual Checks:")
        for check_name, check_result in health_results["checks"].items():
            status_icon = "✅" if check_result["status"] == "pass" else "⚠️" if check_result["status"] == "warning" else "❌"
            print(f"     {status_icon} {check_name}: {check_result['message']}")
            
    elif args.create_backup:
        backup_manager = BackupManager(database_path)
        backup_info = backup_manager.create_backup(args.create_backup)
        print(f"✅ Backup created: {backup_info.name} ({backup_info.size_mb:.2f}MB)")
        
    elif args.list_backups:
        backup_manager = BackupManager(database_path) 
        backups = backup_manager.list_backups()
        
        if not backups:
            print("📭 No backups found")
        else:
            print(f"📦 Found {len(backups)} backups:")
            for backup in backups[:10]:  # Show latest 10
                print(f"   - {backup.name} ({backup.size_mb:.2f}MB) - {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
    elif args.migrate_postgresql:
        results = generate_migration_package(database_path, args.migrate_postgresql)
        
    elif args.export_report:
        optimizer = DatabaseOptimizer(f"sqlite:///{database_path}")
        report = optimizer.generate_performance_report()
        
        with open(args.export_report, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📊 Performance report exported: {args.export_report}")
        
    else:
        print("❓ No operation specified. Use --help for available options")
        print("\nQuick commands:")
        print("  --optimize                  # Run full optimization")
        print("  --benchmark 60              # Run 60-second benchmark")
        print("  --health-check              # Check database health")
        print("  --create-backup manual      # Create manual backup")
        print("  --migrate-postgresql ./pg   # Create PostgreSQL migration package")


if __name__ == "__main__":
    main()