"""
AI Tag Generator - Generate relevant tags from document content using Ollama
Extracts key topics, themes, and entities to create searchable tags
"""
from typing import List
from utils.ollama_helper import OllamaHelper
import json


class AITagger:
    """Generate smart tags from document content"""
    
    def __init__(self):
        """Initialize AI tagger with Ollama"""
        self.ollama = OllamaHelper()
    
    def generate_tags(self, document_text: str, document_name: str = "") -> List[str]:
        """
        Generate relevant tags from document using Ollama
        
        Args:
            document_text: Extracted text from document
            document_name: Filename for context
            
        Returns:
            List of tag strings (3-5 tags)
        """
        try:
            # Limit text for API (keep first 2000 chars)
            text_preview = document_text[:2000] if len(document_text) > 2000 else document_text
            
            system_prompt = """You are a document tagging assistant. 
Analyze documents and extract key topics, themes, document types, and important entities.
Generate concise, relevant tags (single words or short phrases).
Always respond with valid JSON only."""

            user_prompt = f"""Analyze this document and generate 3-5 relevant tags.

Document Name: {document_name}
Content:
{text_preview}

Extract key topics, themes, document type, and important entities.
Generate concise, relevant tags (single words or short phrases, lowercase).

Respond with a JSON array of strings only:
["tag1", "tag2", "tag3"]

Make tags specific and useful for searching. Avoid generic tags like "document" or "file"."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            print(f"🏷️ Requesting tags from Ollama...")
            result = self.ollama.chat(
                messages=messages,
                temperature=0.5,  # Slightly higher for more creative tags
                format="json"
            )
            
            if result["error"]:
                print(f"⚠️ Tag generation failed: {result['error']}")
                return []
            
            # Parse JSON response
            response_text = result["response"]
            
            # Clean JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                tags = json.loads(response_text)
                
                # Handle different response formats
                # Sometimes Ollama returns {'tags': [...]} instead of just [...]
                if isinstance(tags, dict):
                    # Check for common keys
                    if 'tags' in tags:
                        tags = tags['tags']
                    elif 'tag' in tags:
                        tags = tags['tag']
                    else:
                        # Try to extract list from dict values
                        dict_values = list(tags.values())
                        if dict_values and isinstance(dict_values[0], list):
                            tags = dict_values[0]
                        else:
                            tags = []
                
                # Ensure it's a list
                if not isinstance(tags, list):
                    if isinstance(tags, str):
                        # Single tag as string
                        tags = [tags]
                    else:
                        tags = [str(tags)] if tags else []
                
                # Clean and validate tags
                cleaned_tags = []
                for tag in tags[:5]:  # Limit to 5 tags
                    if isinstance(tag, str):
                        # Clean tag: lowercase, remove extra spaces
                        cleaned_tag = tag.strip().lower()
                        if cleaned_tag and len(cleaned_tag) > 1:
                            cleaned_tags.append(cleaned_tag)
                
                print(f"✅ Generated {len(cleaned_tags)} tags: {', '.join(cleaned_tags)}")
                return cleaned_tags
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse tags JSON: {str(e)}")
                print(f"Response was: {response_text[:200]}")
                return []
                
        except Exception as e:
            print(f"⚠️ Tag generation error: {str(e)}")
            return []

