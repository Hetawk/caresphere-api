"""Complete setup script for JICF organization with RBAC.

This script:
1. Creates JICF organization
2. Creates system roles for JICF
3. Assigns admin user as organization owner with super_admin role
"""

import sys
from pathlib import Path
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role, Permission, OrganizationUser


# System role definitions with their permissions
SYSTEM_ROLES = {
    "super_admin": {
        "display_name": "Super Admin",
        "description": "Full access to all features and settings",
        "color": "#DC2626",  # Red
        "permissions": "all",  # Special marker for all permissions
    },
    "admin": {
        "display_name": "Administrator",
        "description": "Manage members, messages, and most features",
        "color": "#EA580C",  # Orange
        "permissions": [
            "view_members", "manage_members", "export_members", "import_members",
            "view_messages", "send_messages", "manage_templates", "delete_messages",
            "view_automation", "manage_automation", "execute_automation",
            "view_analytics", "export_reports",
            "view_roles", "assign_roles",
            "view_settings",
        ],
    },
    "ministry_leader": {
        "display_name": "Ministry Leader",
        "description": "Manage members and communications for ministry",
        "color": "#0891B2",  # Cyan
        "permissions": [
            "view_members", "manage_members", "export_members",
            "view_messages", "send_messages", "manage_templates",
            "view_automation",
            "view_analytics",
        ],
    },
    "volunteer": {
        "display_name": "Volunteer",
        "description": "View members and send messages",
        "color": "#059669",  # Green
        "permissions": [
            "view_members",
            "view_messages", "send_messages",
            "view_analytics",
        ],
    },
    "member": {
        "display_name": "Member",
        "description": "Basic access to view information",
        "color": "#6B7280",  # Gray
        "permissions": [
            "view_members",
            "view_messages",
        ],
    },
}


def create_organization_roles(db: Session, organization_id: str):
    """Create system roles for an organization."""
    print("\nCreating system roles...")
    
    # Get all permissions
    all_permissions = db.query(Permission).all()
    permissions_map = {p.name: p for p in all_permissions}
    
    roles_created = {}
    
    for role_name, role_config in SYSTEM_ROLES.items():
        # Check if role already exists
        existing_role = db.query(Role).filter(
            Role.organization_id == organization_id,
            Role.name == role_name
        ).first()
        
        if existing_role:
            print(f"  ✓ Role '{role_name}' already exists")
            roles_created[role_name] = existing_role
            continue
        
        # Create role
        role = Role(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            name=role_name,
            display_name=role_config["display_name"],
            description=role_config["description"],
            color=role_config["color"],
            is_system=True,  # System roles cannot be deleted
            is_active=True
        )
        
        # Assign permissions
        if role_config["permissions"] == "all":
            role.permissions = all_permissions
        else:
            role.permissions = [
                permissions_map[perm_name]
                for perm_name in role_config["permissions"]
                if perm_name in permissions_map
            ]
        
        db.add(role)
        roles_created[role_name] = role
        print(f"  + Created role: {role_name} with {len(role.permissions)} permissions")
    
    db.commit()
    print(f"\n✅ Created {len(roles_created)} system roles\n")
    
    return roles_created


def main():
    """Run the complete setup."""
    print("=" * 70)
    print("JICF Organization Setup with RBAC")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    
    try:
        # Step 1: Create JICF organization
        print("Step 1: Creating JICF organization...")
        jicf_org = db.query(Organization).filter(
            Organization.slug == "jicf").first()

        if not jicf_org:
            jicf_org = Organization(
                id=str(uuid.uuid4()),
                name="Jinan International Christian Fellowship",
                slug="jicf",
                domain="jinanicf.com",
                settings={
                    "location": "Jinan, Shandong, China",
                    "description": "International Christian Fellowship in Jinan",
                    "timezone": "Asia/Shanghai"
                },
                is_active=True
            )
            db.add(jicf_org)
            db.commit()
            db.refresh(jicf_org)
            print(f"  + Created JICF organization: {jicf_org.id}")
        else:
            print(f"  ✓ JICF organization already exists: {jicf_org.id}")

        # Step 2: Create system roles
        print("\nStep 2: Creating system roles for JICF...")
        roles = create_organization_roles(db, jicf_org.id)

        # Step 3: Assign admin user
        print("Step 3: Assigning admin user...")
        admin_user = db.query(User).filter(
            User.email == "admin@jinanicf.com").first()

        if admin_user:
            # Update user's organization_id (backward compatibility)
            if not admin_user.organization_id:
                admin_user.organization_id = jicf_org.id
                print(f"  + Assigned user to JICF organization")
            
            # Create organization membership with super_admin role
            existing_membership = db.query(OrganizationUser).filter(
                OrganizationUser.user_id == admin_user.id,
                OrganizationUser.organization_id == jicf_org.id
            ).first()
            
            if not existing_membership:
                org_user = OrganizationUser(
                    id=str(uuid.uuid4()),
                    user_id=admin_user.id,
                    organization_id=jicf_org.id,
                    role_id=roles["super_admin"].id,
                    is_owner=True,  # Organization creator
                    is_active=True,
                    joined_at=None  # Owner doesn't need invitation
                )
                db.add(org_user)
                print(f"  + Created organization membership with super_admin role")
            else:
                # Update existing membership to super_admin
                existing_membership.role_id = roles["super_admin"].id
                existing_membership.is_owner = True
                print(f"  ✓ Updated existing membership to super_admin role")
            
            db.commit()
            print(f"  ✅ admin@jinanicf.com is now JICF super admin")
        else:
            print("  ⚠️  Warning: admin@jinanicf.com user not found")

        print("\n" + "=" * 70)
        print("✅ JICF Organization Setup Complete!")
        print("=" * 70)
        print()
        print(f"Organization: {jicf_org.name}")
        print(f"Organization ID: {jicf_org.id}")
        print(f"Slug: {jicf_org.slug}")
        print(f"Domain: {jicf_org.domain}")
        print()
        print(f"System Roles Created: {len(roles)}")
        for role_name, role in roles.items():
            print(f"  - {role.display_name} ({role_name}): {len(role.permissions)} permissions")
        print()
        print("Next steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Admin user can now:")
        print("   - Invite users by email")
        print("   - Create custom roles")
        print("   - Manage organization settings")
        print("   - Import members via CSV")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
