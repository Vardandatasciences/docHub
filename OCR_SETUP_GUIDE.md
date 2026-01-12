# 🔍 OCR & Auto-Categorization Setup Guide

## ✅ Implementation Complete!

All modules have been created and integrated. Here's what was implemented:

### 📦 Modules Created

1. ✅ **`backend/utils/ocr_helper.py`** - OCR text extraction from images/scanned PDFs
2. ✅ **`backend/utils/ollama_helper.py`** - Ollama API wrapper
3. ✅ **`backend/utils/ai_categorizer.py`** - AI category suggestion using Ollama
4. ✅ **`backend/utils/ai_tagger.py`** - AI tag generation using Ollama
5. ✅ **`backend/utils/document_processor.py`** - Background processing pipeline

### 🔧 Configuration Updated

- ✅ Added image file types to `ALLOWED_EXTENSIONS` (jpg, jpeg, png, tiff, bmp)
- ✅ Added Ollama configuration to `config.py`
- ✅ Updated upload route to trigger background processing

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `pytesseract==0.3.10` - OCR library
- `Pillow==10.1.0` - Image processing
- `pdf2image==1.16.3` - PDF to image conversion
- `ollama==0.1.7` - Ollama client

### Step 2: Install System Dependencies

#### Windows:
1. **Install Tesseract OCR:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - Add to PATH or set environment variable:
     ```env
     TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
     ```

2. **Install Poppler (for PDF to image):**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract and add `bin` folder to PATH

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install tesseract
brew install poppler
```

### Step 3: Verify Environment Variables

Your `.env` file should have:
```env
OLLAMA_BASE_URL=http://13.205.15.232:11434
OLLAMA_MODEL=llama3.1:8b

# Optional: If Tesseract not in PATH
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Step 4: Test Ollama Connection

Test if Ollama is accessible:
```python
from utils.ollama_helper import OllamaHelper

helper = OllamaHelper()
if helper.check_connection():
    print("✅ Ollama connection successful!")
else:
    print("❌ Ollama connection failed")
```

### Step 5: Test OCR

Test OCR with a sample image:
```python
from utils.ocr_helper import OCRHelper

ocr = OCRHelper()
text, metadata = ocr.extract_from_image("path/to/test_image.jpg")
print(f"Extracted text: {text[:200]}...")
print(f"Confidence: {metadata['confidence']}%")
```

---

## 🧪 Testing the Feature

### Test 1: Upload Image File

1. Start your Flask server:
   ```bash
   cd backend
   python run.py
   ```

2. Upload a JPG/PNG image through the frontend or API
3. Check server logs - you should see:
   ```
   🔍 Starting processing for document ID: X
   📸 Document needs OCR
   ✅ OCR completed: X words extracted
   🤖 Starting AI analysis...
   ✅ Document processed successfully!
   ```

4. Check database:
   ```sql
   SELECT id, name, extracted_text, suggested_category, ai_tags, status 
   FROM documents 
   WHERE id = [document_id];
   ```

### Test 2: Upload Scanned PDF

1. Upload a scanned PDF (image-based, not text-based)
2. System should:
   - Detect it's scanned
   - Run OCR on pages
   - Generate category suggestion
   - Generate tags

### Test 3: Check Processing Status

Query document status:
```sql
SELECT id, name, status, processing_status, suggested_category, ai_tags
FROM documents
WHERE status = 'processing' OR suggested_category IS NOT NULL;
```

---

## 📊 How It Works

### Flow Diagram

```
User Uploads File
      ↓
File Saved to S3 + Database
      ↓
Background Thread Started
      ↓
┌─────────────────────────┐
│ Step 1: OCR Extraction  │
│ - Check if needs OCR    │
│ - Extract text          │
│ - Save to DB            │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Step 2: AI Analysis    │
│ - Get categories        │
│ - Suggest category      │
│ - Generate tags         │
│ - Update DB            │
└─────────────────────────┘
      ↓
Processing Complete ✅
```

### Database Fields Used

- `extracted_text` - OCR output (LONGTEXT)
- `suggested_category` - AI suggested category (VARCHAR)
- `ai_tags` - Generated tags (JSON array)
- `status` - Document status (processing/ready/failed)
- `processing_status` - Current step (ocr/ai_analysis/completed)
- `word_count` - Word count from OCR

---

## 🐛 Troubleshooting

### Issue: Tesseract not found

**Error:** `TesseractNotFoundError`

**Solution:**
- Install Tesseract (see Step 2)
- Set `TESSERACT_CMD` in `.env` or environment
- Verify: `tesseract --version` in terminal

### Issue: Poppler not found

**Error:** `pdf2image.exceptions.PDFInfoNotInstalledError`

**Solution:**
- Install Poppler (see Step 2)
- Add to PATH
- Verify: `pdftoppm -h` in terminal

### Issue: Ollama connection failed

**Error:** `Ollama connection failed`

**Solution:**
1. Check `OLLAMA_BASE_URL` in `.env`
2. Test connection: `curl http://13.205.15.232:11434/api/tags`
3. Verify Ollama server is running
4. Check firewall/network settings

### Issue: OCR returns empty text

**Possible causes:**
- Image quality too poor
- Image is not in English (Tesseract default is 'eng')
- Image is corrupted

**Solution:**
- Use higher quality images
- For other languages, modify `ocr_helper.py` to use different language

### Issue: AI categorization fails

**Check:**
1. Ollama server is accessible
2. Model `llama3.1:8b` is available on server
3. Check server logs for detailed error

---

## 📈 Performance Notes

### Processing Times (Approximate)

- **Small image (1 page):** 5-10 seconds
- **Medium image (5 pages):** 20-40 seconds
- **Large PDF (10+ pages):** 1-3 minutes
- **AI Analysis:** 2-5 seconds per document

### Optimization Tips

1. **Limit PDF pages:** Currently processes max 10 pages (configurable in `ocr_helper.py`)
2. **Background processing:** Non-blocking, upload returns immediately
3. **Error handling:** Graceful degradation - upload succeeds even if processing fails

---

## 🎯 Next Steps

1. ✅ **Test with real documents**
2. ✅ **Monitor processing times**
3. ✅ **Check category suggestions accuracy**
4. ✅ **Review generated tags**

### Optional Enhancements

- Add progress tracking (WebSocket updates)
- Add retry logic for failed processing
- Add batch processing for multiple files
- Add language detection for OCR
- Add confidence threshold for auto-categorization

---

## 📝 API Response Changes

The upload endpoint now returns additional fields:

```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 123,
    "name": "document.pdf",
    "status": "processing",  // or "ready"
    "suggestedCategory": "Contracts",  // After processing
    "aiTags": ["contract", "legal", "agreement"]  // After processing
  },
  "processing": "started"  // or "not_needed"
}
```

---

## ✅ Checklist

- [x] Dependencies added to requirements.txt
- [x] OCR module created
- [x] Ollama helper created
- [x] AI categorizer created
- [x] AI tagger created
- [x] Document processor created
- [x] Upload route updated
- [x] Config updated
- [ ] Tesseract installed
- [ ] Poppler installed
- [ ] Ollama connection tested
- [ ] Test upload completed

---

**Ready to test!** 🚀

Upload a document and check the logs to see the processing in action!




