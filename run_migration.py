#!/usr/bin/env python3
"""
Run database migration for password reset fields.
Execute this once after deploying the new code.
"""
import subprocess
import sys


def main():
    print("🔄 Running database migration...")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
            # 
        )
        print(result.stdout)
        print("✅ Migration completed successfully!")
        print("\n📝 New endpoints available:")
        print("   - POST /auth/change-password (requires authentication)")
        print("   - POST /auth/forgot-password")
        print("   - POST /auth/reset-password")
        print("   - POST /auth/verify-email")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e.stderr}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
