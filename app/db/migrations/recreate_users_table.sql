-- Drop the profiles table if it exists
IF OBJECT_ID('profiles', 'U') IS NOT NULL
    DROP TABLE profiles;

-- Drop the users table if it exists
IF OBJECT_ID('users', 'U') IS NOT NULL
    DROP TABLE users;

-- Create the new users table
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    mobile_number VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user',
    organization_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    avatar VARCHAR(255),
    last_active DATETIME DEFAULT GETDATE(),
    created_by VARCHAR(50) DEFAULT 'system',
    created_date DATETIME DEFAULT GETDATE(),
    modified_by VARCHAR(50) DEFAULT 'system',
    modified_date DATETIME DEFAULT GETDATE()
); 