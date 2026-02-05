"""Seed default permissions and system roles for RBAC.

This script should be run after the RBAC migration to populate
default permissions and create system roles for organizations.
"""

import uuid
from app.models.role import Permission
from app.database import SessionLocal
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Default permissions grouped by category
DEFAULT_PERMISSIONS = {
    "members": [
        ("view_members", "View Members", "View member list and profiles"),
        ("manage_members", "Manage Members", "Create, update, and delete members"),
        ("export_members", "Export Members", "Export member data to CSV/Excel"),
        ("import_members", "Import Members", "Bulk import members from files"),
    ],
    "messages": [
        ("view_messages", "View Messages", "View message history"),
        ("send_messages", "Send Messages", "Send messages to members"),
        ("manage_templates", "Manage Templates",
         "Create and edit message templates"),
        ("delete_messages", "Delete Messages", "Delete message records"),
    ],
    "automation": [
        ("view_automation", "View Automation", "View automation rules and logs"),
        ("manage_automation", "Manage Automation",
         "Create and edit automation rules"),
        ("execute_automation", "Execute Automation",
         "Manually trigger automation rules"),
    ],
    "analytics": [
        ("view_analytics", "View Analytics",
         "View analytics dashboards and reports"),
        ("export_reports", "Export Reports", "Export analytics reports"),
    ],
    "organization": [
        ("manage_organization", "Manage Organization",
         "Update organization settings"),
        ("invite_users", "Invite Users", "Invite new users to the organization"),
        ("manage_users", "Manage Users", "View and manage organization users"),
        ("remove_users", "Remove Users", "Remove users from the organization"),
    ],
    "roles": [
        ("view_roles", "View Roles", "View organization roles"),
        ("manage_roles", "Manage Roles", "Create, update, and delete custom roles"),
        ("assign_roles", "Assign Roles", "Assign roles to users"),
    ],
    "settings": [
        ("view_settings", "View Settings", "View organization settings"),
        ("manage_settings", "Manage Settings", "Update organization settings"),
        ("manage_integrations", "Manage Integrations",
         "Configure external integrations"),
    ],
}

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


def seed_permissions(db: Session):
    """Create all default permissions."""
    print("Seeding default permissions...")

    permissions_map = {}

    for category, perms in DEFAULT_PERMISSIONS.items():
        for name, display_name, description in perms:
            # Check if permission already exists
            existing = db.query(Permission).filter(
                Permission.name == name).first()
            if existing:
                print(f"  ✓ Permission '{name}' already exists")
                permissions_map[name] = existing
                continue

            permission = Permission(
                id=str(uuid.uuid4()),
                name=name,
                display_name=display_name,
                description=description,
                category=category,
                is_system=True  # System permissions cannot be deleted
            )
            db.add(permission)
            permissions_map[name] = permission
            print(f"  + Created permission: {name}")

    db.commit()
    print(f"\n✅ Seeded {len(permissions_map)} permissions\n")

    return permissions_map


def main():
    """Run the seeding process."""
    print("=" * 60)
    print("RBAC System Seed Script")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        # Seed permissions
        permissions_map = seed_permissions(db)

        print("\n" + "=" * 60)
        print("✅ RBAC seeding complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run the JICF organization seed script")
        print("2. Create system roles for JICF organization")
        print("3. Assign super_admin role to admin@jinanicf.com")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
