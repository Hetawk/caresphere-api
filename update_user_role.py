#!/usr/bin/env python3
"""Quick script to update user role to ADMIN."""

import sys
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

# Import models
from app.models.user import User, UserRole
from app.config import settings


def update_user_role_to_admin(email: str):
    """Update user role to ADMIN."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Find user by email
        user = db.query(User).filter(User.email == email.lower()).first()

        if not user:
            print(f"❌ User with email {email} not found")
            return False

        print(f"Found user: {user.full_name} ({user.email})")
        print(f"Current role: {user.role.value}")

        # Update role to ADMIN
        user.role = UserRole.ADMIN
        db.commit()

        print(f"✅ Successfully updated {user.email} to ADMIN role")
        print(f"   User now has full permissions to manage members, send messages, etc.")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_user_role.py <email>")
        print("Example: python update_user_role.py ekd@ekddigital.com")
        sys.exit(1)

    email = sys.argv[1]
    success = update_user_role_to_admin(email)
    sys.exit(0 if success else 1)
