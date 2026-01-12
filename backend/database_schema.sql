-- ============================================
-- DocHub Database Schema
-- Document Management System
-- ============================================

-- Drop existing tables if they exist (in correct order to avoid foreign key issues)
DROP TABLE IF EXISTS document_shares;
DROP TABLE IF EXISTS document_views;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- ============================================
-- 1. USERS TABLE
-- Stores user information and authentication details
-- ============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
    department VARCHAR(100) NULL,
    phone VARCHAR(20) NULL,
    profile_image_url VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. CATEGORIES TABLE
-- Stores document categories with color coding
-- ============================================
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(50) NOT NULL DEFAULT 'hsl(38 92% 50%)',
    description TEXT NULL,
    icon VARCHAR(50) NULL,
    parent_category_id INT NULL,
    document_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_active (is_active),
    INDEX idx_parent (parent_category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. DOCUMENTS TABLE
-- Main table for storing document metadata
-- ============================================
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    category_id INT NOT NULL,
    
    -- File information
    file_type VARCHAR(20) NOT NULL,
    file_size BIGINT NOT NULL,
    file_size_formatted VARCHAR(20) NOT NULL,
    mime_type VARCHAR(100) NULL,
    
    -- S3 Storage information
    s3_key VARCHAR(500) NOT NULL,
    s3_url VARCHAR(1000) NOT NULL,
    s3_bucket VARCHAR(255) NULL,
    
    -- User tracking
    uploaded_by INT NOT NULL,
    
    -- Document metadata (for PDFs/Excel)
    page_count INT NULL,
    word_count INT NULL,
    author VARCHAR(255) NULL,
    title VARCHAR(500) NULL,
    subject VARCHAR(500) NULL,
    keywords TEXT NULL,
    
    -- AI-generated content
    summary TEXT NULL,
    extracted_text LONGTEXT NULL,
    ai_tags JSON NULL,
    suggested_category VARCHAR(100) NULL,
    
    -- Document status
    status ENUM('uploading', 'processing', 'ready', 'failed') DEFAULT 'ready',
    processing_status VARCHAR(50) NULL,
    error_message TEXT NULL,
    
    -- Version control
    version INT DEFAULT 1,
    parent_document_id INT NULL,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP NULL,
    archived_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_document_id) REFERENCES documents(id) ON DELETE SET NULL,
    
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_uploader (uploaded_by),
    INDEX idx_file_type (file_type),
    INDEX idx_status (status),
    INDEX idx_uploaded_at (uploaded_at),
    INDEX idx_s3_key (s3_key),
    INDEX idx_archived (is_archived),
    FULLTEXT idx_fulltext_search (name, summary, extracted_text, title, subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. DOCUMENT_VIEWS TABLE
-- Tracks document view history
-- ============================================
CREATE TABLE document_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    user_id INT NOT NULL,
    view_count INT DEFAULT 1,
    last_viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_doc_user (document_id, user_id),
    INDEX idx_document (document_id),
    INDEX idx_user (user_id),
    INDEX idx_viewed_at (last_viewed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. DOCUMENT_SHARES TABLE
-- Tracks document sharing between users
-- ============================================
CREATE TABLE document_shares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    shared_by INT NOT NULL,
    shared_with INT NOT NULL,
    permission ENUM('view', 'download', 'edit') DEFAULT 'view',
    message TEXT NULL,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_share (document_id, shared_with),
    INDEX idx_document (document_id),
    INDEX idx_shared_by (shared_by),
    INDEX idx_shared_with (shared_with),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INSERT DEFAULT DATA
-- ============================================

-- Default Admin User (password: admin123 - change in production!)
INSERT INTO users (name, email, password_hash, role, is_active) VALUES
('Admin User', 'admin@dochub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVKq1Q8K2', 'admin', TRUE),
('John Smith', 'john@dochub.com', NULL, 'user', TRUE),
('Sarah Johnson', 'sarah@dochub.com', NULL, 'user', TRUE),
('Mike Wilson', 'mike@dochub.com', NULL, 'user', TRUE);

-- Default Categories
INSERT INTO categories (name, color, description, document_count) VALUES
('Contracts', 'hsl(38 92% 50%)', 'Business contracts and agreements', 0),
('Reports', 'hsl(199 89% 48%)', 'Annual and financial reports', 0),
('Policies', 'hsl(262 83% 58%)', 'Company policies and procedures', 0),
('Guidelines', 'hsl(142 71% 45%)', 'Guidelines and standards', 0),
('Invoices', 'hsl(346 77% 50%)', 'Invoices and billing documents', 0),
('Legal', 'hsl(25 95% 53%)', 'Legal documents and compliance', 0);

-- ============================================
-- USEFUL QUERIES FOR REFERENCE
-- ============================================

-- Get all documents with category and uploader info
-- SELECT d.*, c.name as category_name, c.color as category_color, u.name as uploaded_by_name
-- FROM documents d
-- JOIN categories c ON d.category_id = c.id
-- JOIN users u ON d.uploaded_by = u.id
-- WHERE d.is_archived = FALSE
-- ORDER BY d.uploaded_at DESC;

-- Get document statistics
-- SELECT 
--     COUNT(*) as total_documents,
--     SUM(file_size) as total_size,
--     COUNT(DISTINCT category_id) as total_categories,
--     COUNT(DISTINCT uploaded_by) as total_uploaders
-- FROM documents
-- WHERE is_archived = FALSE;

-- Get category statistics
-- SELECT 
--     c.name,
--     c.color,
--     COUNT(d.id) as document_count,
--     SUM(d.file_size) as total_size
-- FROM categories c
-- LEFT JOIN documents d ON c.id = d.category_id AND d.is_archived = FALSE
-- GROUP BY c.id
-- ORDER BY document_count DESC;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Update category document counts
-- UPDATE categories c
-- SET document_count = (
--     SELECT COUNT(*) FROM documents d 
--     WHERE d.category_id = c.id AND d.is_archived = FALSE
-- );

-- Find orphaned documents (documents without valid category)
-- SELECT d.* FROM documents d
-- LEFT JOIN categories c ON d.category_id = c.id
-- WHERE c.id IS NULL;

-- Find duplicate documents by name and size
-- SELECT name, file_size, COUNT(*) as count
-- FROM documents
-- WHERE is_archived = FALSE
-- GROUP BY name, file_size
-- HAVING count > 1;






