"""
Ollama Helper - Wrapper for Ollama API calls
Provides easy interface to interact with Ollama models
"""
import os
import requests
import json
from typing import Optional, Dict, List
from flask import current_app


class OllamaHelper:
    """Helper class for interacting with Ollama API"""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama helper
        
        Args:
            base_url: Ollama API base URL (defaults to config or env var)
            model: Model name to use (defaults to config or env var)
        """
        # Get from Flask config if available, otherwise from env
        try:
            self.base_url = base_url or current_app.config.get('OLLAMA_BASE_URL') or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            self.model = model or current_app.config.get('OLLAMA_MODEL') or os.environ.get('OLLAMA_MODEL', 'llama3.1:8b')
        except RuntimeError:
            # Outside Flask context, use env vars
            self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            self.model = model or os.environ.get('OLLAMA_MODEL', 'llama3.1:8b')
        
        # Ensure base_url doesn't end with /
        self.base_url = self.base_url.rstrip('/')
        
        print(f"🤖 Ollama initialized: {self.base_url} | Model: {self.model}")
    
    def set_model(self, model: str):
        """Dynamically change the model"""
        old_model = self.model
        self.model = model
        print(f"🔄 Model changed: {old_model} → {self.model}")
    
    def check_connection(self) -> bool:
        """
        Check if Ollama server is accessible
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama connection failed: {str(e)}")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.3, max_tokens: Optional[int] = None,
                 format: Optional[str] = None) -> Dict:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            format: Response format (e.g., "json" for JSON responses)
            
        Returns:
            Dict with 'response' and 'error' keys
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            if format:
                payload["format"] = format
            
            print(f"📤 Sending request to Ollama ({self.model})...")
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {"response": None, "error": error_msg}
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            print(f"✅ Received response from Ollama ({len(generated_text)} chars)")
            return {"response": generated_text, "error": None}
            
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            print(f"❌ {error_msg}")
            return {"response": None, "error": error_msg}
        except Exception as e:
            error_msg = f"Ollama request failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"response": None, "error": error_msg}
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3,
             format: Optional[str] = None) -> Dict:
        """
        Chat completion using Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "system", "content": "..."}, 
                              {"role": "user", "content": "..."}]
            temperature: Temperature for generation
            format: Response format (e.g., "json")
            
        Returns:
            Dict with 'response' and 'error' keys
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if format:
                payload["format"] = format
            
            print(f"📤 Sending chat request to Ollama ({self.model})...")
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {"response": None, "error": error_msg}
            
            result = response.json()
            generated_text = result.get("message", {}).get("content", "").strip()
            
            print(f"✅ Received chat response from Ollama ({len(generated_text)} chars)")
            return {"response": generated_text, "error": None}
            
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            print(f"❌ {error_msg}")
            return {"response": None, "error": error_msg}
        except Exception as e:
            error_msg = f"Ollama request failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"response": None, "error": error_msg}
    
    def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.3,
                    format: Optional[str] = None):
        """
        Stream chat completion using Ollama (generator function)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            format: Response format (e.g., "json")
            
        Yields:
            Dict with 'content' (chunk text) and 'done' (bool) keys
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,  # Enable streaming
                "options": {
                    "temperature": temperature
                }
            }
            
            if format:
                payload["format"] = format
            
            print(f"📤 Sending streaming chat request to Ollama ({self.model})...")
            response = requests.post(url, json=payload, stream=True, timeout=120)
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                yield {"content": "", "done": True, "error": error_msg}
                return
            
            # Stream the response
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.strip():
                            chunk = json.loads(line_text)
                            
                            # Check if this is the final chunk
                            done = chunk.get('done', False)
                            content = chunk.get('message', {}).get('content', '')
                            
                            yield {
                                "content": content,
                                "done": done,
                                "error": None
                            }
                            
                            if done:
                                print(f"✅ Streaming complete")
                                break
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"⚠️ Error parsing stream chunk: {str(e)}")
                        continue
            
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            print(f"❌ {error_msg}")
            yield {"content": "", "done": True, "error": error_msg}
        except Exception as e:
            error_msg = f"Ollama streaming failed: {str(e)}"
            print(f"❌ {error_msg}")
            yield {"content": "", "done": True, "error": error_msg}
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                     temperature: float = 0.3) -> Optional[Dict]:
        """
        Generate JSON response from Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature
            
        Returns:
            Parsed JSON dict or None if error
        """
        result = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            format="json"
        )
        
        if result["error"]:
            return None
        
        try:
            # Try to parse JSON
            response_text = result["response"]
            
            # Clean up if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON response: {str(e)}")
            print(f"Response was: {result['response'][:200]}")
            return None

