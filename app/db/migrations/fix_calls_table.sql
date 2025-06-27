-- Drop existing calls table if it exists
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[calls]') AND type in (N'U'))
BEGIN
    DROP TABLE [dbo].[calls];
END
GO

-- Create calls table with correct structure
CREATE TABLE [dbo].[calls] (
    [id] VARCHAR(36) PRIMARY KEY,
    [call_id] VARCHAR(255) UNIQUE NOT NULL,
    [to_number] VARCHAR(20) NOT NULL,
    [dynamic_variables] NVARCHAR(MAX),
    [metadata] NVARCHAR(MAX),  -- Changed from call_metadata to metadata
    [campaign_id] VARCHAR(50),
    [created_at] DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    [updated_at] DATETIME2 DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [FK_calls_campaign_id] FOREIGN KEY ([campaign_id]) REFERENCES [campaigns]([id])
);
GO

-- Create indexes
CREATE INDEX [idx_calls_call_id] ON [dbo].[calls]([call_id]);
CREATE INDEX [idx_calls_campaign_id] ON [dbo].[calls]([campaign_id]);
GO 