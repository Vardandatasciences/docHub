"""
Chat Routes - AI Document Assistant Chatbot
Handles chat sessions and messages
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import execute_query, get_cursor
from utils.ai_chatbot import AIChatbot
import json
from datetime import datetime
import time

chat_bp = Blueprint('chat', __name__)


def get_user_id():
    """Helper to get current user ID from JWT"""
    identity = get_jwt_identity()
    # Identity can be a dict with 'id' and 'email' or just an int
    if isinstance(identity, dict):
        return identity['id']
    return identity


def validate_document_access(document_id: int, user_id: int) -> bool:
    """Check if user has access to document"""
    try:
        doc = execute_query(
            "SELECT id FROM documents WHERE id = %s AND uploaded_by = %s",
            (document_id, user_id),
            fetch_one=True
        )
        return doc is not None
    except Exception:
        return False


@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new chat session"""
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        
        document_id = data.get('document_id')
        session_name = data.get('session_name')
        
        # Validate document access if document_id provided
        if document_id:
            if not validate_document_access(document_id, user_id):
                return jsonify({'error': 'Document not found or access denied'}), 404
        
        # Auto-generate session name if not provided
        if not session_name:
            if document_id:
                doc = execute_query(
                    "SELECT name FROM documents WHERE id = %s",
                    (document_id,),
                    fetch_one=True
                )
                if doc:
                    session_name = f"Chat: {doc['name']}"
                else:
                    session_name = "New Chat Session"
            else:
                session_name = "New Chat Session"
        
        # Create session
        session_id = execute_query(
            """
            INSERT INTO chat_sessions (user_id, document_id, session_name)
            VALUES (%s, %s, %s)
            """,
            (user_id, document_id, session_name),
            commit=True
        )
        
        # Get created session
        session = execute_query(
            """
            SELECT id, user_id, document_id, session_name, created_at, updated_at
            FROM chat_sessions
            WHERE id = %s
            """,
            (session_id,),
            fetch_one=True
        )
        
        return jsonify({
            'message': 'Session created successfully',
            'session': {
                'id': session['id'],
                'userId': session['user_id'],
                'documentId': session['document_id'],
                'sessionName': session['session_name'],
                'createdAt': session['created_at'].isoformat() if session['created_at'] else None,
                'updatedAt': session['updated_at'].isoformat() if session['updated_at'] else None
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating session: {str(e)}")
        return jsonify({'error': 'Failed to create session', 'details': str(e)}), 500


@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all chat sessions for current user"""
    try:
        user_id = get_user_id()
        
        # Get sessions with last message preview
        sessions = execute_query(
            """
            SELECT 
                s.id,
                s.user_id,
                s.document_id,
                s.session_name,
                s.created_at,
                s.updated_at,
                d.name as document_name,
                (SELECT content FROM chat_messages 
                 WHERE session_id = s.id 
                 ORDER BY created_at DESC 
                 LIMIT 1) as last_message
            FROM chat_sessions s
            LEFT JOIN documents d ON s.document_id = d.id
            WHERE s.user_id = %s
            ORDER BY s.updated_at DESC
            """,
            (user_id,),
            fetch_all=True
        )
        
        result = []
        for session in sessions:
            result.append({
                'id': session['id'],
                'userId': session['user_id'],
                'documentId': session['document_id'],
                'documentName': session.get('document_name'),
                'sessionName': session['session_name'],
                'lastMessage': session.get('last_message', '')[:100] if session.get('last_message') else '',
                'createdAt': session['created_at'].isoformat() if session['created_at'] else None,
                'updatedAt': session['updated_at'].isoformat() if session['updated_at'] else None
            })
        
        return jsonify({
            'sessions': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch sessions', 'details': str(e)}), 500


@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get a specific chat session with all messages"""
    try:
        user_id = get_user_id()
        
        # Verify session belongs to user
        session = execute_query(
            """
            SELECT id, user_id, document_id, session_name, created_at, updated_at
            FROM chat_sessions
            WHERE id = %s AND user_id = %s
            """,
            (session_id, user_id),
            fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Get all messages for this session
        messages = execute_query(
            """
            SELECT id, session_id, role, content, metadata, created_at
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at ASC
            """,
            (session_id,),
            fetch_all=True
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            metadata = None
            if msg.get('metadata'):
                try:
                    metadata = json.loads(msg['metadata']) if isinstance(msg['metadata'], str) else msg['metadata']
                except:
                    metadata = msg.get('metadata')
            
            formatted_messages.append({
                'id': msg['id'],
                'sessionId': msg['session_id'],
                'role': msg['role'],
                'content': msg['content'],
                'metadata': metadata,
                'createdAt': msg['created_at'].isoformat() if msg['created_at'] else None
            })
        
        return jsonify({
            'session': {
                'id': session['id'],
                'userId': session['user_id'],
                'documentId': session['document_id'],
                'sessionName': session['session_name'],
                'createdAt': session['created_at'].isoformat() if session['created_at'] else None,
                'updatedAt': session['updated_at'].isoformat() if session['updated_at'] else None,
                'messages': formatted_messages
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching session: {str(e)}")
        return jsonify({'error': 'Failed to fetch session', 'details': str(e)}), 500


@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """Delete a chat session and all its messages"""
    try:
        user_id = get_user_id()
        
        # Verify session belongs to user
        session = execute_query(
            "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s",
            (session_id, user_id),
            fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Delete session (cascade will delete messages)
        execute_query(
            "DELETE FROM chat_sessions WHERE id = %s",
            (session_id,),
            commit=True
        )
        
        return jsonify({'message': 'Session deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting session: {str(e)}")
        return jsonify({'error': 'Failed to delete session', 'details': str(e)}), 500


@chat_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    """Update session name"""
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        session_name = data.get('session_name')
        
        if not session_name:
            return jsonify({'error': 'session_name is required'}), 400
        
        # Verify session belongs to user
        session = execute_query(
            "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s",
            (session_id, user_id),
            fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Update session name
        execute_query(
            "UPDATE chat_sessions SET session_name = %s WHERE id = %s",
            (session_name, session_id),
            commit=True
        )
        
        return jsonify({'message': 'Session updated successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error updating session: {str(e)}")
        return jsonify({'error': 'Failed to update session', 'details': str(e)}), 500


@chat_bp.route('/sessions/<int:session_id>/messages/stream', methods=['POST'])
@jwt_required()
def send_message_stream(session_id):
    """Send a message and stream AI response in real-time"""
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        
        message_content = data.get('message', '').strip()
        # Accept both camelCase (from frontend) and snake_case
        document_id = data.get('document_id') or data.get('documentId')
        
        if not message_content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Debug logging
        print(f"📥 Received request - document_id: {document_id}, message: {message_content[:50]}...")
        
        # Verify session belongs to user
        session = execute_query(
            """
            SELECT id, user_id, document_id
            FROM chat_sessions
            WHERE id = %s AND user_id = %s
            """,
            (session_id, user_id),
            fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Use provided document_id or session's document_id
        target_document_id = document_id if document_id is not None else session['document_id']
        
        # Debug logging
        print(f"🔍 Document ID - from request: {document_id}, from session: {session['document_id']}, final: {target_document_id}")
        
        # Validate document access if document_id provided
        if target_document_id:
            if not validate_document_access(target_document_id, user_id):
                return jsonify({'error': 'Document not found or access denied'}), 404
        
        # Initialize chatbot
        chatbot = AIChatbot()
        
        # Get document context if document specified
        document_context = None
        if target_document_id:
            print(f"🔍 Fetching context for document ID: {target_document_id}")
            document_context = chatbot.get_document_context(target_document_id, max_chars=4000)
            if document_context and 'error' in document_context:
                print(f"⚠️ Document context error: {document_context['error']}")
            elif document_context:
                print(f"✅ Document context retrieved: {document_context.get('document_name')} ({document_context.get('text_length', 0)} chars)")
        else:
            print(f"ℹ️ No document specified - will search across user's documents")
        
        # Get chat history for context
        previous_messages = execute_query(
            """
            SELECT role, content
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at ASC
            """,
            (session_id,),
            fetch_all=True
        )

        chat_history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in previous_messages
        ]

        # Save user message
        user_message_id = execute_query(
            """
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (%s, 'user', %s)
            """,
            (session_id, message_content),
            commit=True
        )

        # Prepare streaming response
        def generate_stream():
            try:
                # Check if document was selected but has error (no extracted text)
                if target_document_id and document_context and 'error' in document_context:
                    error_msg = document_context['error']
                    document_name = document_context.get('document_name', 'the selected document')
                    
                    # Generate helpful error message
                    if 'no extractable text' in error_msg.lower() or 'no extracted text' in error_msg.lower():
                        response_text = f"I see you've selected the document '{document_name}', but it doesn't have any extractable text content yet. This could mean:\n\n1. The document is still being processed\n2. The document is a scanned image that needs OCR processing\n3. The document may be empty or corrupted\n\nPlease try:\n- Wait a moment if the document is still processing\n- Check if OCR processing is needed for this document\n- Or select a different document that has been fully processed"
                    else:
                        response_text = f"I encountered an issue with the selected document '{document_name}': {error_msg}\n\nPlease try selecting a different document or contact support if the problem persists."
                    
                    # Save assistant error message
                    metadata = {'error': error_msg, 'sources': []}
                    assistant_message_id = execute_query(
                        """
                        INSERT INTO chat_messages (session_id, role, content, metadata)
                        VALUES (%s, 'assistant', %s, %s)
                        """,
                        (session_id, response_text, json.dumps(metadata)),
                        commit=True
                    )
                    
                    # Update session
                    execute_query(
                        "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s",
                        (session_id,),
                        commit=True
                    )
                    
                    # Send error response as stream
                    yield f"data: {json.dumps({'type': 'start', 'userMessageId': user_message_id, 'sources': []})}\n\n"
                    # Stream the error message character by character for consistency
                    for char in response_text:
                        yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"
                    yield f"data: {json.dumps({'type': 'done', 'assistantMessageId': assistant_message_id, 'fullResponse': response_text, 'sources': []})}\n\n"
                    return
                
                # Prepare context for AI
                context_text = ""
                sources = []
                
                if document_context and 'error' not in document_context:
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
                elif user_id and not target_document_id:
                    relevant_docs = chatbot.search_user_documents(message_content, user_id, limit=2)
                    if relevant_docs:
                        context_text = "Relevant Documents:\n\n"
                        for doc in relevant_docs:
                            context_text += f"Document: {doc['document_name']}\nContent: {doc['text']}\n\n"
                            sources.append({
                                'document_id': doc['document_id'],
                                'document_name': doc['document_name']
                            })
                
                # Build system prompt
                has_document_context = bool(context_text)
                if has_document_context:
                    system_prompt = """You are a helpful document assistant. Answer questions about documents accurately and concisely."""
                else:
                    system_prompt = """You are a helpful AI assistant. Answer questions clearly and concisely."""
                
                # Build user prompt
                history_context = ""
                if chat_history:
                    recent_history = chat_history[-6:]
                    history_context = "\n\nPrevious conversation:\n"
                    for msg in recent_history:
                        history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
                user_prompt = f"""{context_text}{history_context}

User Question: {message_content}

Please provide a clear, accurate answer."""
                
                # Select model (smart selection)
                if chatbot.use_smart_selection:
                    context_length = len(context_text) if context_text else 0
                    has_multiple_docs = len(sources) > 1
                    
                    from utils.model_selector import ModelSelector
                    from flask import current_app
                    import os
                    
                    base_url = None
                    try:
                        base_url = current_app.config.get('OLLAMA_BASE_URL')
                    except RuntimeError:
                        base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
                    
                    model_config = ModelSelector.select_model_with_availability_check(
                        question=message_content,
                        document_context_length=context_length,
                        has_multiple_documents=has_multiple_docs,
                        base_url=base_url
                    )
                    
                    if model_config['model'] != chatbot.ollama.model:
                        chatbot.ollama.set_model(model_config['model'])
                    
                    temperature = model_config['temperature']
                else:
                    temperature = 0.3
                
                # Stream response
                full_response = ""
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                # Send initial metadata
                yield f"data: {json.dumps({'type': 'start', 'userMessageId': user_message_id, 'sources': sources})}\n\n"
                
                # Stream from Ollama
                for chunk in chatbot.ollama.chat_stream(messages, temperature=temperature):
                    if chunk.get('error'):
                        yield f"data: {json.dumps({'type': 'error', 'error': chunk['error']})}\n\n"
                        break
                    
                    content = chunk.get('content', '')
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
                    
                    if chunk.get('done'):
                        # Save assistant message
                        metadata = {'sources': sources}
                        assistant_message_id = execute_query(
                            """
                            INSERT INTO chat_messages (session_id, role, content, metadata)
                            VALUES (%s, 'assistant', %s, %s)
                            """,
                            (session_id, full_response, json.dumps(metadata)),
                            commit=True
                        )
                        
                        # Update session
                        execute_query(
                            "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s",
                            (session_id,),
                            commit=True
                        )
                        
                        # Send final message
                        yield f"data: {json.dumps({'type': 'done', 'assistantMessageId': assistant_message_id, 'fullResponse': full_response, 'sources': sources})}\n\n"
                        break
                
            except Exception as e:
                print(f"❌ Streaming error: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        print(f"❌ Error in streaming: {str(e)}")
        return jsonify({'error': 'Failed to stream message', 'details': str(e)}), 500


@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    """Send a message and get AI response"""
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        
        message_content = data.get('message', '').strip()
        # Accept both camelCase (from frontend) and snake_case
        document_id = data.get('document_id') or data.get('documentId')
        stream = data.get('stream', False)  # Check if streaming requested
        
        if not message_content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Debug logging
        print(f"📥 Received request - document_id: {document_id}, message: {message_content[:50]}...")
        
        # If streaming is requested, redirect to streaming endpoint
        if stream:
            # Note: We can't redirect POST, so we'll handle it in the same function
            # But for cleaner code, we'll check here and call streaming logic
            pass  # Will implement streaming in same endpoint with conditional
        
        # Verify session belongs to user
        session = execute_query(
            """
            SELECT id, user_id, document_id
            FROM chat_sessions
            WHERE id = %s AND user_id = %s
            """,
            (session_id, user_id),
            fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Use provided document_id (from request) first, then fall back to session's document_id
        # This allows users to change document selection without recreating the session
        target_document_id = document_id if document_id is not None else session['document_id']
        
        # Debug logging
        print(f"🔍 Document ID - from request: {document_id}, from session: {session['document_id']}, final: {target_document_id}")
        
        # Validate document access if document_id provided
        if target_document_id:
            if not validate_document_access(target_document_id, user_id):
                return jsonify({'error': 'Document not found or access denied'}), 404
        
        # Initialize chatbot
        chatbot = AIChatbot()
        
        # Get document context if document specified
        document_context = None
        if target_document_id:
            print(f"🔍 Fetching context for document ID: {target_document_id}")
            document_context = chatbot.get_document_context(target_document_id, max_chars=4000)
            if document_context and 'error' in document_context:
                print(f"⚠️ Document context error: {document_context['error']}")
            elif document_context:
                print(f"✅ Document context retrieved: {document_context.get('document_name')} ({document_context.get('text_length', 0)} chars)")
        else:
            print(f"ℹ️ No document specified - will search across user's documents")
        
        # Get chat history for context
        previous_messages = execute_query(
            """
            SELECT role, content
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at ASC
            """,
            (session_id,),
            fetch_all=True
        )
        
        chat_history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in previous_messages
        ]
        
        # Save user message
        user_message_id = execute_query(
            """
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (%s, 'user', %s)
            """,
            (session_id, message_content),
            commit=True
        )
        
        # Generate AI response
        print(f"📨 Processing message for session {session_id}, user {user_id}")
        print(f"📄 Target document ID: {target_document_id}")
        print(f"💬 Question: {message_content[:100]}...")
        
        ai_result = chatbot.generate_response(
            question=message_content,
            document_context=document_context,
            chat_history=chat_history,
            user_id=user_id if not target_document_id else None  # Use multi-doc search if no specific doc
        )
        
        # Ensure we have a response
        if not ai_result or not ai_result.get('response'):
            print(f"⚠️ No response generated, using fallback")
            ai_result = {
                'response': "I apologize, but I wasn't able to generate a response. Please try rephrasing your question or check if Ollama is running properly.",
                'sources': [],
                'error': 'No response generated'
            }
        
        # Prepare metadata
        metadata = {
            'sources': ai_result.get('sources', [])
        }
        if ai_result.get('error'):
            metadata['error'] = ai_result['error']
        
        # Save assistant message
        assistant_message_id = execute_query(
            """
            INSERT INTO chat_messages (session_id, role, content, metadata)
            VALUES (%s, 'assistant', %s, %s)
            """,
            (session_id, ai_result['response'], json.dumps(metadata)),
            commit=True
        )
        
        print(f"✅ Saved assistant message {assistant_message_id}")
        
        # Update session updated_at timestamp
        execute_query(
            "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s",
            (session_id,),
            commit=True
        )
        
        return jsonify({
            'message': 'Message sent successfully',
            'userMessage': {
                'id': user_message_id,
                'sessionId': session_id,
                'role': 'user',
                'content': message_content,
                'createdAt': datetime.now().isoformat()
            },
            'assistantMessage': {
                'id': assistant_message_id,
                'sessionId': session_id,
                'role': 'assistant',
                'content': ai_result['response'],
                'metadata': metadata,
                'createdAt': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

