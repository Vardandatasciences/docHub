"""
AI Chatbot - Document Assistant using Ollama
Handles RAG (Retrieval Augmented Generation) for document Q&A
Uses smart model selection based on query complexity
"""
from typing import Dict, Optional, List
from database import execute_query
from utils.ollama_helper import OllamaHelper
from utils.model_selector import ModelSelector
from flask import current_app
import json


class AIChatbot:
    """AI Chatbot for document Q&A using Ollama"""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize AI chatbot with Ollama
        
        Args:
            model: Specific model to use (if None, will use smart selection)
        """
        self.ollama = OllamaHelper(model=model)
        self.use_smart_selection = True
        
        # Check if smart model selection is enabled
        try:
            self.use_smart_selection = current_app.config.get('USE_SMART_MODEL_SELECTION', True)
        except RuntimeError:
            # Outside Flask context
            import os
            self.use_smart_selection = os.environ.get('USE_SMART_MODEL_SELECTION', 'true').lower() == 'true'
        
        # Check connection
        if not self.ollama.check_connection():
            print("⚠️ Warning: Ollama connection check failed. Will attempt anyway.")
    
    def get_document_context(self, document_id: int, max_chars: int = 4000) -> Dict:
        """
        Retrieve document text for context
        
        Args:
            document_id: Document ID to retrieve
            max_chars: Maximum characters to retrieve (for context window)
            
        Returns:
            Dict with document info and text
        """
        try:
            document = execute_query(
                """
                SELECT id, name, extracted_text, summary
                FROM documents
                WHERE id = %s
                """,
                (document_id,),
                fetch_one=True
            )
            
            if not document:
                return {'error': 'Document not found'}
            
            # Use extracted_text, fallback to summary, fallback to empty
            text = document.get('extracted_text') or document.get('summary') or ''
            
            # Check if we actually have text content
            if not text or not text.strip():
                print(f"⚠️ Document {document_id} has no extracted text or summary")
                return {
                    'error': 'Document has no extractable text content. Please ensure the document has been processed and has extracted_text or summary.',
                    'document_id': document['id'],
                    'document_name': document['name'],
                    'text': '',
                    'text_length': 0
                }
            
            # Truncate if too long (keep first max_chars chars)
            if len(text) > max_chars:
                text = text[:max_chars] + "...\n[Text truncated due to length]"
            
            print(f"✅ Retrieved document context: {document['name']} ({len(text)} chars)")
            
            return {
                'document_id': document['id'],
                'document_name': document['name'],
                'text': text,
                'text_length': len(text)
            }
        except Exception as e:
            print(f"⚠️ Error fetching document context: {str(e)}")
            return {'error': f'Failed to fetch document: {str(e)}'}
    
    def search_user_documents(self, query: str, user_id: int, limit: int = 3) -> List[Dict]:
        """
        Search across user's documents for relevant context
        (Simplified search - can be enhanced with embeddings later)
        
        Args:
            query: Search query
            user_id: User ID
            limit: Maximum documents to return
            
        Returns:
            List of document dicts
        """
        try:
            # Simple keyword search in extracted_text and summary
            search_term = f"%{query}%"
            documents = execute_query(
                """
                SELECT id, name, extracted_text, summary
                FROM documents
                WHERE uploaded_by = %s
                AND (extracted_text LIKE %s OR summary LIKE %s OR name LIKE %s)
                AND extracted_text IS NOT NULL
                AND extracted_text != ''
                LIMIT %s
                """,
                (user_id, search_term, search_term, search_term, limit),
                fetch_all=True
            )
            
            results = []
            for doc in documents:
                text = doc.get('extracted_text') or doc.get('summary') or ''
                # Limit each document text to 1500 chars for multi-doc context
                if len(text) > 1500:
                    text = text[:1500] + "..."
                results.append({
                    'document_id': doc['id'],
                    'document_name': doc['name'],
                    'text': text
                })
            
            return results
        except Exception as e:
            print(f"⚠️ Error searching documents: {str(e)}")
            return []
    
    def generate_response(
        self, 
        question: str, 
        document_context: Optional[Dict] = None,
        chat_history: Optional[List[Dict]] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Generate AI response using RAG
        
        Args:
            question: User's question
            document_context: Single document context (if querying specific document)
            chat_history: Previous messages in conversation (for context)
            user_id: User ID (for multi-document search if no document_context)
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Build context
            context_text = ""
            sources = []
            
            if document_context:
                # Single document query
                if 'error' in document_context:
                    error_msg = document_context['error']
                    print(f"⚠️ Document context error: {error_msg}")
                    
                    # If it's an empty text error, still try to answer but inform user
                    if 'no extractable text' in error_msg.lower() or 'no extracted text' in error_msg.lower():
                        return {
                            'response': f"I see you've selected the document '{document_context.get('document_name', 'this document')}', but it doesn't have any extractable text content yet. The document may still be processing, or it might be a scanned image that needs OCR. Please try:\n\n1. Wait a moment if the document is still processing\n2. Check if OCR processing is needed for this document\n3. Or select a different document that has been fully processed.",
                            'sources': [{
                                'document_id': document_context.get('document_id'),
                                'document_name': document_context.get('document_name', 'Unknown')
                            }],
                            'error': error_msg
                        }
                    
                    return {
                        'response': f"I encountered an issue with the selected document: {error_msg}. Please try selecting a different document or contact support if the problem persists.",
                        'sources': [],
                        'error': error_msg
                    }
                
                # Check if document has actual text content
                if not document_context.get('text') or not document_context['text'].strip():
                    print(f"⚠️ Document {document_context.get('document_id')} has empty text")
                    return {
                        'response': f"The document '{document_context.get('document_name', 'selected document')}' doesn't have any text content available yet. It may still be processing, or it might need OCR extraction. Please wait a moment and try again, or select a different document.",
                        'sources': [{
                            'document_id': document_context['document_id'],
                            'document_name': document_context['document_name']
                        }],
                        'error': 'Empty document text'
                    }
                
                context_text = f"""
Document: {document_context['document_name']}
Document ID: {document_context['document_id']}

Document Content:
{document_context['text']}
"""
                sources.append({
                    'document_id': document_context['document_id'],
                    'document_name': document_context['document_name']
                })
                
                print(f"✅ Using document context from: {document_context['document_name']}")
            elif user_id:
                # Multi-document search (search across user's documents)
                relevant_docs = self.search_user_documents(question, user_id, limit=3)
                if relevant_docs:
                    context_text = "Relevant Documents:\n\n"
                    for doc in relevant_docs:
                        context_text += f"Document: {doc['document_name']} (ID: {doc['document_id']})\n"
                        context_text += f"Content: {doc['text']}\n\n"
                        sources.append({
                            'document_id': doc['document_id'],
                            'document_name': doc['document_name']
                        })
                else:
                    # No relevant documents found - still answer the question as a general assistant
                    context_text = "Note: No relevant documents were found in your library matching this query."
            else:
                # No user_id provided - general query without document search
                context_text = "Note: This is a general question not tied to any specific document."
            
            # Build chat history context (last 3 exchanges)
            history_context = ""
            if chat_history:
                recent_history = chat_history[-6:]  # Last 3 exchanges (6 messages)
                history_context = "\n\nPrevious conversation:\n"
                for msg in recent_history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    history_context += f"{role.capitalize()}: {content}\n"
            
            # Determine if we have document context
            has_document_context = bool(document_context and 'error' not in document_context) or bool(sources)
            
            # Create system prompt - adapt based on whether we have document context
            if has_document_context:
                # We have document context
                system_prompt = """You are a helpful document assistant. Your job is to answer questions about documents accurately and concisely.

Guidelines:
- Answer based on the provided document content when available
- If the answer is not in the documents, say so clearly
- Be concise but comprehensive
- Cite document names when referencing multiple documents
- Use clear, professional language"""
                
                # Create user prompt with document context
                user_prompt = f"""{context_text}{history_context}

User Question: {question}

Please provide a clear, accurate answer based on the document content above. If the information is not available in the documents, please state that clearly."""
            else:
                # No document context - act as general assistant
                system_prompt = """You are a helpful AI assistant. Answer the user's question clearly and concisely.

Guidelines:
- Be helpful, accurate, and concise
- If you don't know something, say so
- Use clear, professional language
- If the question is about documents, you can suggest that the user select a specific document from their library or rephrase their question"""
                
                # Create user prompt for general question
                user_prompt = f"""{context_text}{history_context}

User Question: {question}

Please provide a helpful answer to the user's question."""
            
            # Call Ollama
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Smart model selection based on query complexity
            model_config = None
            if self.use_smart_selection:
                context_length = len(context_text) if context_text else 0
                has_multiple_docs = len(sources) > 1
                
                # Get base URL for availability check
                base_url = None
                try:
                    base_url = current_app.config.get('OLLAMA_BASE_URL')
                except RuntimeError:
                    import os
                    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
                
                # Select model with availability check
                model_config = ModelSelector.select_model_with_availability_check(
                    question=question,
                    document_context_length=context_length,
                    has_multiple_documents=has_multiple_docs,
                    base_url=base_url
                )
                
                # Update Ollama helper with selected model
                if model_config['model'] != self.ollama.model:
                    print(f"🔄 Switching model: {self.ollama.model} → {model_config['model']} ({model_config['tier']} tier)")
                    self.ollama.set_model(model_config['model'])
                
                temperature = model_config['temperature']
                print(f"🤖 Using {model_config['tier']} tier model: {model_config['model']}")
            else:
                temperature = 0.3
                print(f"🤖 Using default model: {self.ollama.model}")
            
            print(f"📝 Question: {question[:100]}...")
            print(f"📄 Has document context: {has_document_context}")
            print(f"🔗 Sources count: {len(sources)}")
            print(f"🌡️ Temperature: {temperature}")
            
            result = self.ollama.chat(
                messages=messages,
                temperature=temperature,
                format=None
            )
            
            if result["error"]:
                print(f"⚠️ Ollama chatbot request failed: {result['error']}")
                return {
                    'response': f"I apologize, but I'm having trouble processing your request. Please try again. Error: {result['error']}",
                    'sources': sources,
                    'error': result['error']
                }
            
            response_text = result.get("response", "").strip()
            
            if not response_text:
                print(f"⚠️ Empty response from Ollama")
                return {
                    'response': "I apologize, but I didn't receive a response. Please try asking your question again, or check if Ollama is running properly.",
                    'sources': sources,
                    'error': 'Empty response from Ollama'
                }
            
            print(f"✅ Received chatbot response ({len(response_text)} chars)")
            print(f"📤 Response preview: {response_text[:100]}...")
            
            return {
                'response': response_text,
                'sources': sources,
                'error': None
            }
            
        except Exception as e:
            print(f"⚠️ AI chatbot error: {str(e)}")
            return {
                'response': f"I encountered an error while processing your question. Please try again.",
                'sources': [],
                'error': str(e)
            }

