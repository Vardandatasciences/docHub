# 🤖 AI Document Assistant Chatbot - Complete Implementation Plan

## Overview
This document outlines all steps needed to implement the AI Document Assistant Chatbot feature for DocHub.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Schema Changes](#database-schema-changes)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Testing & Deployment](#testing--deployment)
6. [Estimated Timeline](#estimated-timeline)

---

## 🔧 Prerequisites

### 1. Environment Setup
- ✅ OpenAI API key (or Anthropic Claude API key as alternative)
- ✅ Python packages to install
- ✅ Environment variables configuration

### 2. Required Python Packages
```bash
# Add to backend/requirements.txt
openai>=1.3.0          # OpenAI API client
tiktoken>=0.5.0        # Token counting (optional but recommended)
python-dotenv>=1.0.0   # Already have this
```

### 3. Required Frontend Packages
```bash
# Already have React, but may need:
# Check if these are in package.json, add if not:
# - @tanstack/react-query (optional, for better state management)
# - react-markdown (optional, for formatting AI responses)
```

---

## 🗄️ Database Schema Changes

### Step 1: Create Chat Sessions Table
**Purpose:** Store chat sessions (conversations)

```sql
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
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Step 2: Create Chat Messages Table
**Purpose:** Store individual messages in conversations

```sql
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
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Step 3: Create SQL Migration File
**File:** `backend/database_schema_chat.sql`

```sql
-- Chatbot Tables Migration
-- Run this to add chatbot functionality to existing database

-- Add chatbot tables
-- (Include the CREATE TABLE statements from above)

-- Optional: Add indexes for performance
CREATE INDEX idx_session_user_document ON chat_sessions(user_id, document_id);
CREATE INDEX idx_message_session_role ON chat_messages(session_id, role);
```

---

## 🔙 Backend Implementation

### Step 4: Create AI Chatbot Utility Module
**File:** `backend/utils/ai_chatbot.py`

**Responsibilities:**
- Initialize OpenAI client
- Handle RAG (Retrieval Augmented Generation)
- Process user questions
- Generate responses using document context
- Manage token limits
- Handle errors gracefully

**Key Functions Needed:**
1. `initialize_openai_client()` - Setup OpenAI client
2. `get_document_context(document_id, max_tokens)` - Retrieve document text
3. `search_documents(query, user_id, limit)` - Semantic search across documents
4. `generate_response(question, context, chat_history)` - Generate AI response
5. `stream_response(question, context, chat_history)` - Stream responses (future enhancement)

### Step 5: Create Chat Routes
**File:** `backend/routes/chat.py`

**Endpoints to Create:**
1. `POST /api/chat/sessions` - Create new chat session
2. `GET /api/chat/sessions` - List user's chat sessions
3. `GET /api/chat/sessions/<session_id>` - Get session with messages
4. `DELETE /api/chat/sessions/<session_id>` - Delete session
5. `POST /api/chat/sessions/<session_id>/messages` - Send message and get response
6. `POST /api/chat/quick-ask` - Quick question without creating session (optional)

**Request/Response Format:**
```python
# POST /api/chat/sessions/<session_id>/messages
Request:
{
    "message": "What's in this contract about payment terms?",
    "document_id": 123,  # Optional: specific document
    "stream": false  # Optional: for streaming (future)
}

Response:
{
    "message_id": 456,
    "response": "Based on the document, the payment terms are...",
    "sources": [{"document_id": 123, "document_name": "Contract.pdf"}],
    "tokens_used": 150,
    "created_at": "2025-01-XX..."
}
```

### Step 6: Update App.py to Register Chat Routes
**File:** `backend/app.py`

Add:
```python
from routes.chat import chat_bp
app.register_blueprint(chat_bp, url_prefix='/api/chat')
```

### Step 7: Update Config for OpenAI
**File:** `backend/config.py`

Add configuration:
```python
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')  # or 'gpt-3.5-turbo'
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.3'))  # Lower = more focused
```

### Step 8: Environment Variables
**File:** `backend/.env` (or `.env.example`)

Add:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.3
```

---

## 🎨 Frontend Implementation

### Step 9: Create TypeScript Types
**File:** `src/types/chat.ts`

```typescript
export interface ChatSession {
  id: number;
  userId: number;
  documentId: number | null;
  sessionName: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: number;
  sessionId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata: {
    sources?: Array<{ documentId: number; documentName: string }>;
    tokensUsed?: number;
  } | null;
  createdAt: string;
}

export interface ChatSessionWithMessages extends ChatSession {
  messages: ChatMessage[];
}
```

### Step 10: Create Chat Service
**File:** `src/services/chat.service.ts`

**Functions:**
- `createSession(documentId?: number, sessionName?: string)`
- `getSessions()`
- `getSession(sessionId: number)`
- `deleteSession(sessionId: number)`
- `sendMessage(sessionId: number, message: string, documentId?: number)`

### Step 11: Update API Config
**File:** `src/lib/api-config.ts`

Add chat endpoints:
```typescript
chat: {
  sessions: '/chat/sessions',
  sessionById: (id: number) => `/chat/sessions/${id}`,
  messages: (sessionId: number) => `/chat/sessions/${sessionId}/messages`,
  quickAsk: '/chat/quick-ask',
}
```

### Step 12: Create Chat Interface Component
**File:** `src/components/ChatInterface.tsx`

**Features:**
- Chat message list (user and assistant messages)
- Input field for typing messages
- Document selector (if querying specific document)
- Session name editor
- Loading states
- Error handling
- Message bubbles with timestamps
- Source citations (if document referenced)

**UI Components to Use:**
- Card (from shadcn/ui) - for chat container
- ScrollArea - for message list
- Input/Textarea - for message input
- Button - for send
- Avatar - for user/assistant indicators
- Badge - for source citations

### Step 13: Create Chat Sessions List Component
**File:** `src/components/ChatSessionsList.tsx`

**Features:**
- List of all chat sessions
- Create new session button
- Delete session
- Session preview (last message, timestamp)
- Active session indicator

### Step 14: Create Chat Page
**File:** `src/pages/Chat.tsx`

**Layout:**
- Sidebar with sessions list
- Main area with chat interface
- Optional: Document selector in header

### Step 15: Add Route to App
**File:** `src/App.tsx` or routing configuration

Add route:
```tsx
<Route path="/chat" element={<Chat />} />
<Route path="/chat/:sessionId" element={<Chat />} />
```

### Step 16: Add Navigation Link
**File:** `src/components/Header.tsx` or Navigation component

Add "Chat" link to navigation menu

### Step 17: Optional: Integrate with Document View
**File:** `src/components/DocumentCard.tsx` or document detail page

Add "Ask AI" button that opens chat with document pre-selected

---

## 🧪 Testing & Deployment

### Step 18: Backend Testing
**Create:** `backend/tests/test_chat.py` (optional but recommended)

Test cases:
- Create session
- Send message
- Get session history
- Delete session
- Error handling (no API key, invalid document, etc.)
- Token limit handling

### Step 19: Frontend Testing
- Test chat interface UI
- Test message sending
- Test session management
- Test error states
- Test loading states

### Step 20: Integration Testing
- Full flow: Create session → Send message → Receive response
- Test with actual documents
- Test with different document types
- Performance testing (response time)

### Step 21: Error Handling
**Backend:**
- API key validation
- Rate limiting
- Token limit exceeded
- Invalid document access
- Network errors

**Frontend:**
- Network error display
- Loading states
- Empty states
- Error messages

### Step 22: Security Considerations
- ✅ JWT authentication (already have)
- ✅ User can only access their own sessions
- ✅ Validate document ownership before allowing queries
- ✅ Rate limiting on chat endpoints
- ✅ Sanitize user input
- ✅ API key stored securely in environment variables

---

## 📅 Estimated Timeline

### Week 1: Database & Backend Core (3-4 days)
- [ ] Day 1: Database schema creation and migration
- [ ] Day 2: AI chatbot utility module (`ai_chatbot.py`)
- [ ] Day 3: Chat routes implementation
- [ ] Day 4: Testing and bug fixes

### Week 2: Frontend Implementation (4-5 days)
- [ ] Day 1: TypeScript types and service layer
- [ ] Day 2: Chat interface component
- [ ] Day 3: Sessions list component
- [ ] Day 4: Chat page and routing
- [ ] Day 5: Integration with document views

### Week 3: Polish & Testing (2-3 days)
- [ ] Day 1: Error handling and edge cases
- [ ] Day 2: UI/UX improvements
- [ ] Day 3: Integration testing and documentation

**Total Estimated Time: 2-3 weeks**

---

## 🚀 Implementation Order (Recommended)

### Phase 1: Foundation (Must Have)
1. ✅ Database schema
2. ✅ AI chatbot utility (basic version)
3. ✅ Chat routes (create session, send message, get messages)
4. ✅ Frontend chat interface (basic)

### Phase 2: Enhancements (Should Have)
5. ✅ Session management UI
6. ✅ Document selector in chat
7. ✅ Source citations
8. ✅ Error handling

### Phase 3: Advanced Features (Nice to Have)
9. ⭐ Streaming responses (real-time)
10. ⭐ Multi-document search (query across all documents)
11. ⭐ Chat history export
12. ⭐ Suggested questions
13. ⭐ Chat sharing

---

## 💡 Key Implementation Details

### RAG (Retrieval Augmented Generation) Strategy

**Option 1: Single Document Query**
- User selects a document
- Use `extracted_text` from database
- Send to AI with context window

**Option 2: Multi-Document Search**
- User asks general question
- Search across all user's documents (using `extracted_text`)
- Retrieve top N relevant documents
- Combine context and send to AI

**Option 3: Hybrid Approach (Recommended)**
- If `document_id` provided → use single document
- If no `document_id` → search across documents, use top results

### Token Management
- GPT-4: ~8000 token context window
- Reserve ~1000 tokens for response
- Use ~6000 tokens for document context
- Truncate if document is too long

### Cost Optimization
- Use GPT-3.5-turbo for simple queries (cheaper)
- Use GPT-4 for complex analysis (better quality)
- Cache common queries (future optimization)
- Batch processing (future optimization)

---

## 🔍 Next Steps After Basic Implementation

1. **Semantic Search Integration** - Use embeddings for better document retrieval
2. **Streaming Responses** - Real-time response streaming
3. **Voice Input** - Speak questions instead of typing
4. **Document Summarization** - Auto-summarize before chat context
5. **Multi-language Support** - Support questions in different languages
6. **Analytics** - Track popular questions, document queries, etc.

---

## 📝 Files to Create/Modify Summary

### New Files:
- ✅ `backend/database_schema_chat.sql`
- ✅ `backend/utils/ai_chatbot.py`
- ✅ `backend/routes/chat.py`
- ✅ `src/types/chat.ts`
- ✅ `src/services/chat.service.ts`
- ✅ `src/components/ChatInterface.tsx`
- ✅ `src/components/ChatSessionsList.tsx`
- ✅ `src/pages/Chat.tsx`

### Modified Files:
- ✅ `backend/requirements.txt` (add openai)
- ✅ `backend/config.py` (add OpenAI config)
- ✅ `backend/app.py` (register chat blueprint)
- ✅ `backend/.env` (add OpenAI API key)
- ✅ `src/lib/api-config.ts` (add chat endpoints)
- ✅ `src/App.tsx` (add chat route)
- ✅ `src/components/Header.tsx` (add chat link)

---

## ✅ Pre-Implementation Checklist

- [ ] Get OpenAI API key
- [ ] Test OpenAI API connection
- [ ] Backup database
- [ ] Review existing authentication flow
- [ ] Understand document access permissions
- [ ] Review `extracted_text` field population (ensure it's being populated)

---

## 🎯 Success Criteria

The feature is complete when:
- ✅ Users can create chat sessions
- ✅ Users can ask questions about documents
- ✅ AI provides accurate answers based on document content
- ✅ Chat history is saved and retrievable
- ✅ Multiple sessions can be managed
- ✅ Error handling works gracefully
- ✅ UI is intuitive and responsive
- ✅ Authentication and authorization work correctly

---

*Ready to start implementation? Begin with Step 1 (Database Schema)!*




