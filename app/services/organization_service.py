"""Organization service for business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from slugify import slugify

from app.models.organization import Organization
from app.models.role import OrganizationUser, Role
from app.models.user import User
from app.utils.org_code import generate_unique_code, find_by_code, validate_code_format
from app.schemas.organization import OrganizationCreate


class OrganizationService:
    """Service for organization management operations."""
    
    @staticmethod
    def create_organization(db: Session, org_data: OrganizationCreate, creator: User) -> Organization:
        """
        Create a new organization with auto-generated code.
        Creator becomes super admin.
        
        Args:
            db: Database session
            org_data: Organization creation data
            creator: User creating the organization
            
        Returns:
            Created organization
        """
        # Generate unique code
        code = generate_unique_code(db, Organization, "organization_code")
        
        # Create organization
        org = Organization(
            name=org_data.name,
            slug=org_data.slug if hasattr(org_data, 'slug') else slugify(org_data.name),
            domain=org_data.domain if hasattr(org_data, 'domain') else None,
            organization_code=code,
            is_active=True
        )
        
        db.add(org)
        db.flush()  # Get org.id without committing
        
        # Create super admin role for this organization
        super_admin_role = Role(
            name="super_admin",
            display_name="Super Administrator",
            description="Full control over the organization",
            organization_id=org.id,
            is_system=True
        )
        db.add(super_admin_role)
        db.flush()
        
        # Link creator to organization as super admin
        org_user = OrganizationUser(
            user_id=creator.id,
            organization_id=org.id,
            role_id=super_admin_role.id,
            is_owner=True
        )
        db.add(org_user)
        
        db.commit()
        db.refresh(org)
        
        return org
    
    @staticmethod
    def join_organization(db: Session, code: str, user: User, role_name: str = "member") -> Optional[Organization]:
        """
        Join an organization using its code.
        
        Args:
            db: Database session
            code: 7-digit organization code
            user: User joining the organization
            role_name: Role to assign (default: member)
            
        Returns:
            Organization if successful, None if code invalid
        """
        # Validate code format
        if not validate_code_format(code):
            return None
        
        # Find organization
        org = find_by_code(db, Organization, code, "organization_code")
        if not org or not org.is_active:
            return None
        
        # Check if user already in organization
        existing = db.query(OrganizationUser).filter(
            OrganizationUser.user_id == user.id,
            OrganizationUser.organization_id == org.id
        ).first()
        
        if existing:
            return org  # Already a member
        
        # Get or create role
        role = db.query(Role).filter(
            Role.organization_id == org.id,
            Role.name == role_name
        ).first()
        
        if not role:
            # Create default member role
            role = Role(
                name="member",
                display_name="Member",
                description="Standard organization member",
                organization_id=org.id,
                is_system=False
            )
            db.add(role)
            db.flush()
        
        # Add user to organization
        org_user = OrganizationUser(
            user_id=user.id,
            organization_id=org.id,
            role_id=role.id,
            is_owner=False
        )
        db.add(org_user)
        db.commit()
        
        return org
    
    @staticmethod
    def regenerate_code(db: Session, org: Organization, reason: Optional[str] = None) -> str:
        """
        Regenerate organization code (admin only).
        
        Args:
            db: Database session
            org: Organization to regenerate code for
            reason: Reason for regeneration (for audit trail)
            
        Returns:
            New organization code
        """
        # Generate new unique code
        new_code = generate_unique_code(db, Organization, "organization_code")
        
        # Update organization
        org.organization_code = new_code
        db.commit()
        db.refresh(org)
        
        # TODO: Log to audit trail with reason
        
        return new_code
    
    @staticmethod
    def get_user_organization(db: Session, user: User) -> Optional[Organization]:
        """
        Get the organization the user belongs to.
        
        Args:
            db: Database session
            user: User to get organization for
            
        Returns:
            Organization if user belongs to one, None otherwise
        """
        org_user = db.query(OrganizationUser).filter(
            OrganizationUser.user_id == user.id
        ).first()
        
        if not org_user:
            return None
        
        return db.query(Organization).filter(
            Organization.id == org_user.organization_id
        ).first()
    
    @staticmethod
    def is_org_admin(db: Session, user: User, org: Organization) -> bool:
        """
        Check if user is admin of the organization.
        
        Args:
            db: Database session
            user: User to check
            org: Organization to check against
            
        Returns:
            True if user is admin, False otherwise
        """
        org_user = db.query(OrganizationUser).filter(
            OrganizationUser.user_id == user.id,
            OrganizationUser.organization_id == org.id
        ).first()
        
        if not org_user:
            return False
        
        # Check if owner or has admin role
        if org_user.is_owner:
            return True
        
        role = db.query(Role).filter(Role.id == org_user.role_id).first()
        return role and role.name in ["super_admin", "admin"]
