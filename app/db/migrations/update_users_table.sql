-- Alter users table to add new columns
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    -- First, alter the id column
    ALTER TABLE users
    ALTER COLUMN id VARCHAR(50) NOT NULL;

    -- Add new columns
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'first_name')
    BEGIN
        ALTER TABLE users ADD first_name VARCHAR(100);
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'last_name')
    BEGIN
        ALTER TABLE users ADD last_name VARCHAR(100);
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'mobile_number')
    BEGIN
        ALTER TABLE users ADD mobile_number VARCHAR(20);
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'role')
    BEGIN
        ALTER TABLE users ADD role VARCHAR(50) DEFAULT 'user';
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'organization_id')
    BEGIN
        ALTER TABLE users ADD organization_id VARCHAR(50);
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'status')
    BEGIN
        ALTER TABLE users ADD status VARCHAR(20) DEFAULT 'active';
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'avatar')
    BEGIN
        ALTER TABLE users ADD avatar VARCHAR(255);
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'last_active')
    BEGIN
        ALTER TABLE users ADD last_active DATETIME DEFAULT GETDATE();
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'created_by')
    BEGIN
        ALTER TABLE users ADD created_by VARCHAR(50) DEFAULT 'system';
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'created_date')
    BEGIN
        ALTER TABLE users ADD created_date DATETIME DEFAULT GETDATE();
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'modified_by')
    BEGIN
        ALTER TABLE users ADD modified_by VARCHAR(50) DEFAULT 'system';
    END

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'modified_date')
    BEGIN
        ALTER TABLE users ADD modified_date DATETIME DEFAULT GETDATE();
    END

    -- Drop old columns if they exist
    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'last_active')
    BEGIN
        ALTER TABLE users DROP COLUMN last_active;
    END

    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'created_at')
    BEGIN
        ALTER TABLE users DROP COLUMN created_at;
    END

    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('users') AND name = 'updated_at')
    BEGIN
        ALTER TABLE users DROP COLUMN updated_at;
    END
END 