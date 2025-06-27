-- Add org_id column to campaigns table if it doesn't exist
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'campaigns') 
    AND name = 'org_id'
)
BEGIN
    ALTER TABLE campaigns
    ADD org_id VARCHAR(50);

    -- Add foreign key constraint
    ALTER TABLE campaigns
    ADD CONSTRAINT FK_campaigns_org_id 
    FOREIGN KEY (org_id) 
    REFERENCES organizations(id);
END;
GO 