"""
Document Processor - Background processing for OCR and AI analysis
Handles the complete pipeline: OCR → AI Categorization → AI Tagging
"""
import threading
from typing import Dict, Optional
from flask import current_app
from database import execute_query
from utils.ocr_helper import OCRHelper
from utils.ai_categorizer import AICategorizer
from utils.ai_tagger import AITagger
import os
import json


class DocumentProcessor:
    """Process documents in background (OCR + AI)"""
    
    def __init__(self, app: Optional["Flask"] = None):
        """
        Initialize document processor with all helpers
        
        Args:
            app: Flask application instance. If not provided, will use current_app.
        """
        # Capture a real Flask app object so we can push an app context inside threads
        if app is not None:
            self.app = app
        else:
            # current_app is a proxy; get the underlying app instance
            self.app = current_app._get_current_object()
        
        self.ocr_helper = OCRHelper()
        self.ai_categorizer = AICategorizer()
        self.ai_tagger = AITagger()
    
    def process_document(self, document_id: int, file_path: str, file_type: str):
        """
        Process document: OCR + AI analysis
        
        This method runs the complete pipeline:
        1. OCR extraction (if needed)
        2. AI categorization
        3. AI tagging
        4. Update database
        
        NOTE: This method assumes an active Flask application context.
        
        Args:
            document_id: Document ID in database
            file_path: Path to file (temporary file)
            file_type: File extension
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 Starting processing for document ID: {document_id}")
            print(f"{'='*60}")
            
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
            file_type_lower = file_type.lower()
            needs_ocr = file_type_lower in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']
            is_scanned_pdf = False
            
            if file_type_lower == 'pdf':
                is_scanned_pdf = self.ocr_helper.is_scanned_pdf(file_path)
                needs_ocr = is_scanned_pdf
            
            if needs_ocr:
                print(f"📸 Document needs OCR (type: {file_type})")
                try:
                    extracted_text, ocr_metadata = self.ocr_helper.extract_text(file_path, file_type)
                    
                    # Update with OCR results
                    word_count = ocr_metadata.get('word_count', 0)
                    execute_query(
                        """
                        UPDATE documents 
                        SET extracted_text = %s, 
                            processing_status = 'ai_analysis',
                            word_count = %s
                        WHERE id = %s
                        """,
                        (extracted_text, word_count, document_id),
                        commit=True
                    )
                    
                    print(f"✅ OCR completed: {word_count} words extracted")
                    
                except Exception as ocr_error:
                    print(f"⚠️ OCR failed: {str(ocr_error)}")
                    # Continue without extracted text
                    execute_query(
                        "UPDATE documents SET processing_status = 'ai_analysis', error_message = %s WHERE id = %s",
                        (f"OCR failed: {str(ocr_error)}", document_id),
                        commit=True
                    )
            else:
                # For digital PDFs, extract text ourselves if not already extracted
                print(f"📄 Digital document - extracting text from PDF...")
                try:
                    # Try to extract text from digital PDF using PyPDF2/pdfplumber
                    import PyPDF2
                    import pdfplumber
                    
                    # Try pdfplumber first (better quality)
                    try:
                        with pdfplumber.open(file_path) as pdf:
                            text_parts = []
                            total_pages = len(pdf.pages)
                            # Limit to first 20 pages for performance
                            pages_to_extract = min(20, total_pages)
                            
                            for i in range(pages_to_extract):
                                page = pdf.pages[i]
                                page_text = page.extract_text()
                                if page_text:
                                    text_parts.append(page_text)
                            
                            extracted_text = "\n\n".join(text_parts)
                            word_count = len(extracted_text.split())
                            
                            print(f"✅ Extracted {word_count} words from {pages_to_extract} pages (pdfplumber)")
                            
                    except Exception as plumber_error:
                        # Fallback to PyPDF2
                        print(f"⚠️ pdfplumber failed, trying PyPDF2: {str(plumber_error)}")
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            total_pages = len(pdf_reader.pages)
                            pages_to_extract = min(20, total_pages)
                            
                            text_parts = []
                            for i in range(pages_to_extract):
                                try:
                                    page = pdf_reader.pages[i]
                                    page_text = page.extract_text()
                                    if page_text:
                                        text_parts.append(page_text)
                                except:
                                    continue
                            
                            extracted_text = "\n\n".join(text_parts)
                            word_count = len(extracted_text.split())
                            
                            print(f"✅ Extracted {word_count} words from {pages_to_extract} pages (PyPDF2)")
                    
                    # Update database with extracted text
                    if extracted_text:
                        execute_query(
                            """
                            UPDATE documents 
                            SET extracted_text = %s, 
                                processing_status = 'ai_analysis',
                                word_count = %s
                            WHERE id = %s
                            """,
                            (extracted_text, word_count, document_id),
                            commit=True
                        )
                    else:
                        print(f"⚠️ No text extracted from PDF")
                        execute_query(
                            "UPDATE documents SET processing_status = 'ai_analysis' WHERE id = %s",
                            (document_id,),
                            commit=True
                        )
                        
                except Exception as pdf_error:
                    print(f"⚠️ PDF text extraction failed: {str(pdf_error)}")
                    # Continue without extracted text
                    execute_query(
                        "UPDATE documents SET processing_status = 'ai_analysis', error_message = %s WHERE id = %s",
                        (f"PDF extraction failed: {str(pdf_error)}", document_id),
                        commit=True
                    )
            
            # Step 2: AI Analysis (if we have text or can get it)
            print(f"🤖 Starting AI analysis...")
            
            # Get document name for context
            doc = execute_query(
                "SELECT name, original_name, extracted_text FROM documents WHERE id = %s",
                (document_id,),
                fetch_one=True
            )
            
            if not doc:
                print(f"❌ Document {document_id} not found in database")
                return
            
            doc_name = doc['name'] if doc else ""
            
            # Get text for AI (use extracted_text if available from OCR/PDF extraction, otherwise from DB)
            if not extracted_text:
                extracted_text = doc.get('extracted_text', '') or ''
            
            if extracted_text and len(extracted_text.strip()) > 50:
                # We have text to analyze
                print(f"📝 Analyzing {len(extracted_text)} characters of text...")
                
                try:
                    # Generate category suggestion
                    print(f"  → Generating category suggestion...")
                    category_result = self.ai_categorizer.suggest_category(extracted_text, doc_name)
                    
                    # Generate tags
                    print(f"  → Generating tags...")
                    tags = self.ai_tagger.generate_tags(extracted_text, doc_name)
                    
                    # Update database with AI results
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
                            json.dumps(tags) if tags else None,
                            document_id
                        ),
                        commit=True
                    )
                    
                    print(f"\n✅ Document {document_id} processed successfully!")
                    print(f"   📁 Suggested Category: {category_result['suggested_category']} (confidence: {category_result['confidence']:.2f})")
                    print(f"   🏷️  Tags: {', '.join(tags) if tags else 'None'}")
                    print(f"{'='*60}\n")
                    
                except Exception as ai_error:
                    print(f"⚠️ AI analysis failed: {str(ai_error)}")
                    # Update status but don't fail completely
                    execute_query(
                        """
                        UPDATE documents 
                        SET processing_status = 'completed',
                            status = 'ready',
                            error_message = %s
                        WHERE id = %s
                        """,
                        (f"AI analysis failed: {str(ai_error)}", document_id),
                        commit=True
                    )
            else:
                # No text to analyze (or too short)
                print(f"⚠️ No sufficient text for AI analysis ({len(extracted_text)} chars)")
                execute_query(
                    "UPDATE documents SET status = 'ready', processing_status = 'completed' WHERE id = %s",
                    (document_id,),
                    commit=True
                )
                
        except Exception as e:
            print(f"\n❌ Error processing document {document_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Update status to failed
            try:
                execute_query(
                    "UPDATE documents SET status = 'failed', error_message = %s WHERE id = %s",
                    (str(e)[:500], document_id),  # Limit error message length
                    commit=True
                )
            except:
                pass  # If we can't update, at least log the error
    
    def process_async(self, document_id: int, file_path: str, file_type: str):
        """
        Process document in background thread
        
        Args:
            document_id: Document ID in database
            file_path: Path to file (will be deleted after processing)
            file_type: File extension
            
        Returns:
            Thread object
        """
        def process_and_cleanup():
            # Ensure all DB and config access happens inside an application context
            with self.app.app_context():
                try:
                    self.process_document(document_id, file_path, file_type)
                finally:
                    # Clean up temporary file if it exists
                    if os.path.exists(file_path):
                        try:
                            os.unlink(file_path)
                            print(f"🧹 Cleaned up temporary file: {file_path}")
                        except Exception:
                            pass
        
        thread = threading.Thread(
            target=process_and_cleanup,
            daemon=True
        )
        thread.start()
        print(f"🔄 Started background processing thread for document {document_id}")
        return thread

