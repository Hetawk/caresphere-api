#!/usr/bin/env python3
"""
Run database migrations directly
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import alembic
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run all pending migrations"""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Run upgrade to head
    print("Running migrations...")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
