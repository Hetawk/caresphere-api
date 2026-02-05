#!/usr/bin/env python3
"""Update admin@jinanicf.com to SUPER_ADMIN role."""

import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole


def update_admin_user():
    """Update admin@jinanicf.com to SUPER_ADMIN role."""
    db = SessionLocal()
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == "admin@jinanicf.com").first()
        
        if not user:
            print("❌ User admin@jinanicf.com not found!")
            print("   Please register this account first in the app.")
            return False
        
        print(f"✅ Found user: {user.email}")
        print(f"   Current role: {user.role}")
        print(f"   Current status: {user.status}")
        
        # Update to SUPER_ADMIN
        user.role = UserRole.SUPER_ADMIN
        
        db.commit()
        db.refresh(user)
        
        print(f"\n🎉 Successfully updated user to SUPER_ADMIN!")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Full Name: {user.full_name}")
        
        print("\n📝 Permissions granted:")
        print("   ✓ Manage Users")
        print("   ✓ Manage Members")
        print("   ✓ Send Messages")
        print("   ✓ View Analytics")
        print("   ✓ Manage Automation")
        print("   ✓ Manage Templates")
        print("   ✓ Manage Organization")
        print("   ✓ Manage Settings")
        print("   ✓ Export Data")
        print("   ✓ Delete Data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Updating admin user role...\n")
    success = update_admin_user()
    sys.exit(0 if success else 1)
