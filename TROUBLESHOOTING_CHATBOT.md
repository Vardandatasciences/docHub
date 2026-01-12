# Chatbot Troubleshooting Guide

## Issue: Document Selected But AI Says "No Documents Found"

### Problem
You select a document in the dropdown (e.g., `risk_register_export.pdf`), but when you ask questions, the AI responds saying "no relevant documents were found" or similar.

### Root Causes

1. **Document doesn't have `extracted_text` populated**
   - The document might not have been processed yet
   - OCR might not have run on scanned PDFs
   - The document might be empty or corrupted

2. **Document ID not being passed correctly**
   - The selected document ID might not be sent with the message request

### Solutions

#### Check 1: Verify Document Has Extracted Text

Run this SQL query to check if your document has text:

```sql
SELECT id, name, 
       LENGTH(extracted_text) as text_length,
       LENGTH(summary) as summary_length,
       status,
       processing_status
FROM documents 
WHERE name LIKE '%risk_register%';
```

If `text_length` is 0 or NULL, the document doesn't have extracted text.

#### Check 2: Check Backend Logs

When you send a message, look for these log messages in your backend terminal:

```
🔍 Document ID from request: <id>, from session: <id>, using: <id>
🔍 Fetching context for document ID: <id>
✅ Retrieved document context: <name> (<length> chars)
```

If you see:
- `⚠️ Document <id> has no extracted text or summary` - Document needs processing
- `❌ Error fetching document context` - Database or permission issue

#### Check 3: Process the Document

If the document doesn't have extracted text:

1. **Re-upload the document** - This will trigger text extraction
2. **Or manually trigger processing** (if you have a processing endpoint)
3. **Check OCR status** - For scanned PDFs, ensure OCR has run

#### Check 4: Verify Frontend is Sending Document ID

Open browser DevTools (F12) → Network tab → Find the POST request to `/api/chat/sessions/<id>/messages`

Check the request payload:
```json
{
  "message": "your question",
  "document_id": 123  // ← Should be present if document selected
}
```

If `document_id` is missing, the frontend isn't passing it correctly.

### Quick Fix

If the document doesn't have extracted text, try:

1. Select "All Documents (General Query)" instead
2. Or select a different document that has been processed
3. Wait for document processing to complete
4. Re-upload the document to trigger extraction

### Testing Steps

1. **Check document in database:**
   ```sql
   SELECT id, name, 
          extracted_text IS NOT NULL as has_text,
          LENGTH(extracted_text) as text_len
   FROM documents 
   WHERE id = YOUR_DOCUMENT_ID;
   ```

2. **Test with a document that has text:**
   - Select a document you know has extracted_text
   - Ask: "What is this document about?"
   - Should work correctly

3. **Check backend logs:**
   - Send a message
   - Look for document context retrieval messages
   - Verify no errors

### Expected Behavior

When a document IS selected and HAS extracted_text:
```
📨 Processing message for session X, user Y
📄 Target document ID: 123
🔍 Fetching context for document ID: 123
✅ Retrieved document context: risk_register_export.pdf (5000 chars)
✅ Using document context from: risk_register_export.pdf
🤖 Requesting chatbot response from Ollama...
✅ Received chatbot response (200 chars)
```

When a document IS selected but DOESN'T have extracted_text:
```
📨 Processing message for session X, user Y
📄 Target document ID: 123
🔍 Fetching context for document ID: 123
⚠️ Document 123 has no extracted text or summary
⚠️ Document context error: Document has no extractable text content...
```

### Next Steps

If the document needs processing:
1. Check your document processing pipeline
2. Ensure OCR is enabled for scanned documents
3. Verify documents are being processed after upload




