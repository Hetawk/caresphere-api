"""Utility for generating and validating unique organization codes."""

import random
from typing import Optional

from sqlalchemy.orm import Session

CODE_LENGTH = 7
CODE_MIN = 1000000  # 7 digits minimum
CODE_MAX = 9999999  # 7 digits maximum
MAX_ATTEMPTS = 100


def generate_code() -> str:
    """Generate a random 7-digit code."""
    return str(random.randint(CODE_MIN, CODE_MAX))


def generate_unique_code(db: Session, model_class, code_field: str = "organization_code") -> str:
    """
    Generate a unique organization code.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class to check uniqueness against
        code_field: Name of the field containing the code
        
    Returns:
        A unique 7-digit code as string
        
    Raises:
        RuntimeError: If unable to generate unique code after MAX_ATTEMPTS
    """
    for _ in range(MAX_ATTEMPTS):
        code = generate_code()
        
        # Check if code exists
        existing = db.query(model_class).filter(
            getattr(model_class, code_field) == code
        ).first()
        
        if not existing:
            return code
    
    raise RuntimeError(f"Failed to generate unique code after {MAX_ATTEMPTS} attempts")


def validate_code_format(code: str) -> bool:
    """
    Validate organization code format.
    
    Args:
        code: Code to validate
        
    Returns:
        True if code is valid format (7 digits), False otherwise
    """
    if not code:
        return False
    
    if not code.isdigit():
        return False
    
    if len(code) != CODE_LENGTH:
        return False
    
    try:
        code_int = int(code)
        return CODE_MIN <= code_int <= CODE_MAX
    except ValueError:
        return False


def find_by_code(db: Session, model_class, code: str, code_field: str = "organization_code") -> Optional[any]:
    """
    Find an entity by organization code.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class
        code: Organization code to search for
        code_field: Name of the field containing the code
        
    Returns:
        Entity if found, None otherwise
    """
    if not validate_code_format(code):
        return None
    
    return db.query(model_class).filter(
        getattr(model_class, code_field) == code
    ).first()
