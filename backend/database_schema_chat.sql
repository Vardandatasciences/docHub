-- ============================================
-- Chatbot Tables Migration
-- Adds chat sessions and messages tables for AI Document Assistant
-- ============================================

-- Drop tables if they exist (for clean migration)
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;

-- ============================================
-- 1. CHAT_SESSIONS TABLE
-- Stores chat sessions (conversations)
-- ============================================
CREATE TABLE chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    document_id INT NULL,  -- NULL for general queries across all documents
    session_name VARCHAR(255) NULL,  -- Optional: user can name the session
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_document (document_id),
    INDEX idx_created_at (created_at),
    INDEX idx_session_user_document (user_id, document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. CHAT_MESSAGES TABLE
-- Stores individual messages in conversations
-- ============================================
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    metadata JSON NULL,  -- Store document references, sources, tokens used, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at),
    INDEX idx_message_session_role (session_id, role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Migration Complete
-- ============================================




