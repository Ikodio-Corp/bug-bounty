-- Migration 011: Add usage tracking and update subscription tiers
-- Date: 2025-11-24
-- Author: GitHub Copilot

BEGIN;

-- 1. Create new subscription tier enum
CREATE TYPE subscriptiontier_new AS ENUM ('FREE', 'PROFESSIONAL', 'BUSINESS', 'ENTERPRISE', 'GOVERNMENT');

-- 2. Add temporary column with new enum type
ALTER TABLE users ADD COLUMN subscription_tier_new subscriptiontier_new;

-- 3. Migrate data from old to new column
UPDATE users 
SET subscription_tier_new = 
    CASE subscription_tier::text
        WHEN 'BRONZE' THEN 'PROFESSIONAL'::subscriptiontier_new
        WHEN 'SILVER' THEN 'BUSINESS'::subscriptiontier_new
        WHEN 'GOLD' THEN 'ENTERPRISE'::subscriptiontier_new
        WHEN 'PLATINUM' THEN 'GOVERNMENT'::subscriptiontier_new
        WHEN 'FREE' THEN 'FREE'::subscriptiontier_new
        WHEN 'PROFESSIONAL' THEN 'PROFESSIONAL'::subscriptiontier_new
        WHEN 'BUSINESS' THEN 'BUSINESS'::subscriptiontier_new
        WHEN 'ENTERPRISE' THEN 'ENTERPRISE'::subscriptiontier_new
        WHEN 'GOVERNMENT' THEN 'GOVERNMENT'::subscriptiontier_new
        ELSE 'FREE'::subscriptiontier_new
    END;

-- 4. Drop old column and rename new column
ALTER TABLE users DROP COLUMN subscription_tier;
ALTER TABLE users RENAME COLUMN subscription_tier_new TO subscription_tier;

-- 5. Drop old enum type
DROP TYPE IF EXISTS subscriptiontier CASCADE;

-- 6. Rename new enum type
ALTER TYPE subscriptiontier_new RENAME TO subscriptiontier;

-- 7. Set default value and not null
ALTER TABLE users ALTER COLUMN subscription_tier SET DEFAULT 'FREE'::subscriptiontier;
ALTER TABLE users ALTER COLUMN subscription_tier SET NOT NULL;

-- 8. Create scan_usage table
CREATE TABLE scan_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,  -- YYYY-MM format
    scan_count INTEGER NOT NULL DEFAULT 0,
    "limit" INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- Create indexes for scan_usage
CREATE INDEX idx_scan_usage_user_id ON scan_usage(user_id);
CREATE INDEX idx_scan_usage_month ON scan_usage(month);
CREATE INDEX idx_scan_usage_user_month ON scan_usage(user_id, month);

-- 9. Create autofix_usage table
CREATE TABLE autofix_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    fix_count INTEGER NOT NULL DEFAULT 0,
    "limit" INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- Create indexes for autofix_usage
CREATE INDEX idx_autofix_usage_user_id ON autofix_usage(user_id);
CREATE INDEX idx_autofix_usage_month ON autofix_usage(month);
CREATE INDEX idx_autofix_usage_user_month ON autofix_usage(user_id, month);

-- 10. Create api_usage table
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0,
    "limit" INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- Create indexes for api_usage
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_month ON api_usage(month);
CREATE INDEX idx_api_usage_user_month ON api_usage(user_id, month);

-- 11. Create storage_usage table
CREATE TABLE storage_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bytes_used BIGINT NOT NULL DEFAULT 0,
    bytes_limit BIGINT,
    retention_days INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create indexes for storage_usage
CREATE INDEX idx_storage_usage_user_id ON storage_usage(user_id);

-- 12. Create trigger function to auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 13. Apply triggers to all usage tables
CREATE TRIGGER update_scan_usage_updated_at 
BEFORE UPDATE ON scan_usage
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_autofix_usage_updated_at 
BEFORE UPDATE ON autofix_usage
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_usage_updated_at 
BEFORE UPDATE ON api_usage
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_storage_usage_updated_at 
BEFORE UPDATE ON storage_usage
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMIT;

-- Verification queries
SELECT 'Migration 011 completed successfully!' AS status;
SELECT 'New subscription tiers:' AS info;
SELECT unnest(enum_range(NULL::subscriptiontier)) AS tier;
SELECT 'Usage tables created:' AS info;
SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%usage';
