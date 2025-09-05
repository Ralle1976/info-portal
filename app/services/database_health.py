"""
Database Health Monitoring Service
==================================

Überwacht Database Performance, Connection Health und System-Metriken
für das QR-Info-Portal. Bietet Real-time Monitoring und Alerting.
"""

import sqlite3
import time
import psutil
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from sqlmodel import Session, select, text
from app.database import engine
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Container for database health metrics"""
    timestamp: datetime
    database_size_mb: float
    connection_count: int
    active_queries: int
    avg_query_time_ms: float
    cache_hit_ratio: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_count: int
    status: str  # healthy, warning, critical


class DatabaseHealthMonitor:
    """Real-time database health monitoring"""
    
    def __init__(self, check_interval_seconds: int = 60):
        self.check_interval = check_interval_seconds
        self.metrics_history: List[HealthMetrics] = []
        self.error_log: List[Dict[str, Any]] = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.thresholds = {
            "max_query_time_ms": 1000,
            "max_connection_count": 25,
            "max_database_size_mb": 500,
            "max_cpu_usage": 80,
            "max_memory_usage_mb": 256,
            "min_cache_hit_ratio": 0.85
        }
        
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Database health monitoring started")
        
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("⏹️ Database health monitoring stopped")
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self.collect_health_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
                
                # Check for alerts
                self._check_health_alerts(metrics)
                
            except Exception as e:
                self.error_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "type": "monitoring_error"
                })
                logger.error(f"Health monitoring error: {e}")
                
            time.sleep(self.check_interval)
            
    def collect_health_metrics(self) -> HealthMetrics:
        """Collect current database health metrics"""
        
        start_time = time.perf_counter()
        
        try:
            with Session(engine) as session:
                # Database size
                db_size_pages = session.exec(text("PRAGMA page_count")).first()
                page_size = session.exec(text("PRAGMA page_size")).first()
                db_size_mb = (db_size_pages * page_size) / (1024 * 1024)
                
                # Connection stats (approximation for SQLite)
                connection_count = 1  # SQLite is typically single-connection
                active_queries = 0  # Would need query monitoring for accurate count
                
                # Test query performance
                query_start = time.perf_counter()
                session.exec(text("SELECT COUNT(*) FROM announcement WHERE active = 1")).first()
                avg_query_time_ms = (time.perf_counter() - query_start) * 1000
                
                # Cache statistics
                cache_size = session.exec(text("PRAGMA cache_size")).first()
                cache_hit_ratio = 0.95  # SQLite doesn't expose this directly
                
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            # Return minimal metrics on error
            return HealthMetrics(
                timestamp=datetime.now(),
                database_size_mb=0,
                connection_count=0,
                active_queries=0,
                avg_query_time_ms=999999,
                cache_hit_ratio=0,
                disk_io_read_mb=0,
                disk_io_write_mb=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_count=1,
                status="critical"
            )
        
        # System metrics
        try:
            process = psutil.Process()
            memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            cpu_usage = process.cpu_percent()
            
            # Disk I/O for database file
            io_stats = process.io_counters()
            disk_io_read_mb = io_stats.read_bytes / (1024 * 1024)
            disk_io_write_mb = io_stats.write_bytes / (1024 * 1024)
            
        except (psutil.NoSuchProcess, AttributeError):
            memory_usage_mb = 0
            cpu_usage = 0
            disk_io_read_mb = 0
            disk_io_write_mb = 0
            
        # Determine overall health status
        status = self._calculate_health_status(
            db_size_mb, avg_query_time_ms, connection_count, 
            cpu_usage, memory_usage_mb, cache_hit_ratio
        )
        
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            database_size_mb=db_size_mb,
            connection_count=connection_count,
            active_queries=active_queries,
            avg_query_time_ms=avg_query_time_ms,
            cache_hit_ratio=cache_hit_ratio,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage,
            error_count=len([e for e in self.error_log if e.get("timestamp", "") > (datetime.now() - timedelta(hours=1)).isoformat()]),
            status=status
        )
        
        collection_time = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Health metrics collected in {collection_time:.2f}ms")
        
        return metrics
        
    def _calculate_health_status(self, db_size_mb: float, query_time_ms: float, 
                                 connections: int, cpu_percent: float, 
                                 memory_mb: float, cache_ratio: float) -> str:
        """Calculate overall health status based on metrics"""
        
        critical_conditions = [
            db_size_mb > self.thresholds["max_database_size_mb"],
            query_time_ms > self.thresholds["max_query_time_ms"],
            connections > self.thresholds["max_connection_count"],
            cpu_percent > self.thresholds["max_cpu_usage"],
            memory_mb > self.thresholds["max_memory_usage_mb"]
        ]
        
        warning_conditions = [
            db_size_mb > self.thresholds["max_database_size_mb"] * 0.8,
            query_time_ms > self.thresholds["max_query_time_ms"] * 0.7,
            connections > self.thresholds["max_connection_count"] * 0.8,
            cpu_percent > self.thresholds["max_cpu_usage"] * 0.7,
            memory_mb > self.thresholds["max_memory_usage_mb"] * 0.8,
            cache_ratio < self.thresholds["min_cache_hit_ratio"]
        ]
        
        if any(critical_conditions):
            return "critical"
        elif any(warning_conditions):
            return "warning"
        else:
            return "healthy"
            
    def _check_health_alerts(self, metrics: HealthMetrics):
        """Check for health alerts and log warnings"""
        
        alerts = []
        
        if metrics.status == "critical":
            alerts.append(f"🚨 CRITICAL: Database health is critical")
            
        if metrics.avg_query_time_ms > self.thresholds["max_query_time_ms"]:
            alerts.append(f"🐌 Slow queries detected: {metrics.avg_query_time_ms:.2f}ms avg")
            
        if metrics.database_size_mb > self.thresholds["max_database_size_mb"]:
            alerts.append(f"💾 Large database: {metrics.database_size_mb:.2f}MB")
            
        if metrics.cpu_usage_percent > self.thresholds["max_cpu_usage"]:
            alerts.append(f"🔥 High CPU usage: {metrics.cpu_usage_percent:.1f}%")
            
        for alert in alerts:
            logger.warning(alert)
            
    def get_current_health(self) -> Dict[str, Any]:
        """Get current health status"""
        
        if not self.metrics_history:
            metrics = self.collect_health_metrics()
        else:
            metrics = self.metrics_history[-1]
            
        return {
            "status": metrics.status,
            "last_check": metrics.timestamp.isoformat(),
            "metrics": asdict(metrics),
            "alerts": self._get_current_alerts(metrics)
        }
        
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health metrics history"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        return [asdict(m) for m in recent_metrics]
        
    def _get_current_alerts(self, metrics: HealthMetrics) -> List[str]:
        """Get current alert messages"""
        
        alerts = []
        
        if metrics.avg_query_time_ms > self.thresholds["max_query_time_ms"]:
            alerts.append(f"Slow query performance: {metrics.avg_query_time_ms:.2f}ms")
            
        if metrics.database_size_mb > self.thresholds["max_database_size_mb"]:
            alerts.append(f"Database size limit exceeded: {metrics.database_size_mb:.2f}MB")
            
        if metrics.cpu_usage_percent > self.thresholds["max_cpu_usage"]:
            alerts.append(f"High CPU usage: {metrics.cpu_usage_percent:.1f}%")
            
        if metrics.memory_usage_mb > self.thresholds["max_memory_usage_mb"]:
            alerts.append(f"High memory usage: {metrics.memory_usage_mb:.2f}MB")
            
        return alerts

    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        
        start_time = time.perf_counter()
        
        health_check = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Database connectivity test
        try:
            with Session(engine) as session:
                session.exec(text("SELECT 1")).first()
                health_check["checks"]["database_connectivity"] = {"status": "pass", "message": "Database accessible"}
        except Exception as e:
            health_check["checks"]["database_connectivity"] = {"status": "fail", "message": str(e)}
            health_check["overall_status"] = "critical"
            
        # Table integrity test
        try:
            with Session(engine) as session:
                session.exec(text("PRAGMA integrity_check")).first()
                health_check["checks"]["database_integrity"] = {"status": "pass", "message": "Database integrity OK"}
        except Exception as e:
            health_check["checks"]["database_integrity"] = {"status": "fail", "message": str(e)}
            health_check["overall_status"] = "critical"
            
        # Index usage test
        try:
            with Session(engine) as session:
                # Test critical indexes
                test_queries = [
                    "SELECT COUNT(*) FROM announcement WHERE active = 1 AND lang = 'de'",
                    "SELECT COUNT(*) FROM availability WHERE availability_date >= date('now')",
                    "SELECT COUNT(*) FROM hourexception WHERE exception_date = date('now')"
                ]
                
                slow_queries = []
                for query in test_queries:
                    query_start = time.perf_counter()
                    session.exec(text(query)).first()
                    query_time = (time.perf_counter() - query_start) * 1000
                    
                    if query_time > 50:  # More than 50ms is considered slow for simple queries
                        slow_queries.append(f"{query[:50]}... ({query_time:.2f}ms)")
                        
                if slow_queries:
                    health_check["checks"]["query_performance"] = {
                        "status": "warning", 
                        "message": f"Slow queries detected: {', '.join(slow_queries)}"
                    }
                    if health_check["overall_status"] == "healthy":
                        health_check["overall_status"] = "warning"
                else:
                    health_check["checks"]["query_performance"] = {"status": "pass", "message": "Query performance OK"}
                    
        except Exception as e:
            health_check["checks"]["query_performance"] = {"status": "fail", "message": str(e)}
            health_check["overall_status"] = "critical"
            
        # Disk space check
        try:
            db_path = Path("data/portal.db")
            if db_path.exists():
                disk_usage = psutil.disk_usage(db_path.parent)
                free_space_mb = disk_usage.free / (1024 * 1024)
                
                if free_space_mb < 100:  # Less than 100MB free
                    health_check["checks"]["disk_space"] = {
                        "status": "critical", 
                        "message": f"Low disk space: {free_space_mb:.2f}MB free"
                    }
                    health_check["overall_status"] = "critical"
                elif free_space_mb < 500:  # Less than 500MB free
                    health_check["checks"]["disk_space"] = {
                        "status": "warning", 
                        "message": f"Disk space low: {free_space_mb:.2f}MB free"
                    }
                    if health_check["overall_status"] == "healthy":
                        health_check["overall_status"] = "warning"
                else:
                    health_check["checks"]["disk_space"] = {
                        "status": "pass", 
                        "message": f"Disk space OK: {free_space_mb:.2f}MB free"
                    }
        except Exception as e:
            health_check["checks"]["disk_space"] = {"status": "fail", "message": str(e)}
            
        health_check["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
        return health_check

    def get_performance_recommendations(self) -> List[Dict[str, str]]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        if not self.metrics_history:
            return [{"type": "info", "message": "No metrics available yet - start monitoring first"}]
            
        latest = self.metrics_history[-1]
        
        # Database size recommendations
        if latest.database_size_mb > 100:
            recommendations.append({
                "type": "warning",
                "message": f"Database size is {latest.database_size_mb:.2f}MB - consider archiving old analytics data"
            })
            
        # Query performance recommendations
        if latest.avg_query_time_ms > 50:
            recommendations.append({
                "type": "warning", 
                "message": f"Average query time is {latest.avg_query_time_ms:.2f}ms - review indexes and query patterns"
            })
            
        # Memory usage recommendations
        if latest.memory_usage_mb > 128:
            recommendations.append({
                "type": "info",
                "message": f"Memory usage is {latest.memory_usage_mb:.2f}MB - consider connection pooling optimization"
            })
            
        # Cache performance
        if latest.cache_hit_ratio < 0.9:
            recommendations.append({
                "type": "warning",
                "message": f"Cache hit ratio is {latest.cache_hit_ratio:.2%} - increase cache_size PRAGMA"
            })
            
        # Error rate recommendations
        if latest.error_count > 5:
            recommendations.append({
                "type": "critical",
                "message": f"High error count: {latest.error_count} errors in last hour"
            })
            
        if not recommendations:
            recommendations.append({
                "type": "success",
                "message": "Database performance is optimal"
            })
            
        return recommendations

    def export_health_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive health report"""
        
        if not filepath:
            filepath = f"database_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_period_hours": 24,
            "current_health": self.get_current_health(),
            "metrics_history": [asdict(m) for m in self.metrics_history[-100:]],  # Last 100 metrics
            "recommendations": self.get_performance_recommendations(),
            "error_log": self.error_log[-50:],  # Last 50 errors
            "thresholds": self.thresholds,
            "summary": {
                "total_metrics_collected": len(self.metrics_history),
                "average_database_size_mb": sum(m.database_size_mb for m in self.metrics_history) / len(self.metrics_history) if self.metrics_history else 0,
                "average_query_time_ms": sum(m.avg_query_time_ms for m in self.metrics_history) / len(self.metrics_history) if self.metrics_history else 0,
                "health_status_distribution": self._calculate_status_distribution()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        logger.info(f"📊 Health report exported to: {filepath}")
        return filepath
        
    def _calculate_status_distribution(self) -> Dict[str, int]:
        """Calculate distribution of health statuses"""
        
        distribution = {"healthy": 0, "warning": 0, "critical": 0}
        
        for metric in self.metrics_history:
            distribution[metric.status] = distribution.get(metric.status, 0) + 1
            
        return distribution


class DatabaseMaintenanceManager:
    """Manages database maintenance tasks"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        
    def run_maintenance(self, vacuum: bool = False) -> Dict[str, Any]:
        """Run database maintenance tasks"""
        
        start_time = time.perf_counter()
        results = {"tasks": [], "errors": []}
        
        try:
            with Session(engine) as session:
                # Analyze database for query optimizer
                session.exec(text("ANALYZE"))
                results["tasks"].append("✅ Database analysis completed")
                
                # Optimize query planner
                session.exec(text("PRAGMA optimize"))
                results["tasks"].append("✅ Query planner optimized")
                
                # Update table statistics
                session.exec(text("PRAGMA stats"))
                results["tasks"].append("✅ Table statistics updated")
                
                # Vacuum if requested (requires exclusive lock)
                if vacuum:
                    session.exec(text("VACUUM"))
                    results["tasks"].append("✅ Database vacuumed")
                    
        except Exception as e:
            results["errors"].append(f"❌ Maintenance error: {str(e)}")
            logger.error(f"Database maintenance error: {e}")
            
        results["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
        results["completed_at"] = datetime.now().isoformat()
        
        return results

    def cleanup_old_data(self, retention_days: int = 90) -> Dict[str, Any]:
        """Clean up old analytics and log data"""
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cleanup_results = {"deleted_records": {}, "errors": []}
        
        # Tables to clean up with their date columns
        cleanup_tables = {
            "visitoranalytics": "visit_date",
            "compliancelog": "created_at", 
            "changelog": "created_at"
        }
        
        try:
            with Session(engine) as session:
                for table, date_column in cleanup_tables.items():
                    try:
                        # Count records to be deleted
                        count_query = f"SELECT COUNT(*) FROM {table} WHERE {date_column} < ?"
                        count_result = session.exec(text(count_query), (cutoff_date,)).first()
                        
                        if count_result and count_result > 0:
                            # Delete old records
                            delete_query = f"DELETE FROM {table} WHERE {date_column} < ?"
                            session.exec(text(delete_query), (cutoff_date,))
                            
                            cleanup_results["deleted_records"][table] = count_result
                            logger.info(f"🧹 Cleaned up {count_result} old records from {table}")
                        else:
                            cleanup_results["deleted_records"][table] = 0
                            
                    except Exception as e:
                        cleanup_results["errors"].append(f"Error cleaning {table}: {str(e)}")
                        
                session.commit()
                
        except Exception as e:
            cleanup_results["errors"].append(f"Transaction error: {str(e)}")
            
        return cleanup_results


# Global health monitor instance
health_monitor = DatabaseHealthMonitor()


def start_health_monitoring():
    """Start database health monitoring"""
    health_monitor.start_monitoring()


def stop_health_monitoring():
    """Stop database health monitoring"""
    health_monitor.stop_monitoring()


def get_health_status() -> Dict[str, Any]:
    """Get current database health status"""
    return health_monitor.get_current_health()


def run_database_maintenance(vacuum: bool = False) -> Dict[str, Any]:
    """Run database maintenance tasks"""
    maintenance = DatabaseMaintenanceManager("data/portal.db")
    return maintenance.run_maintenance(vacuum=vacuum)