-- Add status column to organizations table
ALTER TABLE organizations
ADD status NVARCHAR(50) NOT NULL DEFAULT 'active';

-- Update existing records to have 'active' status
UPDATE organizations
SET status = 'active'
WHERE status IS NULL; 