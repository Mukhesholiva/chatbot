-- Add status column to organizations table
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('organizations') AND name = 'status')
BEGIN
    ALTER TABLE organizations
    ADD status VARCHAR(20) DEFAULT 'active' NOT NULL;
END 