#!/usr/bin/env python3
"""
Run the RBAC migration SQL directly on the database
"""
import pymysql

# Database connection details
DB_CONFIG = {
    'host': '31.97.41.230',
    'port': 9909,
    'user': 'hetawk',
    'password': 'Kwatehekd7!',
    'database': 'church_connect'
}

# Read the migration SQL
migration_sql = """
-- Drop existing tables to recreate with correct schema
DROP TABLE IF EXISTS `user_invitations`;
DROP TABLE IF EXISTS `organization_users`;
DROP TABLE IF EXISTS `role_permissions`;
DROP TABLE IF EXISTS `roles`;
DROP TABLE IF EXISTS `permissions`;

-- Create permissions table
CREATE TABLE IF NOT EXISTS `permissions` (
    `id` CHAR(36) NOT NULL,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `display_name` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `category` VARCHAR(50),
    `is_system` BOOLEAN DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_permission_category` (`category`),
    INDEX `idx_permission_is_system` (`is_system`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create roles table
CREATE TABLE IF NOT EXISTS `roles` (
    `id` CHAR(36) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `display_name` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `organization_id` CHAR(36) NOT NULL,
    `is_system` BOOLEAN DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`organization_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uq_role_name_org` (`name`, `organization_id`),
    INDEX `idx_role_organization` (`organization_id`),
    INDEX `idx_role_is_system` (`is_system`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create role_permissions join table
CREATE TABLE IF NOT EXISTS `role_permissions` (
    `role_id` CHAR(36) NOT NULL,
    `permission_id` CHAR(36) NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`),
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`permission_id`) REFERENCES `permissions`(`id`) ON DELETE CASCADE,
    INDEX `idx_role_permission_role` (`role_id`),
    INDEX `idx_role_permission_permission` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create organization_users table
CREATE TABLE IF NOT EXISTS `organization_users` (
    `organization_id` CHAR(36) NOT NULL,
    `user_id` CHAR(36) NOT NULL,
    `role_id` CHAR(36),
    `is_owner` BOOLEAN DEFAULT 0,
    `joined_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`organization_id`, `user_id`),
    FOREIGN KEY (`organization_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE SET NULL,
    INDEX `idx_org_user_organization` (`organization_id`),
    INDEX `idx_org_user_user` (`user_id`),
    INDEX `idx_org_user_role` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create user_invitations table
CREATE TABLE IF NOT EXISTS `user_invitations` (
    `id` CHAR(36) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `organization_id` CHAR(36) NOT NULL,
    `role_id` CHAR(36),
    `invited_by_user_id` CHAR(36),
    `token` VARCHAR(255) NOT NULL UNIQUE,
    `status` VARCHAR(20) DEFAULT 'pending',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `expires_at` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`organization_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`invited_by_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_invitation_email` (`email`),
    INDEX `idx_invitation_organization` (`organization_id`),
    INDEX `idx_invitation_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Update alembic_version
INSERT INTO `alembic_version` (`version_num`) VALUES ('202602051730')
ON DUPLICATE KEY UPDATE `version_num` = '202602051730';
"""

def run_migration():
    """Execute the migration SQL"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute migration
        print("Running migration SQL...")
        for statement in migration_sql.split(';'):
            statement = statement.strip()
            if statement:
                print(f"Executing: {statement[:80]}...")
                cursor.execute(statement)
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
