# 🔍 Intelligent OCR with Auto-Categorization - Implementation Plan

## 📋 Overview

This document outlines the complete implementation plan for **Feature 2: Intelligent OCR with Auto-Categorization**. This feature will enable DocHub to:
1. Extract text from scanned documents and images using OCR
2. Automatically categorize documents based on content analysis
3. Generate smart tags and metadata
4. Support image file formats (JPG, PNG, TIFF)

---

## 🎯 Current State Analysis

### ✅ What We Already Have

1. **Database Schema** - Ready for OCR/AI:
   - `extracted_text` (LONGTEXT) - For storing OCR output
   - `ai_tags` (JSON) - For auto-generated tags
   - `suggested_category` (VARCHAR) - For AI category suggestions
   - `summary` (TEXT) - For document summaries
   - `status` (ENUM) - Can track processing status

2. **PDF Text Extraction** - Partial:
   - `s3.py` has PDF text extraction for digital PDFs
   - Uses PyPDF2 and pdfplumber
   - **BUT:** Doesn't handle scanned PDFs (images)

3. **File Upload Flow**:
   - Upload route in `backend/routes/documents.py`
   - S3 integration working
   - File validation in place

### ❌ What's Missing

1. **OCR Capability:**
   - No image file support (JPG, PNG, TIFF)
   - No OCR for scanned PDFs
   - No OCR for image files

2. **Auto-Categorization:**
   - Manual category selection required
   - No AI-powered category suggestion
   - No content-based categorization

3. **Smart Tagging:**
   - No automatic tag generation
   - No metadata extraction from content

---

## 🏗️ Architecture Design

### High-Level Flow

```
┌─────────────┐
│ User Upload │
│  (File)     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ File Validation │
│ (Type, Size)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Upload to S3    │
│ (Save to DB)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────────┐
│ Background Job   │─────▶│ OCR Processing   │
│ (Async)         │      │ (Tesseract/API) │
└──────┬──────────┘      └────────┬─────────┘
       │                           │
       │                           ▼
       │                  ┌──────────────────┐
       │                  │ Extract Text     │
       │                  │ (OCR Output)     │
       │                  └────────┬─────────┘
       │                           │
       │                           ▼
       │                  ┌──────────────────┐
       │                  │ AI Analysis      │
       │                  │ (OpenAI API)     │
       │                  └────────┬─────────┘
       │                           │
       │                           ▼
       │                  ┌──────────────────┐
       │                  │ Generate:        │
       │                  │ - Category       │
       │                  │ - Tags          │
       │                  │ - Summary       │
       │                  └────────┬─────────┘
       │                           │
       └───────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Update Database │
         │ (extracted_text,│
         │  ai_tags,      │
         │  suggested_     │
         │  category)      │
         └─────────────────┘
```

---

## 📦 Implementation Components

### 1. OCR Module (`backend/utils/ocr_helper.py`)

**Purpose:** Extract text from images and scanned documents

**Features:**
- Support for JPG, PNG, TIFF, scanned PDFs
- Use Tesseract OCR (free) or Google Cloud Vision (better accuracy)
- Handle multi-page documents
- Error handling and fallbacks

**File Types to Support:**
- Images: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`
- Scanned PDFs: Detect if PDF is image-based

### 2. AI Categorizer (`backend/utils/ai_categorizer.py`)

**Purpose:** Analyze document content and suggest category

**Features:**
- Use OpenAI GPT-3.5-turbo (cost-effective)
- Analyze extracted text
- Match to existing categories
- Confidence scoring

### 3. AI Tag Generator (`backend/utils/ai_tagger.py`)

**Purpose:** Generate relevant tags from document content

**Features:**
- Extract key topics, entities, dates
- Generate 3-5 relevant tags
- Store as JSON array

### 4. Background Job Processor (`backend/utils/document_processor.py`)

**Purpose:** Process documents asynchronously after upload

**Features:**
- Run OCR in background
- Run AI analysis in background
- Update database with results
- Handle errors gracefully

---

## 🔧 Technical Implementation

### Step 1: Add Dependencies

**Add to `backend/requirements.txt`:**

```python
# OCR Libraries
pytesseract==0.3.10          # Tesseract OCR wrapper
Pillow==10.1.0                # Image processing
pdf2image==1.16.3             # Convert PDF pages to images
poppler-utils                 # Required for pdf2image (system package)

# AI Libraries
openai==1.3.0                 # OpenAI API for categorization

# Image Processing
opencv-python==4.8.1.78       # Advanced image processing (optional)
```

**System Requirements:**
- Tesseract OCR must be installed on system
- Poppler (for PDF to image conversion)

### Step 2: Update File Type Support

**Update `backend/config.py`:**

```python
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv',
    # Add image formats for OCR
    'jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp'
}
```

### Step 3: Create OCR Helper

**File: `backend/utils/ocr_helper.py`**

```python
"""
OCR Helper - Extract text from images and scanned documents
"""
import pytesseract
from PIL import Image
import pdf2image
import os
import tempfile
from typing import Tuple, Optional

# Configure Tesseract path (Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRHelper:
    """Handle OCR operations for images and scanned documents"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR helper
        
        Args:
            tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Check if PDF is scanned (image-based) or text-based
        
        Returns:
            True if PDF appears to be scanned
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                # Check first page for text
                if len(pdf_reader.pages) > 0:
                    first_page_text = pdf_reader.pages[0].extract_text()
                    # If very little text, likely scanned
                    return len(first_page_text.strip()) < 50
        except:
            pass
        return True  # Assume scanned if can't determine
    
    def extract_from_image(self, image_path: str) -> Tuple[str, dict]:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            image = Image.open(image_path)
            
            # OCR with detailed output
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Get OCR metadata
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            metadata = {
                'confidence': sum([int(conf) for conf in data['conf'] if conf != '-1']) / len([c for c in data['conf'] if c != '-1']) if data['conf'] else 0,
                'word_count': len([w for w in data['text'] if w.strip()]),
                'page_count': 1
            }
            
            return text.strip(), metadata
            
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def extract_from_pdf(self, pdf_path: str, max_pages: int = 10) -> Tuple[str, dict]:
        """
        Extract text from scanned PDF
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (for performance)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(pdf_path, first_page=1, last_page=max_pages)
            
            full_text = ""
            total_confidence = 0
            word_count = 0
            
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng')
                full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
                # Get confidence for this page
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                page_confidences = [int(c) for c in data['conf'] if c != '-1']
                if page_confidences:
                    total_confidence += sum(page_confidences) / len(page_confidences)
                
                word_count += len([w for w in data['text'] if w.strip()])
            
            metadata = {
                'confidence': total_confidence / len(images) if images else 0,
                'word_count': word_count,
                'page_count': len(images),
                'pages_processed': len(images)
            }
            
            return full_text.strip(), metadata
            
        except Exception as e:
            raise Exception(f"PDF OCR extraction failed: {str(e)}")
    
    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, dict]:
        """
        Main method to extract text from any supported file
        
        Args:
            file_path: Path to file
            file_type: File extension (pdf, jpg, png, etc.)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        file_type_lower = file_type.lower()
        
        # Image files
        if file_type_lower in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']:
            return self.extract_from_image(file_path)
        
        # PDF files
        elif file_type_lower == 'pdf':
            # Check if scanned
            if self.is_scanned_pdf(file_path):
                return self.extract_from_pdf(file_path)
            else:
                # Use existing PDF text extraction (from s3.py)
                # Return empty for now, will be handled by existing logic
                return "", {'note': 'Digital PDF - use existing extraction'}
        
        else:
            raise ValueError(f"Unsupported file type for OCR: {file_type}")
```

### Step 4: Create AI Categorizer

**File: `backend/utils/ai_categorizer.py`**

```python
"""
AI Categorizer - Use AI to suggest document categories
"""
import os
from openai import OpenAI
from typing import Optional, Dict
from database import execute_query


class AICategorizer:
    """Use AI to categorize documents based on content"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=api_key)
    
    def get_existing_categories(self) -> list:
        """Get list of existing categories from database"""
        categories = execute_query(
            "SELECT id, name, description FROM categories WHERE is_active = TRUE",
            (),
            fetch_all=True
        )
        return [f"{cat['name']}" for cat in categories]
    
    def suggest_category(self, document_text: str, document_name: str = "") -> Dict:
        """
        Suggest category for document based on content
        
        Args:
            document_text: Extracted text from document
            document_name: Original filename (for context)
            
        Returns:
            Dict with category_name, confidence, reasoning
        """
        try:
            # Get existing categories
            categories = self.get_existing_categories()
            categories_str = ", ".join(categories)
            
            # Limit text length for API (keep first 3000 chars)
            text_preview = document_text[:3000] if len(document_text) > 3000 else document_text
            
            prompt = f"""Analyze this document and suggest the most appropriate category.

Document Name: {document_name}
Document Content Preview:
{text_preview}

Available Categories: {categories_str}

Analyze the document content and determine which category it best fits into.
Consider the document's purpose, content type, and subject matter.

Respond in this exact JSON format:
{{
    "category_name": "CategoryName",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this category fits"
}}

If the document doesn't clearly fit any category, suggest "General" or the closest match."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document categorization assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            # Sometimes GPT wraps JSON in markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return {
                'suggested_category': result.get('category_name', 'General'),
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', '')
            }
            
        except Exception as e:
            print(f"⚠️ AI categorization failed: {str(e)}")
            # Fallback: return default
            return {
                'suggested_category': 'General',
                'confidence': 0.0,
                'reasoning': f'Categorization failed: {str(e)}'
            }
```

### Step 5: Create AI Tag Generator

**File: `backend/utils/ai_tagger.py`**

```python
"""
AI Tag Generator - Generate relevant tags from document content
"""
import os
from openai import OpenAI
from typing import List, Dict
import json


class AITagger:
    """Generate smart tags from document content"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=api_key)
    
    def generate_tags(self, document_text: str, document_name: str = "") -> List[str]:
        """
        Generate relevant tags from document
        
        Args:
            document_text: Extracted text
            document_name: Filename for context
            
        Returns:
            List of tag strings
        """
        try:
            # Limit text for API
            text_preview = document_text[:2000] if len(document_text) > 2000 else document_text
            
            prompt = f"""Analyze this document and generate 3-5 relevant tags.

Document Name: {document_name}
Content:
{text_preview}

Extract key topics, themes, document type, and important entities.
Generate concise, relevant tags (single words or short phrases).

Respond with a JSON array of strings only:
["tag1", "tag2", "tag3"]"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document tagging assistant. Respond with JSON array only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            tags = json.loads(result_text)
            
            # Ensure it's a list and limit to 5 tags
            if isinstance(tags, list):
                return tags[:5]
            else:
                return [str(tags)] if tags else []
                
        except Exception as e:
            print(f"⚠️ Tag generation failed: {str(e)}")
            return []
```

### Step 6: Create Document Processor

**File: `backend/utils/document_processor.py`**

```python
"""
Document Processor - Background processing for OCR and AI analysis
"""
import threading
from typing import Dict
from database import execute_query
from utils.ocr_helper import OCRHelper
from utils.ai_categorizer import AICategorizer
from utils.ai_tagger import AITagger
import os


class DocumentProcessor:
    """Process documents in background (OCR + AI)"""
    
    def __init__(self):
        self.ocr_helper = OCRHelper()
        self.ai_categorizer = AICategorizer()
        self.ai_tagger = AITagger()
    
    def process_document(self, document_id: int, file_path: str, file_type: str):
        """
        Process document: OCR + AI analysis
        
        Args:
            document_id: Document ID in database
            file_path: Path to file
            file_type: File extension
        """
        try:
            # Update status to processing
            execute_query(
                "UPDATE documents SET status = 'processing', processing_status = 'ocr' WHERE id = %s",
                (document_id,),
                commit=True
            )
            
            # Step 1: OCR Extraction
            extracted_text = ""
            ocr_metadata = {}
            
            # Check if file needs OCR
            needs_ocr = file_type.lower() in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']
            is_scanned_pdf = False
            
            if file_type.lower() == 'pdf':
                is_scanned_pdf = self.ocr_helper.is_scanned_pdf(file_path)
                needs_ocr = is_scanned_pdf
            
            if needs_ocr:
                print(f"🔍 Running OCR on document {document_id}...")
                extracted_text, ocr_metadata = self.ocr_helper.extract_text(file_path, file_type)
                
                # Update with OCR results
                execute_query(
                    """
                    UPDATE documents 
                    SET extracted_text = %s, 
                        processing_status = 'ai_analysis',
                        word_count = %s
                    WHERE id = %s
                    """,
                    (extracted_text, ocr_metadata.get('word_count', 0), document_id),
                    commit=True
                )
            else:
                # For digital PDFs, text extraction happens elsewhere
                # Just mark as ready for AI analysis
                execute_query(
                    "UPDATE documents SET processing_status = 'ai_analysis' WHERE id = %s",
                    (document_id,),
                    commit=True
                )
            
            # Step 2: AI Analysis (if we have text)
            if extracted_text or not needs_ocr:
                print(f"🤖 Running AI analysis on document {document_id}...")
                
                # Get document name for context
                doc = execute_query(
                    "SELECT name, original_name FROM documents WHERE id = %s",
                    (document_id,),
                    fetch_one=True
                )
                doc_name = doc['name'] if doc else ""
                
                # Get text for AI (use extracted_text if available, or fetch from DB)
                if not extracted_text:
                    doc_with_text = execute_query(
                        "SELECT extracted_text FROM documents WHERE id = %s",
                        (document_id,),
                        fetch_one=True
                    )
                    extracted_text = doc_with_text.get('extracted_text', '') if doc_with_text else ''
                
                if extracted_text:
                    # Generate category suggestion
                    category_result = self.ai_categorizer.suggest_category(extracted_text, doc_name)
                    
                    # Generate tags
                    tags = self.ai_tagger.generate_tags(extracted_text, doc_name)
                    
                    # Update database with AI results
                    import json
                    execute_query(
                        """
                        UPDATE documents 
                        SET suggested_category = %s,
                            ai_tags = %s,
                            processing_status = 'completed',
                            status = 'ready'
                        WHERE id = %s
                        """,
                        (
                            category_result['suggested_category'],
                            json.dumps(tags),
                            document_id
                        ),
                        commit=True
                    )
                    
                    print(f"✅ Document {document_id} processed successfully")
                    print(f"   Suggested Category: {category_result['suggested_category']}")
                    print(f"   Tags: {tags}")
                else:
                    # No text to analyze
                    execute_query(
                        "UPDATE documents SET status = 'ready', processing_status = 'completed' WHERE id = %s",
                        (document_id,),
                        commit=True
                    )
            else:
                # OCR failed or no text extracted
                execute_query(
                    "UPDATE documents SET status = 'ready', processing_status = 'completed' WHERE id = %s",
                    (document_id,),
                    commit=True
                )
                
        except Exception as e:
            print(f"❌ Error processing document {document_id}: {str(e)}")
            # Update status to failed
            execute_query(
                "UPDATE documents SET status = 'failed', error_message = %s WHERE id = %s",
                (str(e), document_id),
                commit=True
            )
    
    def process_async(self, document_id: int, file_path: str, file_type: str):
        """Process document in background thread"""
        thread = threading.Thread(
            target=self.process_document,
            args=(document_id, file_path, file_type),
            daemon=True
        )
        thread.start()
        return thread
```

### Step 7: Update Upload Route

**Modify `backend/routes/documents.py`:**

Add after document is saved to database:

```python
# After document is inserted (around line 259)

# Start background processing for OCR and AI
from utils.document_processor import DocumentProcessor

processor = DocumentProcessor()
processor.process_async(
    document_id=doc_id,
    file_path=temp_path,
    file_type=file_extension
)
```

---

## 🔄 User Experience Flow

### Option 1: Auto-Categorize (Recommended)

1. User uploads document
2. User can **optionally** select category (or skip)
3. System processes in background:
   - OCR (if needed)
   - AI suggests category
   - AI generates tags
4. User sees notification: "Category suggested: [Category Name]"
5. User can accept or change category

### Option 2: Suggest Before Save

1. User uploads document
2. System quickly processes (OCR + AI)
3. Shows suggestion: "We suggest: [Category]"
4. User confirms or changes
5. Document saved

**Recommendation:** Option 1 (background processing) - Better UX, non-blocking

---

## 🎨 Frontend Changes Needed

### 1. Update File Upload Component

**Add image file support:**
```typescript
// src/components/UploadModal.tsx
const ACCEPTED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  // Add image types
  'image/jpeg',
  'image/png',
  'image/tiff',
  'image/bmp'
];
```

### 2. Show Processing Status

**Add status indicator:**
```typescript
// Show "Processing..." badge while status === 'processing'
// Show "Category Suggested: X" when suggested_category is available
```

### 3. Category Suggestion UI

**Add suggestion banner:**
```tsx
{suggestedCategory && (
  <Alert>
    <InfoIcon />
    <AlertTitle>Category Suggestion</AlertTitle>
    <AlertDescription>
      We suggest: <strong>{suggestedCategory}</strong>
      <Button onClick={acceptSuggestion}>Accept</Button>
      <Button variant="outline" onClick={dismissSuggestion}>Dismiss</Button>
    </AlertDescription>
  </Alert>
)}
```

---

## 📊 Database Updates

### No Schema Changes Needed! ✅

All required fields already exist:
- `extracted_text` - For OCR output
- `ai_tags` - For generated tags (JSON)
- `suggested_category` - For AI category suggestion
- `status` - Track processing state
- `processing_status` - Track processing step

### Optional: Add Index for Performance

```sql
-- Add index for faster searches on extracted text
ALTER TABLE documents ADD FULLTEXT INDEX idx_extracted_text (extracted_text(500));
```

---

## 🚀 Deployment Checklist

### System Requirements

- [ ] Install Tesseract OCR
  - **Windows:** Download from GitHub, add to PATH
  - **Linux:** `sudo apt-get install tesseract-ocr`
  - **Mac:** `brew install tesseract`

- [ ] Install Poppler (for PDF to image)
  - **Windows:** Download from poppler website
  - **Linux:** `sudo apt-get install poppler-utils`
  - **Mac:** `brew install poppler`

### Environment Variables

Add to `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows only
```

### Testing

1. **Test OCR:**
   - Upload scanned PDF
   - Upload JPG image
   - Verify text extraction

2. **Test Auto-Categorization:**
   - Upload invoice → Should suggest "Financial" or similar
   - Upload contract → Should suggest "Contracts"
   - Verify category suggestion appears

3. **Test Tags:**
   - Upload document
   - Verify tags are generated
   - Check tags are relevant

---

## 💰 Cost Estimates

### OCR (Tesseract - FREE)
- No cost for Tesseract OCR
- Optional: Google Cloud Vision API (~$1.50 per 1000 images)

### AI Categorization (OpenAI)
- GPT-3.5-turbo: ~$0.001 per document
- 1000 documents/month = ~$1/month
- Very cost-effective!

### Total Monthly Cost
- **With Tesseract:** ~$1-10/month (just OpenAI API)
- **With Google Vision:** ~$50-150/month (for high volume)

---

## ⚠️ Considerations & Trade-offs

### OCR Accuracy

**Tesseract (Free):**
- ✅ Free, open-source
- ✅ Good for clean documents
- ❌ Lower accuracy for poor quality scans
- ❌ Slower processing

**Google Cloud Vision (Paid):**
- ✅ Higher accuracy
- ✅ Better for poor quality scans
- ✅ Faster processing
- ❌ Costs money (~$1.50 per 1000 images)

**Recommendation:** Start with Tesseract, upgrade to Google Vision if needed

### Processing Time

- **OCR:** 5-30 seconds per page (Tesseract)
- **AI Analysis:** 2-5 seconds per document
- **Total:** 10-60 seconds per document

**Solution:** Background processing (non-blocking)

### Error Handling

- OCR failures → Continue without extracted text
- AI failures → Use default category
- Always graceful degradation

---

## 🎯 Success Metrics

Track these to measure success:

1. **OCR Success Rate:** % of documents with extracted text
2. **Category Accuracy:** % of suggestions accepted by users
3. **Time Saved:** Reduction in manual categorization time
4. **User Adoption:** % of users using auto-categorization

---

## 📝 Next Steps

1. **Review this plan** - Discuss any changes needed
2. **Set up environment** - Install Tesseract, get OpenAI API key
3. **Implement OCR module** - Start with `ocr_helper.py`
4. **Implement AI modules** - `ai_categorizer.py` and `ai_tagger.py`
5. **Integrate with upload flow** - Add background processing
6. **Update frontend** - Show suggestions and status
7. **Test thoroughly** - Various document types
8. **Deploy** - Roll out to users

---

## ❓ Questions to Discuss

1. **Category Selection:**
   - Should users be required to select category, or can it be optional?
   - Should we auto-apply suggested category if confidence > 90%?

2. **OCR Strategy:**
   - Start with Tesseract (free) or Google Vision (paid)?
   - Process all pages or limit to first N pages?

3. **Processing Priority:**
   - Process immediately or queue for batch processing?
   - Should users wait or get notification when done?

4. **Error Handling:**
   - What happens if OCR fails?
   - What happens if AI API is down?

5. **User Experience:**
   - Show processing progress?
   - Allow users to reject suggestions?
   - Show extracted text preview?

---

*Ready to start implementation? Let's discuss these questions and begin coding!* 🚀




