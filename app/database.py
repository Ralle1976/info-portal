from sqlmodel import create_engine, SQLModel, Session, select
from pathlib import Path
import os

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{data_dir}/portal.db")

# Create optimized engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # 30 second timeout for busy database
    },
    pool_size=10,  # Connection pool size  
    max_overflow=20,  # Additional connections during peak
    pool_timeout=30,  # Timeout waiting for connection
    pool_recycle=3600,  # Recycle connections hourly
    echo=False  # Set to True for SQL debugging
)

# Setup SQLite optimization on connect
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Optimize SQLite settings on each connection"""
    cursor = dbapi_connection.cursor()
    
    # Performance optimizations
    cursor.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA synchronous = NORMAL")  # Balanced safety/performance  
    cursor.execute("PRAGMA cache_size = -32000")  # 32MB cache (negative = KB)
    cursor.execute("PRAGMA temp_store = MEMORY")  # Store temporary data in memory
    cursor.execute("PRAGMA mmap_size = 134217728")  # 128MB memory-mapped I/O
    cursor.execute("PRAGMA optimize")  # Auto-optimize indexes
    
    # Enable query planner optimization
    cursor.execute("PRAGMA automatic_index = ON")
    
    # Foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.close()


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    return Session(engine)


def db_session_context():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def init_database():
    """Initialize database with default data"""
    from app.models import StandardHours, Settings, SocialMediaConfig, AdminUser
    import yaml
    from datetime import datetime
    
    create_db_and_tables()
    
    # Load config
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    with Session(engine) as session:
        # Check if already initialized
        existing = session.query(Settings).filter_by(key="initialized").first()
        if existing:
            # Check if social media migration is needed
            social_migrated = session.query(Settings).filter_by(key="social_media_migrated").first()
            if not social_migrated:
                _migrate_social_media_config(session, config)
            return
        
        # Create standard hours from config
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for i, day in enumerate(days):
            hours = StandardHours(
                day_of_week=i,
                time_ranges=config['hours']['weekly'].get(day, [])
            )
            session.add(hours)
        
        # Initialize social media configurations
        _initialize_social_media_config(session, config)
        
        # Initialize default admin user if none exists
        existing_admin = session.exec(select(AdminUser)).first()
        if not existing_admin:
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            default_admin = AdminUser(username=admin_username)
            default_admin.set_password(admin_password)
            session.add(default_admin)
            print(f"✅ Created default admin user: {admin_username}")
        
        # Mark as initialized
        session.add(Settings(
            key="initialized",
            value={"date": datetime.utcnow().isoformat()}
        ))
        
        # Store site config
        session.add(Settings(
            key="site_config",
            value=config
        ))
        
        session.commit()


def _initialize_social_media_config(session, config):
    """Initialize social media platform configurations"""
    from app.models import SocialMediaConfig
    from sqlmodel import select
    
    social_config = config.get('social_media', {})
    platforms = social_config.get('platforms', {})
    
    for platform_name, platform_data in platforms.items():
        # Check if platform already exists
        existing = session.exec(
            select(SocialMediaConfig).where(SocialMediaConfig.platform == platform_name)
        ).first()
        
        if not existing:
            social_media_config = SocialMediaConfig(
                platform=platform_name,
                enabled=platform_data.get('enabled', False),
                config=platform_data,
                qr_enabled=platform_data.get('qr_enabled', False)
            )
            session.add(social_media_config)


def _migrate_social_media_config(session, config):
    """Migrate social media configuration for existing installations"""
    from app.models import Settings
    from datetime import datetime
    
    try:
        _initialize_social_media_config(session, config)
        
        # Mark social media as migrated
        session.add(Settings(
            key="social_media_migrated",
            value={"date": datetime.utcnow().isoformat()}
        ))
        
        session.commit()
        print("✅ Social Media configuration migrated successfully")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error migrating social media config: {e}")


def migrate_database():
    """Run database migrations"""
    from app.models import Settings
    import yaml
    from datetime import datetime
    
    print("🔄 Running database migrations...")
    
    # Ensure all tables exist
    create_db_and_tables()
    
    # Load current config
    try:
        with open('config.yml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("⚠️  config.yml not found, skipping migrations")
        return
    
    with Session(engine) as session:
        # Check and run social media migration
        social_migrated = session.query(Settings).filter_by(key="social_media_migrated").first()
        if not social_migrated:
            print("🆕 Running social media migration...")
            _migrate_social_media_config(session, config)
        else:
            print("✅ Social media already migrated")
    
    print("✅ Database migrations completed")