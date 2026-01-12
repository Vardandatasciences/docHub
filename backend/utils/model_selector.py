"""
Model Selector - Intelligently select Ollama model based on query complexity
Uses smaller/faster models for simple queries, better models for complex ones
"""
import re
import requests
import os
from typing import Dict, List
from flask import current_app


class ModelSelector:
    """Select optimal Ollama model based on query characteristics"""
    
    # Model definitions with capabilities
    # Ordered by preference (first available will be used)
    MODELS = {
        # Fast models for simple queries (1-3 words, yes/no, greetings)
        # These are the smallest and fastest models
        'fast': {
            'models': [
                'llama3.2:1b-instruct-q4_K_M',  # Smallest, fastest
                'tinyllama:latest',              # Alternative tiny model
                'llama3.2:3b'                    # Fallback if 1b not available
            ],
            'default': 'llama3.2:1b-instruct-q4_K_M',
            'max_tokens': 200,
            'temperature': 0.2
        },
        # Medium models for moderate queries (4-10 words, simple questions)
        # Balance between speed and quality
        'medium': {
            'models': [
                'llama3.2:3b-instruct-q4_K_M',  # Best medium model
                'llama3.2:3b',                   # Alternative
                'phi3:mini'                      # Another option
            ],
            'default': 'llama3.2:3b-instruct-q4_K_M',
            'max_tokens': 500,
            'temperature': 0.3
        },
        # Better models for complex queries (long questions, analysis, summaries)
        # Higher quality for complex tasks
        'complex': {
            'models': [
                'llama3.1:8b',                   # High quality, balanced
                'llama3:8b-instruct-q4_K_M',     # Instruct-tuned variant
                'llama2:latest'                  # Fallback
            ],
            'default': 'llama3.1:8b',
            'max_tokens': 1000,
            'temperature': 0.3
        },
        # Best model for very complex tasks (multi-document, deep analysis)
        # Use the best available model for advanced tasks
        'advanced': {
            'models': [
                'llama3:8b-instruct-q4_K_M',     # Instruct-tuned for better following
                'llama3.1:8b',                   # High quality
                'llama2:latest'                  # Fallback
            ],
            'default': 'llama3:8b-instruct-q4_K_M',
            'max_tokens': 2000,
            'temperature': 0.3
        }
    }
    
    # Simple question patterns (use fast models)
    SIMPLE_PATTERNS = [
        r'^(hi|hello|hey|greetings)\s*[!?.]?$',
        r'^(yes|no|ok|okay|sure|thanks|thank you)\s*[!?.]?$',
        r'^\w+\?$',  # Single word questions
        r'^(what|who|when|where|why|how)\s+\w+\s*\?$',  # Simple what/who questions
        r'^(is|are|was|were|do|does|did|can|could|will|would)\s+\w+\s*\?$',  # Simple yes/no questions
    ]
    
    # Complex question indicators (use better models)
    COMPLEX_INDICATORS = [
        'analyze', 'compare', 'summarize', 'explain in detail',
        'describe', 'evaluate', 'discuss', 'review',
        'all documents', 'multiple', 'across', 'between',
        'difference', 'similarity', 'relationship',
        'extract', 'list all', 'find all', 'search for'
    ]
    
    @classmethod
    def detect_complexity(cls, question: str, document_context_length: int = 0, 
                          has_multiple_documents: bool = False) -> str:
        """
        Detect query complexity and return model tier
        
        Args:
            question: User's question
            document_context_length: Length of document context (chars)
            has_multiple_documents: Whether query spans multiple documents
            
        Returns:
            Model tier: 'fast', 'medium', 'complex', or 'advanced'
        """
        question = question.strip().lower()
        word_count = len(question.split())
        
        # Advanced: Multiple documents or very long context
        if has_multiple_documents or document_context_length > 5000:
            return 'advanced'
        
        # Check for simple patterns first (very fast)
        for pattern in cls.SIMPLE_PATTERNS:
            if re.match(pattern, question, re.IGNORECASE):
                return 'fast'
        
        # Check for complex indicators
        has_complex_keywords = any(
            indicator in question for indicator in cls.COMPLEX_INDICATORS
        )
        
        # Very short questions (1-3 words) - fast
        if word_count <= 3 and not has_complex_keywords:
            return 'fast'
        
        # Short questions (4-8 words) without complex keywords - medium
        if word_count <= 8 and not has_complex_keywords:
            return 'medium'
        
        # Long questions (9+ words) or has complex keywords - complex
        if word_count > 8 or has_complex_keywords:
            return 'complex'
        
        # Long context (even with medium questions) - complex
        if document_context_length > 2000:
            return 'complex'
        
        # Default to medium for safety
        return 'medium'
    
    @classmethod
    def select_model(cls, question: str, document_context_length: int = 0,
                     has_multiple_documents: bool = False,
                     available_models: list = None) -> Dict:
        """
        Select optimal model and parameters based on query
        
        Args:
            question: User's question
            document_context_length: Length of document context
            has_multiple_documents: Whether multiple documents are involved
            available_models: List of available model names (optional, for validation)
            
        Returns:
            Dict with model_name, temperature, and max_tokens
        """
        complexity = cls.detect_complexity(
            question, 
            document_context_length, 
            has_multiple_documents
        )
        
        tier_config = cls.MODELS[complexity]
        
        # Select model from tier
        selected_model = tier_config['default']
        
        # If available_models provided, try to match available models
        if available_models:
            for model in tier_config['models']:
                if model in available_models:
                    selected_model = model
                    break
        
        return {
            'model': selected_model,
            'tier': complexity,
            'temperature': tier_config['temperature'],
            'max_tokens': tier_config.get('max_tokens'),
            'reason': f"Selected {complexity} tier model for query"
        }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with model tier and capabilities
        """
        for tier, config in cls.MODELS.items():
            if model_name in config['models'] or model_name == config['default']:
                return {
                    'tier': tier,
                    'temperature': config['temperature'],
                    'max_tokens': config.get('max_tokens'),
                    'is_fast': tier in ['fast', 'medium'],
                    'is_advanced': tier in ['complex', 'advanced']
                }
        
        # Default info if model not found
        return {
            'tier': 'medium',
            'temperature': 0.3,
            'max_tokens': 500,
            'is_fast': True,
            'is_advanced': False
        }
    
    @classmethod
    def get_available_models(cls, base_url: str = None) -> List[str]:
        """
        Get list of available models from Ollama server
        
        Args:
            base_url: Ollama base URL (defaults to config)
            
        Returns:
            List of available model names
        """
        try:
            # Get base URL
            if not base_url:
                try:
                    base_url = current_app.config.get('OLLAMA_BASE_URL')
                except RuntimeError:
                    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            
            base_url = base_url.rstrip('/')
            url = f"{base_url}/api/tags"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                print(f"✅ Found {len(models)} available Ollama models")
                return models
            else:
                print(f"⚠️ Failed to fetch models: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ Error fetching available models: {str(e)}")
            return []
    
    @classmethod
    def select_model_with_availability_check(cls, question: str, 
                                             document_context_length: int = 0,
                                             has_multiple_documents: bool = False,
                                             base_url: str = None) -> Dict:
        """
        Select optimal model, checking availability first
        
        Args:
            question: User's question
            document_context_length: Length of document context
            has_multiple_documents: Whether multiple documents are involved
            base_url: Ollama base URL (optional)
            
        Returns:
            Dict with model_name, temperature, and other config
        """
        # Get available models
        available_models = cls.get_available_models(base_url)
        
        # Select model (will use available models if provided)
        return cls.select_model(
            question=question,
            document_context_length=document_context_length,
            has_multiple_documents=has_multiple_documents,
            available_models=available_models if available_models else None
        )

