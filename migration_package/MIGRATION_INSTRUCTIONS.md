# PostgreSQL Migration Instructions

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
