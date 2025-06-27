-- Drop all foreign key constraints referencing user_roles, users, roles, organizations
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += N'
ALTER TABLE [' + OBJECT_SCHEMA_NAME(parent_object_id) + '].[' + OBJECT_NAME(parent_object_id) + '] DROP CONSTRAINT [' + name + '];'
FROM sys.foreign_keys
WHERE referenced_object_id IN (
    OBJECT_ID('user_roles'),
    OBJECT_ID('users'),
    OBJECT_ID('roles'),
    OBJECT_ID('organizations'),
    OBJECT_ID('campaigns')
);

EXEC sp_executesql @sql;
GO

-- Drop existing tables if they exist (in correct order)
DROP TABLE IF EXISTS user_roles;
GO
DROP TABLE IF EXISTS users;
GO
DROP TABLE IF EXISTS roles;
GO
DROP TABLE IF EXISTS campaigns;
GO
DROP TABLE IF EXISTS organizations;
GO

-- Create organizations table first
CREATE TABLE organizations (
    id VARCHAR(50) PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    modified_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50) NOT NULL
);
GO

-- Create roles table
CREATE TABLE roles (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(500),
    org_id VARCHAR(50),
    permissions VARCHAR(MAX),
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    modified_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50) NOT NULL,
    CONSTRAINT FK_roles_org_id FOREIGN KEY (org_id) REFERENCES organizations(id)
);
GO

-- Create users table with foreign key to organizations
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mobile_number VARCHAR(20),
    hashed_password VARCHAR(255) NOT NULL,
    organization_id VARCHAR(50),
    role VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    is_superuser BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    modified_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50) NOT NULL,
    CONSTRAINT FK_users_organization_id FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT FK_users_role FOREIGN KEY (role) REFERENCES roles(name)
);
GO

-- Create user_roles table for many-to-many relationship
CREATE TABLE user_roles (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    role_id VARCHAR(50) NOT NULL,
    created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    modified_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50) NOT NULL,
    CONSTRAINT FK_user_roles_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT FK_user_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
);
GO

-- Create campaigns table
CREATE TABLE campaigns (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    inbound_number VARCHAR(20),
    caller_id_number VARCHAR(20),
    state VARCHAR(20) NOT NULL,
    version INT DEFAULT 0,
    llm_config NVARCHAR(MAX),
    tts_config NVARCHAR(MAX),
    stt_config NVARCHAR(MAX),
    timezone VARCHAR(50),
    post_call_actions NVARCHAR(MAX),
    live_actions NVARCHAR(MAX),
    callback_endpoint VARCHAR(255),
    retry_config NVARCHAR(MAX),
    account_id VARCHAR(50),
    org_id VARCHAR(50),
    created_by INT,
    created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    is_active BIT DEFAULT 1,
    telephonic_provider VARCHAR(50),
    knowledge_base NVARCHAR(MAX),
    CONSTRAINT FK_campaigns_org_id FOREIGN KEY (org_id) REFERENCES organizations(id)
);
GO

-- Create trigger to update is_superuser when user_roles changes
CREATE TRIGGER trg_update_is_superuser
ON user_roles
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update is_superuser for affected users
    UPDATE u
    SET u.is_superuser = CASE 
        WHEN EXISTS (
            SELECT 1 
            FROM user_roles ur 
            JOIN roles r ON ur.role_id = r.id 
            WHERE ur.user_id = u.id AND r.name = 'superuser'
        ) THEN 1 
        ELSE 0 
    END
    FROM users u
    WHERE u.id IN (
        SELECT user_id FROM inserted
        UNION
        SELECT user_id FROM deleted
    );
END;
GO

-- Insert default organization first
INSERT INTO organizations (id, code, name, description, created_by, modified_by) VALUES
('org_1', 'DEFAULT', 'Default Organization', 'Default organization for system users', 'system', 'system');
GO

-- Insert default roles with permissions
INSERT INTO roles (id, name, description, org_id, permissions, created_by, modified_by) VALUES
('role_1', 'superuser', 'Superuser with full access', 'org_1', '["*"]', 'system', 'system'),
('role_2', 'org_admin', 'Organization administrator', 'org_1', '["read:users", "write:users", "read:org", "write:org"]', 'system', 'system'),
('role_3', 'user', 'Regular user', 'org_1', '["read:own", "write:own"]', 'system', 'system');
GO

-- Insert test users
INSERT INTO users (id, first_name, last_name, email, mobile_number, hashed_password, organization_id, role, status, is_superuser, created_by, modified_by) VALUES
('user_1', 'Admin', 'User', 'admin@example.com', '+1234567890', '$2b$12$uqoI7h.QlT/7j0RgaQLJnOVKLjcWe7IZR2GImud1kqC.dSfPj.Bd6', 'org_1', 'superuser', 'active', 1, 'system', 'system'),
('user_2', 'Org', 'Admin', 'orgadmin@example.com', '+1234567891', '$2b$12$uqoI7h.QlT/7j0RgaQLJnOVKLjcWe7IZR2GImud1kqC.dSfPj.Bd6', 'org_1', 'org_admin', 'active', 0, 'system', 'system'),
('user_3', 'Regular', 'User', 'user@example.com', '+1234567892', '$2b$12$uqoI7h.QlT/7j0RgaQLJnOVKLjcWe7IZR2GImud1kqC.dSfPj.Bd6', 'org_1', 'user', 'active', 0, 'system', 'system');
GO

-- Insert user roles
INSERT INTO user_roles (id, user_id, role_id, created_by, modified_by) VALUES
('ur_1', 'user_1', 'role_1', 'system', 'system'),
('ur_2', 'user_2', 'role_2', 'system', 'system'),
('ur_3', 'user_3', 'role_3', 'system', 'system');
GO 