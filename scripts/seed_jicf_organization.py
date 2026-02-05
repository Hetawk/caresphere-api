"""Seed script to create JICF organization and assign admin user."""

import asyncio
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.organization import Organization
from app.models.user import User


def seed_jicf_organization():
    """Create JICF organization and assign admin user to it."""
    db: Session = SessionLocal()

    try:
        # Check if JICF organization already exists
        jicf_org = db.query(Organization).filter(
            Organization.slug == "jicf").first()

        if not jicf_org:
            # Create JICF organization
            jicf_org = Organization(
                name="Jinan International Christian Fellowship",
                slug="jicf",
                domain="jinanicf.com",
                settings={
                    "location": "Jinan, Shandong, China",
                    "description": "International Christian Fellowship in Jinan"
                },
                is_active=True
            )
            db.add(jicf_org)
            db.commit()
            db.refresh(jicf_org)
            print(f"✅ Created JICF organization: {jicf_org.id}")
        else:
            print(f"✅ JICF organization already exists: {jicf_org.id}")

        # Find admin user and assign to JICF organization
        admin_user = db.query(User).filter(
            User.email == "admin@jinanicf.com").first()

        if admin_user:
            if not admin_user.organization_id:
                admin_user.organization_id = jicf_org.id
                db.commit()
                print(f"✅ Assigned admin@jinanicf.com to JICF organization")
            else:
                print(f"✅ admin@jinanicf.com already assigned to organization")
        else:
            print("⚠️ Warning: admin@jinanicf.com user not found")

        db.commit()
        print("\n🎉 JICF organization setup complete!")
        print(f"Organization ID: {jicf_org.id}")
        print(f"Organization Name: {jicf_org.name}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_jicf_organization()
