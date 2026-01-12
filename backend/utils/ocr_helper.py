"""
OCR Helper - Extract text from images and scanned documents
Uses Tesseract OCR for text extraction from images and scanned PDFs
"""
import pytesseract
from PIL import Image
import pdf2image
import os
from typing import Tuple, Optional, Dict
import PyPDF2


class OCRHelper:
    """Handle OCR operations for images and scanned documents"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR helper
        
        Args:
            tesseract_cmd: Path to tesseract executable (if not in PATH)
                           On Windows, might be: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        # Try to get from environment variable
        elif os.environ.get('TESSERACT_CMD'):
            pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD')
    
    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Check if PDF is scanned (image-based) or text-based
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned (image-based)
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                # Check first few pages for text
                pages_to_check = min(3, len(pdf_reader.pages))
                total_text_length = 0
                
                for i in range(pages_to_check):
                    try:
                        page_text = pdf_reader.pages[i].extract_text()
                        total_text_length += len(page_text.strip())
                    except:
                        pass
                
                # If very little text across first few pages, likely scanned
                # Threshold: less than 100 characters per page on average
                avg_text_per_page = total_text_length / pages_to_check if pages_to_check > 0 else 0
                return avg_text_per_page < 100
                
        except Exception as e:
            print(f"⚠️ Error checking if PDF is scanned: {str(e)}")
            # If we can't determine, assume it might be scanned
            return True
    
    def extract_from_image(self, image_path: str) -> Tuple[str, Dict]:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file (JPG, PNG, TIFF, BMP)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            print(f"🔍 Extracting text from image: {image_path}")
            image = Image.open(image_path)
            
            # OCR with detailed output
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Get OCR metadata for confidence scoring
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence (exclude -1 values)
            # Handle both string and int values from OCR
            confidences = []
            for conf in data['conf']:
                if conf == -1 or conf == '-1':
                    continue
                try:
                    # Convert to int if string, or use directly if int
                    conf_int = int(conf) if isinstance(conf, str) else conf
                    confidences.append(conf_int)
                except (ValueError, TypeError):
                    continue
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count words (handle both string and None values)
            words = [w for w in data['text'] if w and (isinstance(w, str) and w.strip())]
            word_count = len(words)
            
            metadata = {
                'confidence': round(avg_confidence, 2),
                'word_count': word_count,
                'page_count': 1,
                'method': 'tesseract_ocr'
            }
            
            print(f"✅ Extracted {word_count} words with {avg_confidence:.1f}% confidence")
            return text.strip(), metadata
            
        except Exception as e:
            print(f"❌ OCR extraction failed: {str(e)}")
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def extract_from_pdf(self, pdf_path: str, max_pages: int = 10) -> Tuple[str, Dict]:
        """
        Extract text from scanned PDF using OCR
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (for performance)
                      Set to None to process all pages
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            print(f"🔍 Extracting text from scanned PDF: {pdf_path}")
            
            # Convert PDF pages to images
            # First, determine how many pages to process
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                total_pages = len(pdf_reader.pages)
            
            # Limit pages for performance
            pages_to_process = min(max_pages, total_pages) if max_pages else total_pages
            
            print(f"📄 Processing {pages_to_process} of {total_pages} pages...")
            
            # Convert PDF to images
            images = pdf2image.convert_from_path(
                pdf_path, 
                first_page=1, 
                last_page=pages_to_process
            )
            
            full_text = ""
            total_confidence = 0
            word_count = 0
            pages_processed = 0
            
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                    
                    # Get confidence for this page
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    # Handle both string and int values from OCR
                    page_confidences = []
                    for c in data['conf']:
                        if c == -1 or c == '-1':
                            continue
                        try:
                            # Convert to int if string, or use directly if int
                            conf_int = int(c) if isinstance(c, str) else c
                            page_confidences.append(conf_int)
                        except (ValueError, TypeError):
                            continue
                    
                    if page_confidences:
                        page_avg_confidence = sum(page_confidences) / len(page_confidences)
                        total_confidence += page_avg_confidence
                    
                    # Handle both string and None values
                    page_words = [w for w in data['text'] if w and (isinstance(w, str) and w.strip())]
                    word_count += len(page_words)
                    pages_processed += 1
                    
                    print(f"  ✓ Processed page {i+1}/{pages_to_process}")
                    
                except Exception as page_error:
                    print(f"  ⚠️ Error processing page {i+1}: {str(page_error)}")
                    continue
            
            metadata = {
                'confidence': round(total_confidence / pages_processed, 2) if pages_processed > 0 else 0,
                'word_count': word_count,
                'page_count': pages_processed,
                'total_pages': total_pages,
                'pages_processed': pages_processed,
                'method': 'tesseract_ocr_pdf'
            }
            
            print(f"✅ Extracted {word_count} words from {pages_processed} pages")
            return full_text.strip(), metadata
            
        except Exception as e:
            print(f"❌ PDF OCR extraction failed: {str(e)}")
            raise Exception(f"PDF OCR extraction failed: {str(e)}")
    
    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, Dict]:
        """
        Main method to extract text from any supported file
        
        Args:
            file_path: Path to file
            file_type: File extension (pdf, jpg, png, etc.)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        file_type_lower = file_type.lower()
        
        # Image files - always use OCR
        if file_type_lower in ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']:
            return self.extract_from_image(file_path)
        
        # PDF files - check if scanned first
        elif file_type_lower == 'pdf':
            if self.is_scanned_pdf(file_path):
                print("📸 Detected scanned PDF - using OCR")
                return self.extract_from_pdf(file_path)
            else:
                print("📄 Detected digital PDF - text extraction handled elsewhere")
                # Digital PDFs are handled by existing PDF extraction in s3.py
                return "", {
                    'note': 'Digital PDF - use existing text extraction',
                    'method': 'digital_pdf'
                }
        
        else:
            raise ValueError(f"Unsupported file type for OCR: {file_type}")

