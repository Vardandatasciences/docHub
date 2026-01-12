"""
AI Categorizer - Use Ollama to suggest document categories
Analyzes document content and suggests the most appropriate category
"""
from typing import Dict, Optional
from database import execute_query
from utils.ollama_helper import OllamaHelper
import json


class AICategorizer:
    """Use AI to categorize documents based on content"""
    
    def __init__(self):
        """Initialize AI categorizer with Ollama"""
        self.ollama = OllamaHelper()
        
        # Check connection
        if not self.ollama.check_connection():
            print("⚠️ Warning: Ollama connection check failed. Will attempt anyway.")
    
    def get_existing_categories(self) -> list:
        """
        Get list of existing categories from database
        
        Returns:
            List of category names
        """
        try:
            categories = execute_query(
                "SELECT id, name, description FROM categories WHERE is_active = TRUE ORDER BY name",
                (),
                fetch_all=True
            )
            return [cat['name'] for cat in categories]
        except Exception as e:
            print(f"⚠️ Error fetching categories: {str(e)}")
            return ['General']  # Fallback
    
    def suggest_category(self, document_text: str, document_name: str = "") -> Dict:
        """
        Suggest category for document based on content using Ollama
        
        Args:
            document_text: Extracted text from document
            document_name: Original filename (for context)
            
        Returns:
            Dict with:
                - suggested_category: Category name
                - confidence: Confidence score (0.0-1.0)
                - reasoning: Brief explanation
        """
        try:
            # Get existing categories
            categories = self.get_existing_categories()
            
            if not categories:
                return {
                    'suggested_category': 'General',
                    'confidence': 0.0,
                    'reasoning': 'No categories available'
                }
            
            categories_str = ", ".join(categories)
            
            # Limit text length for API (keep first 3000 chars to avoid token limits)
            text_preview = document_text[:3000] if len(document_text) > 3000 else document_text
            
            # Create prompt for Ollama
            system_prompt = """You are a document categorization assistant. 
Analyze documents and suggest the most appropriate category from a given list.
Always respond with valid JSON only, no additional text."""

            user_prompt = f"""Analyze this document and suggest the most appropriate category.

Document Name: {document_name}
Document Content Preview:
{text_preview}

Available Categories: {categories_str}

Analyze the document content and determine which category it best fits into.
Consider the document's purpose, content type, and subject matter.

Respond with JSON in this exact format:
{{
    "category_name": "CategoryName",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this category fits"
}}

If the document doesn't clearly fit any category, suggest "General" or the closest match.
Make sure the category_name exactly matches one of the available categories."""

            # Use chat format for better results
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            print(f"🤖 Requesting category suggestion from Ollama...")
            result = self.ollama.chat(
                messages=messages,
                temperature=0.3,
                format="json"
            )
            
            if result["error"]:
                print(f"⚠️ Ollama categorization failed: {result['error']}")
                return {
                    'suggested_category': 'General',
                    'confidence': 0.0,
                    'reasoning': f'Categorization failed: {result["error"]}'
                }
            
            # Parse JSON response
            response_text = result["response"]
            
            # Clean JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                parsed_result = json.loads(response_text)
                
                category_name = parsed_result.get('category_name', 'General')
                confidence = float(parsed_result.get('confidence', 0.5))
                reasoning = parsed_result.get('reasoning', '')
                
                # Validate category exists - try exact match first, then fuzzy match
                valid_categories = self.get_existing_categories()
                
                if category_name not in valid_categories:
                    # Try case-insensitive match
                    category_lower = category_name.lower()
                    matched = None
                    for valid_cat in valid_categories:
                        if valid_cat.lower() == category_lower:
                            matched = valid_cat
                            break
                    
                    if matched:
                        print(f"⚠️ Category '{category_name}' matched to '{matched}' (case-insensitive)")
                        category_name = matched
                    else:
                        # Try partial/fuzzy match (e.g., "Enterprice" -> "Enterprise")
                        for valid_cat in valid_categories:
                            if category_lower in valid_cat.lower() or valid_cat.lower() in category_lower:
                                if len(valid_cat) >= len(category_name) * 0.7:  # At least 70% length match
                                    matched = valid_cat
                                    print(f"⚠️ Category '{category_name}' matched to '{matched}' (fuzzy match)")
                                    break
                        
                        if matched:
                            category_name = matched
                            confidence = max(0.3, confidence * 0.8)  # Reduce confidence for fuzzy match
                        else:
                            print(f"⚠️ Suggested category '{category_name}' not found. Using 'General'")
                            category_name = 'General'
                            confidence = 0.3
                
                print(f"✅ Category suggested: {category_name} (confidence: {confidence:.2f})")
                
                return {
                    'suggested_category': category_name,
                    'confidence': round(confidence, 2),
                    'reasoning': reasoning
                }
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse JSON response: {str(e)}")
                print(f"Response was: {response_text[:200]}")
                return {
                    'suggested_category': 'General',
                    'confidence': 0.0,
                    'reasoning': f'Failed to parse AI response: {str(e)}'
                }
                
        except Exception as e:
            print(f"⚠️ AI categorization error: {str(e)}")
            # Fallback: return default
            return {
                'suggested_category': 'General',
                'confidence': 0.0,
                'reasoning': f'Categorization error: {str(e)}'
            }

