"""
Database Performance Optimizer für QR-Info-Portal
===================================================

Optimiert SQLite Performance durch:
- Erweiterte Index-Strategien
- Connection Pool Management  
- Query Optimization
- Performance Monitoring
- Backup & Migration Support
"""

import sqlite3
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging
from sqlmodel import create_engine, Session, select, text
from sqlalchemy import event, inspect
from sqlalchemy.pool import StaticPool
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Container for query performance metrics"""
    query: str
    execution_time_ms: float
    rows_examined: int
    rows_returned: int
    used_index: bool
    timestamp: datetime


class DatabaseOptimizer:
    """Advanced SQLite Performance Optimizer"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.metrics: List[QueryMetrics] = []
        self.connection_pool = self._create_optimized_engine()
        self._setup_monitoring()
        
    def _create_optimized_engine(self):
        """Create optimized SQLite engine with performance settings"""
        
        # SQLite optimization parameters
        connect_args = {
            "check_same_thread": False,
            # Performance optimizations
            "timeout": 30,  # 30 second timeout for busy database
        }
        
        # Create engine with optimized settings (SQLite doesn't support all pool options)
        if self.database_url.startswith("sqlite"):
            engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
                echo=False,  # Set to True for SQL debugging
            )
        else:
            # For PostgreSQL and other databases
            engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                pool_size=20,  # Connection pool size
                max_overflow=30,  # Additional connections during peak
                pool_timeout=30,  # Timeout waiting for connection
                pool_recycle=3600,  # Recycle connections hourly
                echo=False,  # Set to True for SQL debugging
            )
        
        # Setup connection event listeners for optimization
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Optimize SQLite settings on each connection"""
            cursor = dbapi_connection.cursor()
            
            # Performance optimizations
            cursor.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA synchronous = NORMAL")  # Balanced safety/performance
            cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache (negative = KB)
            cursor.execute("PRAGMA temp_store = MEMORY")  # Store temporary data in memory
            cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
            cursor.execute("PRAGMA optimize")  # Auto-optimize indexes
            
            # Enable query planner optimization
            cursor.execute("PRAGMA automatic_index = ON")
            cursor.execute("PRAGMA query_only = OFF")
            
            # Foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            cursor.close()
            
        return engine
    
    def _setup_monitoring(self):
        """Setup query performance monitoring"""
        
        @event.listens_for(self.connection_pool, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.perf_counter()
            context._query_statement = statement
            
        @event.listens_for(self.connection_pool, "after_cursor_execute") 
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if hasattr(context, '_query_start_time'):
                execution_time = (time.perf_counter() - context._query_start_time) * 1000
                
                # Only log slow queries (> 10ms) or complex queries
                if execution_time > 10 or any(keyword in statement.upper() for keyword in ['JOIN', 'SUBQUERY', 'ORDER BY']):
                    metric = QueryMetrics(
                        query=statement[:200] + "..." if len(statement) > 200 else statement,
                        execution_time_ms=execution_time,
                        rows_examined=cursor.rowcount if cursor.rowcount >= 0 else 0,
                        rows_returned=cursor.rowcount if cursor.rowcount >= 0 else 0,
                        used_index="INDEX" in statement.upper(),
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metric)
                    
                    # Log very slow queries
                    if execution_time > 100:
                        logger.warning(f"Slow query detected ({execution_time:.2f}ms): {statement[:100]}...")

    def optimize_indexes(self) -> Dict[str, Any]:
        """Create optimized indexes for common query patterns"""
        
        optimization_queries = [
            # Composite indexes for common filter combinations
            "CREATE INDEX IF NOT EXISTS idx_announcement_active_lang_priority ON announcement(active, lang, priority) WHERE active = 1",
            "CREATE INDEX IF NOT EXISTS idx_availability_date_active_type ON availability(availability_date, active, slot_type) WHERE active = 1",
            "CREATE INDEX IF NOT EXISTS idx_hourexception_date_closed ON hourexception(exception_date, closed)",
            
            # Analytics optimizations
            "CREATE INDEX IF NOT EXISTS idx_visitoranalytics_date_time ON visitoranalytics(visit_date, visit_time)",
            "CREATE INDEX IF NOT EXISTS idx_visitoranalytics_session_page ON visitoranalytics(session_hash, page_path)",
            "CREATE INDEX IF NOT EXISTS idx_dailystatistics_date_desc ON dailystatistics(stats_date DESC)",
            
            # Compliance & Security indexes  
            "CREATE INDEX IF NOT EXISTS idx_compliancelog_type_severity_created ON compliancelog(log_type, severity, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_cookieconsent_session_expires ON cookieconsent(session_id, expires_at) WHERE expires_at > datetime('now')",
            "CREATE INDEX IF NOT EXISTS idx_datasubjectrequest_status_deadline ON datasubjectrequest(status, deadline)",
            
            # Social Media optimizations
            "CREATE INDEX IF NOT EXISTS idx_socialmediapost_platform_active_scheduled ON socialmediapost(platform, active, scheduled_for) WHERE active = 1",
            "CREATE INDEX IF NOT EXISTS idx_shareablecontent_type_active_shared ON shareablecontent(content_type, active, last_shared) WHERE active = 1",
            
            # Admin & Change tracking
            "CREATE INDEX IF NOT EXISTS idx_changelog_table_action_created ON changelog(table_name, action, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_changelog_rollback_status ON changelog(is_rolled_back, created_at) WHERE is_rolled_back = 0",
            "CREATE INDEX IF NOT EXISTS idx_adminuser_username_locked ON adminuser(username, locked_until)",
            
            # Legal document indexes
            "CREATE INDEX IF NOT EXISTS idx_legaldocument_type_lang_active ON legaldocument(document_type, language, is_active) WHERE is_active = 1",
            "CREATE INDEX IF NOT EXISTS idx_dataprocessingpurpose_active_consent ON dataprocessingpurpose(is_active, requires_explicit_consent) WHERE is_active = 1",
        ]
        
        results = {
            "created_indexes": [],
            "failed_indexes": [],
            "execution_time_ms": 0
        }
        
        start_time = time.perf_counter()
        
        with Session(self.connection_pool) as session:
            for query in optimization_queries:
                try:
                    session.exec(text(query))
                    session.commit()
                    index_name = query.split("CREATE INDEX IF NOT EXISTS ")[1].split(" ")[0]
                    results["created_indexes"].append(index_name)
                    logger.info(f"✅ Created index: {index_name}")
                except Exception as e:
                    results["failed_indexes"].append(f"{query[:50]}... - Error: {str(e)}")
                    logger.error(f"❌ Failed to create index: {e}")
                    
        results["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
        return results

    def analyze_query_performance(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Analyze performance of a specific query"""
        
        with Session(self.connection_pool) as session:
            # Get query plan
            plan_query = f"EXPLAIN QUERY PLAN {query}"
            plan_result = session.exec(text(plan_query)).all()
            
            # Execute query with timing
            start_time = time.perf_counter()
            if params:
                result = session.exec(text(query), params).all()
            else:
                result = session.exec(text(query)).all()
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return {
                "query": query,
                "execution_time_ms": execution_time,
                "rows_returned": len(result),
                "query_plan": [str(row) for row in plan_result],
                "uses_index": any("INDEX" in str(row) for row in plan_result),
                "recommendations": self._analyze_query_plan(plan_result)
            }

    def _analyze_query_plan(self, plan_result) -> List[str]:
        """Analyze query plan and provide optimization recommendations"""
        recommendations = []
        
        plan_text = " ".join(str(row) for row in plan_result)
        
        if "SCAN TABLE" in plan_text:
            recommendations.append("⚠️ Full table scan detected - consider adding an index")
            
        if "TEMP B-TREE" in plan_text:
            recommendations.append("⚠️ Temporary B-tree for ORDER BY - consider covering index")
            
        if "USING INDEX" in plan_text:
            recommendations.append("✅ Query uses index efficiently")
            
        if not recommendations:
            recommendations.append("✅ Query plan looks optimal")
            
        return recommendations

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        
        with Session(self.connection_pool) as session:
            # Database size and fragmentation - get scalar values
            db_size_result = session.exec(text("PRAGMA page_count")).first()
            page_size_result = session.exec(text("PRAGMA page_size")).first()
            freelist_result = session.exec(text("PRAGMA freelist_count")).first()
            
            # Extract numeric values (handle both Row objects and direct values)
            db_size = db_size_result[0] if hasattr(db_size_result, '__getitem__') else db_size_result
            page_size = page_size_result[0] if hasattr(page_size_result, '__getitem__') else page_size_result
            freelist_count = freelist_result[0] if hasattr(freelist_result, '__getitem__') else freelist_result
            
            # Cache hit ratio
            cache_stats = {}
            try:
                cache_result = session.exec(text("PRAGMA cache_size")).first()
                cache_hits = cache_result[0] if hasattr(cache_result, '__getitem__') else cache_result
                cache_stats["cache_size_kb"] = abs(cache_hits) if cache_hits < 0 else cache_hits * page_size / 1024
            except:
                cache_stats = {"cache_size_kb": "unknown"}
            
            # Connection pool stats (SQLite uses StaticPool)
            try:
                if hasattr(self.connection_pool.pool, 'size'):
                    pool_stats = {
                        "size": self.connection_pool.pool.size(),
                        "checked_out": self.connection_pool.pool.checkedout(),
                        "overflow": self.connection_pool.pool.overflow(),
                        "total_connections": self.connection_pool.pool.size() + self.connection_pool.pool.overflow()
                    }
                else:
                    # SQLite StaticPool doesn't have these methods
                    pool_stats = {
                        "size": 1,  # SQLite is single-connection
                        "checked_out": 0,
                        "overflow": 0,
                        "total_connections": 1,
                        "pool_type": "StaticPool (SQLite)"
                    }
            except AttributeError:
                pool_stats = {
                    "size": 1,
                    "checked_out": 0, 
                    "overflow": 0,
                    "total_connections": 1,
                    "note": "Pool stats not available for SQLite"
                }
            
            # Recent query metrics
            recent_queries = [
                {
                    "query": m.query,
                    "time_ms": m.execution_time_ms,
                    "timestamp": m.timestamp.isoformat()
                } 
                for m in self.metrics[-10:]  # Last 10 queries
            ]
            
            return {
                "database": {
                    "size_mb": (db_size * page_size) / (1024 * 1024),
                    "pages": db_size,
                    "page_size": page_size,
                    "fragmentation_pages": freelist_count,
                    "fragmentation_percent": (freelist_count / db_size * 100) if db_size > 0 else 0
                },
                "cache": cache_stats,
                "connection_pool": pool_stats,
                "query_metrics": {
                    "total_monitored_queries": len(self.metrics),
                    "avg_execution_time_ms": sum(m.execution_time_ms for m in self.metrics) / len(self.metrics) if self.metrics else 0,
                    "slow_queries_count": len([m for m in self.metrics if m.execution_time_ms > 100]),
                    "recent_queries": recent_queries
                }
            }

    def vacuum_optimize(self) -> Dict[str, Any]:
        """Perform database maintenance and optimization"""
        
        start_time = time.perf_counter()
        results = {"operations": [], "errors": []}
        
        with Session(self.connection_pool) as session:
            try:
                # Analyze database statistics
                session.exec(text("ANALYZE"))
                results["operations"].append("✅ ANALYZE completed")
                
                # Optimize query planner statistics  
                session.exec(text("PRAGMA optimize"))
                results["operations"].append("✅ PRAGMA optimize completed")
                
                # Note: VACUUM requires exclusive lock, skip in production
                # session.exec(text("VACUUM"))
                # results["operations"].append("✅ VACUUM completed")
                
            except Exception as e:
                results["errors"].append(f"❌ Error during optimization: {str(e)}")
                logger.error(f"Database optimization error: {e}")
        
        results["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
        return results

    @contextmanager
    def get_optimized_session(self):
        """Get database session with performance monitoring"""
        session = Session(self.connection_pool)
        session_start = time.perf_counter()
        
        try:
            yield session
        finally:
            session.close()
            session_duration = (time.perf_counter() - session_start) * 1000
            if session_duration > 500:  # Log sessions longer than 500ms
                logger.warning(f"Long database session: {session_duration:.2f}ms")

    def create_performance_indexes(self) -> Dict[str, Any]:
        """Create specialized performance indexes"""
        
        performance_indexes = [
            # Current status lookup (most frequent query)
            "CREATE INDEX IF NOT EXISTS idx_status_current ON status(type, date_from, date_to) WHERE date_from IS NULL OR date_from <= date('now')",
            
            # Opening hours with day lookup
            "CREATE INDEX IF NOT EXISTS idx_standardhours_day_updated ON standardhours(day_of_week, updated_at DESC)",
            
            # Active announcements by language and date range
            "CREATE INDEX IF NOT EXISTS idx_announcement_active_range ON announcement(active, lang, start_date, end_date) WHERE active = 1",
            
            # Availability slots for date range queries
            "CREATE INDEX IF NOT EXISTS idx_availability_date_range_active ON availability(availability_date, start_time, active) WHERE active = 1",
            
            # Analytics time series indexes
            "CREATE INDEX IF NOT EXISTS idx_visitoranalytics_time_series ON visitoranalytics(visit_date DESC, visit_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_visitoranalytics_session_timeline ON visitoranalytics(session_hash, visit_time ASC)",
            
            # Admin activity tracking
            "CREATE INDEX IF NOT EXISTS idx_changelog_recent_activity ON changelog(table_name, created_at DESC) WHERE is_rolled_back = 0",
            
            # Legal compliance time-sensitive queries
            "CREATE INDEX IF NOT EXISTS idx_cookieconsent_active_sessions ON cookieconsent(session_id, expires_at) WHERE expires_at > datetime('now')",
            "CREATE INDEX IF NOT EXISTS idx_compliancelog_retention ON compliancelog(retention_until, requires_retention) WHERE requires_retention = 1",
        ]
        
        results = {"created": [], "failed": []}
        
        with Session(self.connection_pool) as session:
            for index_sql in performance_indexes:
                try:
                    session.exec(text(index_sql))
                    session.commit()
                    index_name = index_sql.split("IF NOT EXISTS ")[1].split(" ")[0]
                    results["created"].append(index_name)
                except Exception as e:
                    results["failed"].append(f"{index_sql[:50]}... -> {str(e)}")
        
        return results

    def monitor_query_performance(self, query: str, params: Optional[tuple] = None) -> QueryMetrics:
        """Monitor and return performance metrics for a specific query"""
        
        with Session(self.connection_pool) as session:
            # Get query plan first
            plan_query = f"EXPLAIN QUERY PLAN {query}"
            plan_result = session.exec(text(plan_query)).all()
            uses_index = any("INDEX" in str(row) for row in plan_result)
            
            # Execute with timing
            start_time = time.perf_counter()
            if params:
                result = session.exec(text(query), params).all()
            else:
                result = session.exec(text(query)).all()
            execution_time = (time.perf_counter() - start_time) * 1000
            
            metrics = QueryMetrics(
                query=query,
                execution_time_ms=execution_time,
                rows_examined=-1,  # SQLite doesn't provide this easily
                rows_returned=len(result),
                used_index=uses_index,
                timestamp=datetime.now()
            )
            
            self.metrics.append(metrics)
            return metrics

    def get_slow_queries(self, threshold_ms: float = 50.0) -> List[QueryMetrics]:
        """Get list of slow queries above threshold"""
        return [m for m in self.metrics if m.execution_time_ms > threshold_ms]

    def cleanup_old_metrics(self, hours: int = 24):
        """Clean up old performance metrics"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        metrics = self.get_performance_metrics()
        slow_queries = self.get_slow_queries()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "database_metrics": metrics,
            "performance_summary": {
                "total_queries_monitored": len(self.metrics),
                "slow_queries_count": len(slow_queries),
                "average_query_time_ms": metrics["query_metrics"]["avg_execution_time_ms"],
                "database_size_mb": metrics["database"]["size_mb"],
                "fragmentation_percent": metrics["database"]["fragmentation_percent"]
            },
            "slow_queries": [
                {
                    "query": sq.query,
                    "time_ms": sq.execution_time_ms,
                    "used_index": sq.used_index,
                    "timestamp": sq.timestamp.isoformat()
                }
                for sq in slow_queries[-5:]  # Last 5 slow queries
            ],
            "recommendations": self._generate_recommendations(metrics, slow_queries)
        }
        
        return report

    def _generate_recommendations(self, metrics: Dict, slow_queries: List[QueryMetrics]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Database size recommendations
        if metrics["database"]["size_mb"] > 100:
            recommendations.append("📊 Database is large (>100MB) - consider archiving old analytics data")
            
        if metrics["database"]["fragmentation_percent"] > 20:
            recommendations.append("🗂️ High fragmentation detected - run VACUUM during maintenance window")
            
        # Query performance recommendations
        if metrics["query_metrics"]["avg_execution_time_ms"] > 25:
            recommendations.append("⚡ Average query time is high - review slow queries and add indexes")
            
        if len(slow_queries) > 10:
            recommendations.append("🐌 Many slow queries detected - optimize most frequent patterns")
            
        # Connection pool recommendations
        pool_usage = metrics["connection_pool"]["checked_out"] / metrics["connection_pool"]["size"]
        if pool_usage > 0.8:
            recommendations.append("🔗 High connection pool usage - consider increasing pool size")
            
        if not recommendations:
            recommendations.append("✅ Database performance looks good")
            
        return recommendations


class DatabaseBackupManager:
    """Manages database backups and migrations"""
    
    def __init__(self, database_path: str, backup_dir: str = "backups"):
        self.database_path = database_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create database backup with timestamp"""
        
        if not backup_name:
            backup_name = f"portal_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
        backup_path = self.backup_dir / backup_name
        
        try:
            start_time = time.perf_counter()
            
            # Use SQLite backup API for consistent backup
            source = sqlite3.connect(self.database_path)
            backup = sqlite3.connect(str(backup_path))
            source.backup(backup)
            source.close()
            backup.close()
            
            backup_time = (time.perf_counter() - start_time) * 1000
            backup_size = backup_path.stat().st_size
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_size_bytes": backup_size,
                "backup_time_ms": backup_time,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "attempted_path": str(backup_path)
            }

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        
        backups = []
        for backup_file in self.backup_dir.glob("*.db"):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "age_hours": (datetime.now().timestamp() - stat.st_ctime) / 3600
            })
            
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up backups older than specified days"""
        
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        deleted_backups = []
        total_freed_bytes = 0
        
        for backup_file in self.backup_dir.glob("*.db"):
            stat = backup_file.stat()
            if datetime.fromtimestamp(stat.st_ctime) < cutoff_time:
                size = stat.st_size
                backup_file.unlink()
                deleted_backups.append({
                    "name": backup_file.name,
                    "size_mb": size / (1024 * 1024)
                })
                total_freed_bytes += size
                
        return {
            "deleted_count": len(deleted_backups),
            "freed_space_mb": total_freed_bytes / (1024 * 1024),
            "deleted_backups": deleted_backups
        }


class PostgreSQLMigrator:
    """Handles migration from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        
    def generate_postgresql_schema(self) -> str:
        """Generate PostgreSQL schema from SQLite database"""
        
        # Type mapping from SQLite to PostgreSQL
        type_mapping = {
            'INTEGER': 'INTEGER',
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT',
            'BOOLEAN': 'BOOLEAN', 
            'DATE': 'DATE',
            'DATETIME': 'TIMESTAMP',
            'TIME': 'TIME',
            'FLOAT': 'REAL',
            'JSON': 'JSONB'  # PostgreSQL's better JSON type
        }
        
        schema_sql = []
        schema_sql.append("-- PostgreSQL Schema Migration from SQLite")
        schema_sql.append("-- Generated on: " + datetime.now().isoformat())
        schema_sql.append("")
        
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_sql.append(f"-- Table: {table_name}")
            schema_sql.append(f"CREATE TABLE {table_name} (")
            
            col_definitions = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = " NOT NULL" if col[3] else ""
                default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                primary_key = " PRIMARY KEY" if col[5] else ""
                
                # Map SQLite type to PostgreSQL
                pg_type = type_mapping.get(col_type, col_type)
                
                col_def = f"    {col_name} {pg_type}{primary_key}{not_null}{default}"
                col_definitions.append(col_def)
                
            schema_sql.append(",\n".join(col_definitions))
            schema_sql.append(");")
            schema_sql.append("")
            
        # Add indexes
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
        indexes = cursor.fetchall()
        
        if indexes:
            schema_sql.append("-- Indexes")
            for idx in indexes:
                # Convert SQLite index syntax to PostgreSQL
                index_sql = idx[2].replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
                schema_sql.append(f"{index_sql};")
            schema_sql.append("")
            
        conn.close()
        return "\n".join(schema_sql)

    def export_data_for_postgresql(self) -> Dict[str, Any]:
        """Export data in PostgreSQL-compatible format"""
        
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        export_data = {}
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            export_data[table_name] = {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
            
        conn.close()
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_tables": len(tables),
            "tables": export_data
        }


def optimize_database(database_path: str) -> Dict[str, Any]:
    """Main optimization function - runs all optimizations"""
    
    optimizer = DatabaseOptimizer(f"sqlite:///{database_path}")
    
    print("🔧 Starting database optimization...")
    
    # Run optimizations
    index_results = optimizer.optimize_indexes()
    performance_indexes = optimizer.create_performance_indexes() 
    vacuum_results = optimizer.vacuum_optimize()
    metrics = optimizer.get_performance_metrics()
    
    # Generate report
    report = {
        "optimization_timestamp": datetime.now().isoformat(),
        "database_path": database_path,
        "index_optimization": index_results,
        "performance_indexes": performance_indexes,
        "maintenance": vacuum_results,
        "current_metrics": metrics,
        "recommendations": optimizer._generate_recommendations(metrics, optimizer.get_slow_queries())
    }
    
    print(f"✅ Database optimization completed")
    print(f"   - Created {len(index_results['created_indexes'])} standard indexes")
    print(f"   - Created {len(performance_indexes['created'])} performance indexes") 
    print(f"   - Database size: {metrics['database']['size_mb']:.2f} MB")
    print(f"   - Fragmentation: {metrics['database']['fragmentation_percent']:.1f}%")
    
    return report


if __name__ == "__main__":
    # Run optimization on default database
    db_path = "data/portal.db"
    if os.path.exists(db_path):
        report = optimize_database(db_path)
        
        # Save report
        report_path = f"database_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"📊 Performance report saved to: {report_path}")
    else:
        print(f"❌ Database not found: {db_path}")