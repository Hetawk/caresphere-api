"""Initialize database with all tables."""

import logging
import os
DEFAULT_ADMIN_EMAIL = os.getenv("CARESPHERE_ADMIN_EMAIL", "admin@caresphere.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("CARESPHERE_ADMIN_PASSWORD", "admin123")

from sqlalchemy import text

from app.database import engine, Base
from app.models.user import User, UserRole, UserStatus
from app.models.member import Member
from app.models.message import Message, MessageRecipient
from app.models.template import Template
from app.models.setting import SenderSetting, SettingScope
from app.models.automation import AutomationRule
from app.models.organization import Organization
from app.utils import security

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Create all database tables."""
    logger.info("Creating database tables...")

    # Disable foreign key checks temporarily
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        conn.commit()

    # Drop all tables first (for clean slate)
    logger.info("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    # Re-enable foreign key checks
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        conn.commit()

    # Create all tables
    logger.info("Creating fresh tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Database tables created successfully!")
    
    # Verify tables were created
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = DATABASE()"
        ))
        tables = [row[0] for row in result]
        logger.info(f"Tables created: {', '.join(tables)}")


def create_default_admin():
    """Create a default admin user if none exists."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()

        if not admin_exists:
            logger.info("Creating default admin user...")
            admin = User(
                email=DEFAULT_ADMIN_EMAIL,
                full_name="System Administrator",
                display_name="Admin",
                password_hash=security.get_password_hash(DEFAULT_ADMIN_PASSWORD),
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                email_verified=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("✅ Default admin user created!")
            logger.info("   Email: %s", DEFAULT_ADMIN_EMAIL)
            logger.info("   Password: %s", DEFAULT_ADMIN_PASSWORD)
            logger.info("   ⚠️  Please change this password immediately!")
        else:
            logger.info("Admin user already exists, skipping creation.")
    except Exception as exc:
        logger.error("Error creating admin user: %s", exc)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🚀 Initializing CareSphere database...")
    init_database()
    create_default_admin()
    logger.info("✅ Database initialization complete!")
