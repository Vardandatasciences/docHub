-- ============================================
-- QUICK MySQL COMMANDS for MySQL Workbench
-- Copy and paste these commands directly
-- ============================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS dochub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Step 2: Use Database
USE dochub;

-- Step 3: Create Tables (run database_schema.sql or continue below)

-- Or you can simply execute:
-- File > Open SQL Script > Select database_schema.sql > Execute

-- ============================================
-- VERIFICATION COMMANDS
-- Run these after executing database_schema.sql
-- ============================================

-- Check if all tables are created
SHOW TABLES;
-- Expected output: 5 tables (users, categories, documents, document_views, document_shares)

-- Check users table
SELECT * FROM users;
-- Expected: 4 default users

-- Check categories table  
SELECT * FROM categories;
-- Expected: 6 default categories

-- Verify table structure
DESCRIBE users;
DESCRIBE categories;
DESCRIBE documents;

-- ============================================
-- USEFUL MANAGEMENT COMMANDS
-- ============================================

-- View all documents with details
SELECT 
    d.id,
    d.name,
    c.name as category,
    u.name as uploaded_by,
    d.file_size_formatted as size,
    d.uploaded_at,
    d.status
FROM documents d
LEFT JOIN categories c ON d.category_id = c.id
LEFT JOIN users u ON d.uploaded_by = u.id
WHERE d.is_archived = FALSE
ORDER BY d.uploaded_at DESC
LIMIT 20;

-- Get statistics
SELECT 
    'Total Documents' as metric,
    COUNT(*) as value
FROM documents 
WHERE is_archived = FALSE
UNION ALL
SELECT 
    'Total Categories',
    COUNT(*)
FROM categories 
WHERE is_active = TRUE
UNION ALL
SELECT 
    'Total Users',
    COUNT(*)
FROM users 
WHERE is_active = TRUE;

-- View category statistics
SELECT 
    c.name as category,
    c.color,
    COUNT(d.id) as document_count,
    COALESCE(SUM(d.file_size), 0) as total_size_bytes
FROM categories c
LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
WHERE c.is_active = TRUE
GROUP BY c.id
ORDER BY document_count DESC;

-- View recent uploads (last 7 days)
SELECT 
    d.name,
    u.name as uploaded_by,
    c.name as category,
    d.uploaded_at
FROM documents d
JOIN users u ON d.uploaded_by = u.id
JOIN categories c ON d.category_id = c.id
WHERE d.uploaded_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
AND d.is_archived = FALSE
ORDER BY d.uploaded_at DESC;

-- ============================================
-- MAINTENANCE COMMANDS
-- ============================================

-- Update category document counts
UPDATE categories c
SET document_count = (
    SELECT COUNT(*) 
    FROM documents d 
    WHERE d.category_id = c.id AND d.is_archived = FALSE
);

-- Find documents without category
SELECT d.*
FROM documents d
LEFT JOIN categories c ON d.category_id = c.id
WHERE c.id IS NULL;

-- Find large documents (> 10MB)
SELECT 
    name,
    file_size_formatted,
    uploaded_at,
    uploaded_by
FROM documents
WHERE file_size > 10485760
AND is_archived = FALSE
ORDER BY file_size DESC;

-- ============================================
-- USER MANAGEMENT
-- ============================================

-- Create new user
INSERT INTO users (name, email, password_hash, role, is_active)
VALUES ('New User', 'newuser@example.com', '$2b$12$...hash...', 'user', TRUE);

-- Update user role to admin
UPDATE users 
SET role = 'admin' 
WHERE email = 'user@example.com';

-- Deactivate user
UPDATE users 
SET is_active = FALSE 
WHERE email = 'user@example.com';

-- View user upload statistics
SELECT 
    u.name,
    u.email,
    COUNT(d.id) as total_uploads,
    COALESCE(SUM(d.file_size), 0) as total_size_bytes
FROM users u
LEFT JOIN documents d ON u.id = d.uploaded_by AND d.is_archived = FALSE
WHERE u.is_active = TRUE
GROUP BY u.id
ORDER BY total_uploads DESC;

-- ============================================
-- CATEGORY MANAGEMENT
-- ============================================

-- Create new category
INSERT INTO categories (name, color, description, created_by)
VALUES ('New Category', 'hsl(210 100% 50%)', 'Category description', 1);

-- Update category name
UPDATE categories 
SET name = 'Updated Name' 
WHERE id = 1;

-- Deactivate category (soft delete)
UPDATE categories 
SET is_active = FALSE 
WHERE id = 1;

-- Find categories with no documents
SELECT c.*
FROM categories c
LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
WHERE d.id IS NULL AND c.is_active = TRUE;

-- ============================================
-- DOCUMENT MANAGEMENT
-- ============================================

-- Archive (soft delete) document
UPDATE documents 
SET is_archived = TRUE, archived_at = NOW() 
WHERE id = 1;

-- Restore archived document
UPDATE documents 
SET is_archived = FALSE, archived_at = NULL 
WHERE id = 1;

-- Delete documents older than 1 year (CAREFUL!)
-- UPDATE documents 
-- SET is_archived = TRUE, archived_at = NOW()
-- WHERE uploaded_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Find duplicate documents (same name and size)
SELECT 
    name,
    file_size,
    COUNT(*) as duplicate_count
FROM documents
WHERE is_archived = FALSE
GROUP BY name, file_size
HAVING duplicate_count > 1;

-- Search documents by name
SELECT 
    d.name,
    c.name as category,
    u.name as uploaded_by,
    d.uploaded_at
FROM documents d
JOIN categories c ON d.category_id = c.id
JOIN users u ON d.uploaded_by = u.id
WHERE d.name LIKE '%search_term%'
AND d.is_archived = FALSE
ORDER BY d.uploaded_at DESC;

-- ============================================
-- BACKUP & RESTORE
-- ============================================

-- Backup database (run in terminal, not MySQL Workbench)
-- mysqldump -u root -p dochub > backup_$(date +%Y%m%d).sql

-- Restore database (run in terminal)
-- mysql -u root -p dochub < backup_20240120.sql

-- ============================================
-- PERFORMANCE OPTIMIZATION
-- ============================================

-- Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'dochub'
ORDER BY (data_length + index_length) DESC;

-- Analyze tables for optimization
ANALYZE TABLE users, categories, documents, document_views, document_shares;

-- Optimize tables
OPTIMIZE TABLE users, categories, documents, document_views, document_shares;

-- ============================================
-- SECURITY
-- ============================================

-- Create read-only user (for reporting)
CREATE USER 'dochub_readonly'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT SELECT ON dochub.* TO 'dochub_readonly'@'localhost';
FLUSH PRIVILEGES;

-- Create application user (for Flask app)
CREATE USER 'dochub_app'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE ON dochub.* TO 'dochub_app'@'localhost';
FLUSH PRIVILEGES;

-- View current user permissions
SHOW GRANTS FOR 'root'@'localhost';

-- ============================================
-- TROUBLESHOOTING
-- ============================================

-- Check MySQL version
SELECT VERSION();

-- Check current database
SELECT DATABASE();

-- Check table engines
SELECT 
    table_name,
    engine
FROM information_schema.TABLES
WHERE table_schema = 'dochub';

-- Check foreign key constraints
SELECT 
    constraint_name,
    table_name,
    referenced_table_name
FROM information_schema.KEY_COLUMN_USAGE
WHERE table_schema = 'dochub'
AND referenced_table_name IS NOT NULL;

-- Check indexes
SHOW INDEX FROM documents;

-- View running queries
SHOW PROCESSLIST;

-- ============================================
-- RESET DATABASE (CAREFUL - DELETES EVERYTHING!)
-- ============================================

-- Drop all tables and recreate
-- DROP DATABASE IF EXISTS dochub;
-- CREATE DATABASE dochub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Then run database_schema.sql again

-- ============================================
-- NOTES
-- ============================================

-- 1. Always backup before making changes!
-- 2. Test queries on development database first
-- 3. Use transactions for multiple changes:
--    START TRANSACTION;
--    -- your commands here
--    COMMIT;  -- or ROLLBACK; to undo
-- 4. Be careful with DELETE and UPDATE without WHERE clause
-- 5. Regular backups are essential!

-- ============================================
-- END OF COMMANDS
-- ============================================






