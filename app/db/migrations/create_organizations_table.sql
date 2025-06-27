-- Create organizations table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[organizations]') AND type in (N'U'))
BEGIN
    CREATE TABLE organizations (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(50) NOT NULL UNIQUE,
        address VARCHAR(500),
        phone VARCHAR(20),
        created_by VARCHAR(50),
        last_modified_by VARCHAR(50),
        created_date DATETIME DEFAULT GETDATE(),
        modified_date DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX idx_organization_code ON organizations(code);
END 