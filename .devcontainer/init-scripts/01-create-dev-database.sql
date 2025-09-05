-- Development Database Initialization Script
-- This script sets up the development database for QR-Info-Portal

-- Create development database (if not exists via environment)
-- The main database qr_portal_dev is already created by the environment variable

-- Create test database for testing
CREATE DATABASE IF NOT EXISTS qr_portal_test;

-- Create user for testing (if needed)
-- User is already created via environment variables

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE qr_portal_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE qr_portal_test TO postgres;

-- Log the setup
INSERT INTO pg_stat_statements_info (userid, dbid, queryid, query, calls) 
VALUES (0, 0, 0, 'Development database initialized', 1) 
ON CONFLICT DO NOTHING;

-- Create extensions if needed
\c qr_portal_dev;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c qr_portal_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Switch back to default database
\c postgres;

-- Log completion
SELECT 'QR-Info-Portal development databases initialized successfully' AS status;