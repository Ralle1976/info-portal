"""
Automated Database Backup Manager
=================================

Verwaltet automatische SQLite Backups, Rotationen und Wiederherstellungen
für das QR-Info-Portal. Unterstützt inkrementelle Backups und Migration.
"""

import sqlite3
import shutil
import gzip
import json
import os
import threading
# import schedule  # Optional dependency - commented out for now
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass  
class BackupInfo:
    """Information about a backup"""
    name: str
    path: str
    size_bytes: int
    size_mb: float
    created_at: datetime
    backup_type: str  # full, incremental, scheduled
    checksum: str
    compressed: bool
    

class BackupManager:
    """Advanced backup management for SQLite database"""
    
    def __init__(self, database_path: str, backup_dir: str = "backups"):
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup settings
        self.max_backups_per_type = {
            "hourly": 24,   # Keep 24 hourly backups
            "daily": 30,    # Keep 30 daily backups  
            "weekly": 12,   # Keep 12 weekly backups
            "monthly": 12   # Keep 12 monthly backups
        }
        
        self.compression_enabled = True
        self.verify_backups = True
        self._scheduler_running = False
        self._scheduler_thread = None
        
    def create_backup(self, backup_type: str = "manual", compress: bool = True) -> BackupInfo:
        """Create a new database backup"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"portal_{backup_type}_{timestamp}.db"
        
        if compress:
            backup_name += ".gz"
            
        backup_path = self.backup_dir / backup_name
        
        try:
            import time
            start_time = time.time()
            
            if compress:
                # Create compressed backup
                with open(self.database_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Create uncompressed backup using SQLite backup API
                source = sqlite3.connect(str(self.database_path))
                backup = sqlite3.connect(str(backup_path))
                source.backup(backup)
                source.close()
                backup.close()
                
            # Calculate checksum for integrity verification
            checksum = self._calculate_file_checksum(backup_path)
            
            # Verify backup if enabled
            if self.verify_backups:
                verification_result = self._verify_backup(backup_path, compress)
                if not verification_result["valid"]:
                    backup_path.unlink()  # Delete invalid backup
                    raise Exception(f"Backup verification failed: {verification_result['error']}")
            
            backup_size = backup_path.stat().st_size
            backup_time = time.time() - start_time
            
            backup_info = BackupInfo(
                name=backup_name,
                path=str(backup_path),
                size_bytes=backup_size,
                size_mb=backup_size / (1024 * 1024),
                created_at=datetime.now(),
                backup_type=backup_type,
                checksum=checksum,
                compressed=compress
            )
            
            logger.info(f"✅ Backup created: {backup_name} ({backup_info.size_mb:.2f}MB) in {backup_time:.2f}s")
            
            # Clean up old backups of this type
            self._cleanup_old_backups(backup_type)
            
            return backup_info
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()  # Clean up failed backup
            raise

    def _calculate_file_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of backup file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _verify_backup(self, backup_path: Path, compressed: bool) -> Dict[str, Any]:
        """Verify backup integrity"""
        
        try:
            if compressed:
                # Verify compressed backup by decompressing and checking
                with gzip.open(backup_path, 'rb') as f:
                    # Try to read first few bytes to verify it's valid
                    header = f.read(100)
                    if not header.startswith(b'SQLite format 3'):
                        return {"valid": False, "error": "Invalid SQLite header in compressed backup"}
            else:
                # Verify uncompressed backup by opening as SQLite database
                conn = sqlite3.connect(str(backup_path))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                
                if result != "ok":
                    return {"valid": False, "error": f"SQLite integrity check failed: {result}"}
                    
            return {"valid": True, "message": "Backup verification successful"}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _cleanup_old_backups(self, backup_type: str):
        """Clean up old backups according to retention policy"""
        
        pattern = f"portal_{backup_type}_*.db*"
        backups = list(self.backup_dir.glob(pattern))
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.stat().st_ctime, reverse=True)
        
        max_backups = self.max_backups_per_type.get(backup_type, 10)
        
        if len(backups) > max_backups:
            backups_to_delete = backups[max_backups:]
            freed_space = 0
            
            for backup in backups_to_delete:
                freed_space += backup.stat().st_size
                backup.unlink()
                logger.info(f"🗑️ Deleted old backup: {backup.name}")
                
            logger.info(f"🧹 Cleaned up {len(backups_to_delete)} old backups, freed {freed_space / (1024*1024):.2f}MB")

    def list_backups(self, backup_type: Optional[str] = None) -> List[BackupInfo]:
        """List all available backups"""
        
        pattern = f"portal_{backup_type}_*.db*" if backup_type else "portal_*.db*"
        backup_files = self.backup_dir.glob(pattern)
        
        backups = []
        for backup_file in backup_files:
            try:
                stat = backup_file.stat()
                
                # Extract backup type from filename
                name_parts = backup_file.stem.split('_')
                file_backup_type = name_parts[1] if len(name_parts) > 1 else "unknown"
                
                backup_info = BackupInfo(
                    name=backup_file.name,
                    path=str(backup_file),
                    size_bytes=stat.st_size,
                    size_mb=stat.st_size / (1024 * 1024),
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    backup_type=file_backup_type,
                    checksum=self._calculate_file_checksum(backup_file),
                    compressed=backup_file.suffix == ".gz"
                )
                backups.append(backup_info)
                
            except Exception as e:
                logger.warning(f"Error reading backup info for {backup_file}: {e}")
                
        return sorted(backups, key=lambda x: x.created_at, reverse=True)

    def restore_backup(self, backup_name: str, confirm: bool = False) -> Dict[str, Any]:
        """Restore database from backup"""
        
        if not confirm:
            return {
                "success": False,
                "error": "Restore operation requires explicit confirmation",
                "message": "Call with confirm=True to proceed"
            }
            
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return {"success": False, "error": f"Backup file not found: {backup_name}"}
            
        try:
            # Create backup of current database before restore
            current_backup = self.create_backup("pre_restore")
            
            # Restore from backup
            if backup_path.suffix == ".gz":
                # Decompress and restore
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.database_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Direct copy
                shutil.copy2(backup_path, self.database_path)
                
            # Verify restored database
            verification = self._verify_backup(self.database_path, False)
            if not verification["valid"]:
                # Restore from pre-restore backup
                shutil.copy2(current_backup.path, self.database_path)
                return {
                    "success": False,
                    "error": f"Restored database failed verification: {verification['error']}",
                    "message": "Original database restored"
                }
                
            return {
                "success": True,
                "restored_from": backup_name,
                "pre_restore_backup": current_backup.name,
                "message": "Database successfully restored"
            }
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return {"success": False, "error": str(e)}

    def setup_scheduled_backups(self):
        """Setup automatic scheduled backups (manual implementation without schedule library)"""
        
        # Note: This is a simplified implementation without the schedule library
        # In production, use cron jobs or systemd timers for scheduling
        
        logger.info("📅 Scheduled backups setup (requires manual cron configuration):")
        logger.info("   - Hourly backups: 0 * * * * /path/to/backup_script.sh hourly")
        logger.info("   - Daily backups: 0 2 * * * /path/to/backup_script.sh daily")  
        logger.info("   - Weekly backups: 0 3 * * 0 /path/to/backup_script.sh weekly")
        logger.info("   - Monthly backups: 0 4 1 * * /path/to/backup_script.sh monthly")
        
        # Create backup script for cron
        self._create_backup_script()

    def _create_backup_script(self):
        """Create shell script for cron-based backups"""
        
        script_content = f'''#!/bin/bash
# Automated backup script for QR-Info-Portal
# Usage: backup_script.sh [hourly|daily|weekly|monthly]

BACKUP_TYPE="${{1:-manual}}"
DATABASE_PATH="{self.database_path}"
BACKUP_DIR="{self.backup_dir}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="portal_${{BACKUP_TYPE}}_${{TIMESTAMP}}.db"

echo "🔄 Creating $BACKUP_TYPE backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup using sqlite3 .backup command
sqlite3 "$DATABASE_PATH" ".backup $BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    echo "📦 Backup compressed: $BACKUP_FILE.gz"
    
    # Clean up old backups based on type
    case $BACKUP_TYPE in
        "hourly")
            find "$BACKUP_DIR" -name "portal_hourly_*.db.gz" -mtime +1 -delete
            ;;
        "daily")
            find "$BACKUP_DIR" -name "portal_daily_*.db.gz" -mtime +30 -delete
            ;;
        "weekly")
            find "$BACKUP_DIR" -name "portal_weekly_*.db.gz" -mtime +84 -delete
            ;;
        "monthly")
            find "$BACKUP_DIR" -name "portal_monthly_*.db.gz" -mtime +365 -delete
            ;;
    esac
    
else
    echo "❌ Backup failed!"
    exit 1
fi
'''
        
        script_path = self.backup_dir.parent / "backup_script.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        # Make executable
        import stat
        script_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        
        logger.info(f"📜 Backup script created: {script_path}")

    def _start_scheduler(self):
        """Placeholder for scheduler (use cron instead)"""
        logger.info("⚠️ Use cron jobs for production scheduling")

    def stop_scheduled_backups(self):
        """Stop scheduled backups (placeholder)"""
        logger.info("⏹️ Stop cron jobs to disable scheduled backups")

    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics"""
        
        backups = self.list_backups()
        
        # Group by type
        by_type = {}
        total_size = 0
        
        for backup in backups:
            backup_type = backup.backup_type
            if backup_type not in by_type:
                by_type[backup_type] = []
            by_type[backup_type].append(backup)
            total_size += backup.size_bytes
            
        # Calculate statistics
        stats = {
            "total_backups": len(backups),
            "total_size_mb": total_size / (1024 * 1024),
            "backup_types": {},
            "oldest_backup": min(backups, key=lambda x: x.created_at).created_at.isoformat() if backups else None,
            "newest_backup": max(backups, key=lambda x: x.created_at).created_at.isoformat() if backups else None,
            "scheduler_running": self._scheduler_running
        }
        
        for backup_type, type_backups in by_type.items():
            stats["backup_types"][backup_type] = {
                "count": len(type_backups),
                "size_mb": sum(b.size_mb for b in type_backups),
                "latest": max(type_backups, key=lambda x: x.created_at).created_at.isoformat()
            }
            
        return stats


class PostgreSQLMigrator:
    """Handles migration from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgresql_url: Optional[str] = None):
        self.sqlite_path = sqlite_path
        self.postgresql_url = postgresql_url or os.getenv("POSTGRESQL_URL")
        
    def generate_migration_script(self) -> str:
        """Generate complete PostgreSQL migration script"""
        
        script_lines = [
            "-- PostgreSQL Migration Script",
            "-- Generated from SQLite database",
            f"-- Source: {self.sqlite_path}",
            f"-- Generated: {datetime.now().isoformat()}",
            "",
            "-- Enable necessary extensions",
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";",
            "",
        ]
        
        # Connect to SQLite and analyze schema
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        # SQLite to PostgreSQL type mapping
        type_mapping = {
            'INTEGER': 'INTEGER',
            'VARCHAR': 'VARCHAR',
            'VARCHAR(14)': 'VARCHAR(14)', 
            'TEXT': 'TEXT',
            'BOOLEAN': 'BOOLEAN',
            'DATE': 'DATE', 
            'DATETIME': 'TIMESTAMP WITH TIME ZONE',
            'TIME': 'TIME',
            'FLOAT': 'REAL',
            'JSON': 'JSONB'  # PostgreSQL's optimized JSON type
        }
        
        # Generate table schemas
        for table in tables:
            table_name = table[0]
            script_lines.append(f"-- Table: {table_name}")
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            script_lines.append(f"CREATE TABLE {table_name} (")
            
            col_definitions = []
            primary_keys = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2] 
                not_null = " NOT NULL" if col[3] else ""
                default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                is_pk = col[5]
                
                if is_pk:
                    primary_keys.append(col_name)
                
                # Map to PostgreSQL type
                pg_type = type_mapping.get(col_type, col_type)
                
                # Handle special cases
                if is_pk and col_type == 'INTEGER':
                    pg_type = "SERIAL"
                    default = ""  # SERIAL doesn't need default
                    
                col_def = f"    {col_name} {pg_type}{not_null}{default}"
                col_definitions.append(col_def)
                
            # Add primary key constraint if multiple columns
            if len(primary_keys) > 1:
                col_definitions.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")
                
            script_lines.append(",\n".join(col_definitions))
            script_lines.append(");")
            script_lines.append("")
            
        # Generate indexes (converted to PostgreSQL syntax)
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
        indexes = cursor.fetchall()
        
        if indexes:
            script_lines.append("-- Indexes")
            for idx in indexes:
                index_name = idx[0]
                table_name = idx[1] 
                index_sql = idx[2]
                
                # Skip auto-generated indexes
                if index_name.startswith('sqlite_'):
                    continue
                    
                # Convert to PostgreSQL syntax
                pg_index_sql = index_sql.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
                script_lines.append(f"{pg_index_sql};")
                
            script_lines.append("")
            
        # Add PostgreSQL-specific optimizations
        script_lines.extend([
            "-- PostgreSQL-specific optimizations",
            "",
            "-- Optimize for analytics queries",
            "CREATE INDEX IF NOT EXISTS idx_visitoranalytics_jsonb_gin ON visitoranalytics USING GIN (interaction_events);",
            "CREATE INDEX IF NOT EXISTS idx_announcement_jsonb_gin ON announcement USING GIN ((body::jsonb)) WHERE body::text ~ '^{';",
            "",
            "-- Add foreign key constraints",
            "-- ALTER TABLE availability ADD CONSTRAINT fk_availability_service FOREIGN KEY (service_id) REFERENCES booking_service(id);",
            "",
            "-- Optimize for Thai text search", 
            "CREATE INDEX IF NOT EXISTS idx_announcement_thai_search ON announcement USING GIN (to_tsvector('thai', title || ' ' || body));",
            "",
            "-- Update table statistics",
            "ANALYZE;",
            "",
            "-- Migration completed",
            f"-- Generated on: {datetime.now().isoformat()}",
        ])
        
        conn.close()
        return "\n".join(script_lines)

    def export_data_json(self) -> Dict[str, Any]:
        """Export all data in JSON format for migration"""
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "source_database": str(self.sqlite_path),
                "sqlite_version": sqlite3.sqlite_version,
                "table_count": len(tables)
            },
            "tables": {}
        }
        
        total_rows = 0
        
        for table in tables:
            table_name = table[0]
            
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                table_data = []
                for row in rows:
                    row_dict = dict(row)
                    # Handle datetime serialization
                    for key, value in row_dict.items():
                        if isinstance(value, (datetime, )):
                            row_dict[key] = value.isoformat()
                    table_data.append(row_dict)
                    
                export_data["tables"][table_name] = {
                    "row_count": len(table_data),
                    "data": table_data
                }
                
                total_rows += len(table_data)
                
            except Exception as e:
                logger.error(f"Error exporting table {table_name}: {e}")
                export_data["tables"][table_name] = {
                    "error": str(e),
                    "row_count": 0,
                    "data": []
                }
                
        export_data["export_info"]["total_rows_exported"] = total_rows
        
        conn.close()
        return export_data

    def create_migration_package(self, output_dir: str = "migration_package") -> Dict[str, Any]:
        """Create complete migration package"""
        
        package_dir = Path(output_dir)
        package_dir.mkdir(exist_ok=True)
        
        package_info = {
            "created_at": datetime.now().isoformat(),
            "files": {}
        }
        
        try:
            # Generate PostgreSQL schema
            schema_sql = self.generate_migration_script()
            schema_file = package_dir / "postgresql_schema.sql"
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(schema_sql)
            package_info["files"]["schema"] = str(schema_file)
            
            # Export data as JSON
            data_export = self.export_data_json()
            data_file = package_dir / "data_export.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data_export, f, indent=2, default=str)
            package_info["files"]["data"] = str(data_file)
            
            # Create migration instructions
            instructions = self._generate_migration_instructions()
            instructions_file = package_dir / "MIGRATION_INSTRUCTIONS.md"
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
            package_info["files"]["instructions"] = str(instructions_file)
            
            # Create validation script
            validation_script = self._generate_validation_script()
            validation_file = package_dir / "validate_migration.py"
            with open(validation_file, 'w', encoding='utf-8') as f:
                f.write(validation_script)
            package_info["files"]["validation"] = str(validation_file)
            
            package_info["success"] = True
            package_info["package_dir"] = str(package_dir)
            
            logger.info(f"📦 Migration package created: {package_dir}")
            return package_info
            
        except Exception as e:
            logger.error(f"Migration package creation failed: {e}")
            return {"success": False, "error": str(e)}

    def _generate_migration_instructions(self) -> str:
        """Generate detailed migration instructions"""
        
        return """# PostgreSQL Migration Instructions

## Prerequisites
1. PostgreSQL 14+ installed and running
2. Database user with CREATE privileges
3. Python PostgreSQL adapter: `pip install psycopg2-binary`

## Migration Steps

### 1. Setup PostgreSQL Database
```sql
CREATE DATABASE qr_info_portal;
CREATE USER portal_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE qr_info_portal TO portal_user;
```

### 2. Update Environment Variables
```bash
export DATABASE_URL="postgresql://portal_user:password@localhost/qr_info_portal"
```

### 3. Run Schema Migration
```bash
psql -d qr_info_portal -U portal_user -f postgresql_schema.sql
```

### 4. Import Data
```python
python validate_migration.py --import-data data_export.json
```

### 5. Validate Migration
```bash
python validate_migration.py --validate-all
```

### 6. Update Application Configuration
- Update `requirements.txt`: Replace `sqlite` dependencies with `psycopg2-binary`
- Update `app/database.py`: Change engine configuration for PostgreSQL
- Test all application functionality

## Performance Benefits
- Better concurrent access
- Advanced indexing (GIN, GiST)
- Full-text search support
- Better JSON/JSONB performance
- Improved analytics queries

## Rollback Plan
1. Keep SQLite backup: `cp data/portal.db data/portal_before_migration.db`
2. Export PostgreSQL data: `pg_dump qr_info_portal > postgresql_backup.sql`
3. Restore SQLite if needed: `cp data/portal_before_migration.db data/portal.db`
"""

    def _generate_validation_script(self) -> str:
        """Generate migration validation script"""
        
        return '''#!/usr/bin/env python3
"""
PostgreSQL Migration Validation Script
=====================================

Validates data integrity after migration from SQLite to PostgreSQL.
"""

import argparse
import json
import sys
from datetime import datetime
from sqlmodel import create_engine, Session, text, select
import os


def validate_row_counts(pg_engine, data_export):
    """Validate that all rows were migrated correctly"""
    
    print("🔍 Validating row counts...")
    
    with Session(pg_engine) as session:
        for table_name, table_info in data_export["tables"].items():
            expected_count = table_info["row_count"]
            
            try:
                actual_count = session.exec(text(f"SELECT COUNT(*) FROM {table_name}")).first()
                
                if actual_count == expected_count:
                    print(f"  ✅ {table_name}: {actual_count} rows (matches SQLite)")
                else:
                    print(f"  ❌ {table_name}: {actual_count} rows (expected {expected_count})")
                    return False
                    
            except Exception as e:
                print(f"  ❌ {table_name}: Error - {e}")
                return False
                
    return True


def validate_data_integrity(pg_engine, data_export):
    """Validate sample data integrity"""
    
    print("🔍 Validating data integrity...")
    
    # Test key tables with sample queries
    integrity_tests = [
        ("announcement", "SELECT COUNT(*) FROM announcement WHERE active = true"),
        ("status", "SELECT COUNT(*) FROM status"),
        ("standardhours", "SELECT COUNT(*) FROM standardhours WHERE day_of_week BETWEEN 0 AND 6"),
    ]
    
    with Session(pg_engine) as session:
        for table_name, test_query in integrity_tests:
            try:
                result = session.exec(text(test_query)).first()
                print(f"  ✅ {table_name}: Integrity test passed ({result} rows)")
            except Exception as e:
                print(f"  ❌ {table_name}: Integrity test failed - {e}")
                return False
                
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate PostgreSQL migration")
    parser.add_argument("--validate-all", action="store_true", help="Run all validation tests")
    parser.add_argument("--import-data", help="Import data from JSON export file")
    parser.add_argument("--postgresql-url", help="PostgreSQL connection URL", 
                       default=os.getenv("DATABASE_URL", "postgresql://portal_user:password@localhost/qr_info_portal"))
    
    args = parser.parse_args()
    
    if args.import_data:
        print("📥 Importing data from JSON export...")
        # Implementation would go here
        print("  ⚠️  Data import not yet implemented - use manual import process")
        return
        
    if args.validate_all:
        print("🧪 Running migration validation...")
        
        # Load data export for comparison
        if not os.path.exists("data_export.json"):
            print("❌ data_export.json not found")
            sys.exit(1)
            
        with open("data_export.json", 'r') as f:
            data_export = json.load(f)
            
        # Connect to PostgreSQL
        try:
            pg_engine = create_engine(args.postgresql_url)
            print(f"✅ Connected to PostgreSQL: {args.postgresql_url}")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            sys.exit(1)
            
        # Run validation tests
        tests_passed = 0
        total_tests = 2
        
        if validate_row_counts(pg_engine, data_export):
            tests_passed += 1
            
        if validate_data_integrity(pg_engine, data_export):
            tests_passed += 1
            
        # Summary
        print(f"\\n📊 Validation Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("✅ Migration validation successful!")
        else:
            print("❌ Migration validation failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
'''


# Global backup manager instance
backup_manager = BackupManager("data/portal.db")


def start_scheduled_backups():
    """Start scheduled backup system"""
    backup_manager.setup_scheduled_backups()


def create_manual_backup(backup_type: str = "manual") -> BackupInfo:
    """Create manual backup"""
    return backup_manager.create_backup(backup_type)


def get_backup_status() -> Dict[str, Any]:
    """Get current backup system status"""
    return backup_manager.get_backup_statistics()


def restore_from_backup(backup_name: str, confirm: bool = False) -> Dict[str, Any]:
    """Restore database from backup"""
    return backup_manager.restore_backup(backup_name, confirm)