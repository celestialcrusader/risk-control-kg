import httpx
import os

try:
    from langfuse import observe
except ImportError:
    # Dummy decorator if langfuse missing or import fails
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

class LLMException(Exception):
    pass

class LLMClient:
    def __init__(self, base_url: str = None, model: str = "qwen2.5:7b"):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    @observe(as_type="generation")
    def generate(self, prompt: str) -> str:
        """
        Generates text completion using Ollama API.
        Does not use streaming for simplicity in this version.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # Increased timeout to 300s to allow for slow model loading on CPU
            response = httpx.post(url, json=payload, timeout=300.0)
            
            if response.status_code != 200:
                raise LLMException(f"Ollama API Error: {response.status_code} - {response.text}")
                
            data = response.json()
            return data.get("response", "")
            
        except httpx.RequestError as e:
            raise LLMException(f"Connection Error: {str(e)}")
            
    @observe(as_type="generation")
    def generate_structured(self, prompt: str, response_model: any) -> any:
        """
        Generates structured output conforming to a Pydantic model.
        """
        import json
        from pydantic import ValidationError
        
        # We need to manually update the span with model parameters if desired, 
        # but @observe captures inputs/outputs automatically.

        schema = response_model.model_json_schema()
        
        # Enhanced prompt to force JSON format matching the schema
        system_msg = f"""You are a data extraction assistant. You must output valid JSON only. 
        Do not explain. Do not wrap in markdown blocks. 
        The JSON must strictly follow this schema:
        {json.dumps(schema, indent=2)}
        """
        
        full_prompt = f"{system_msg}\n\nTask: {prompt}"
        
        # Some models support "format": "json" natively in Ollama
        # We'll use strict mode prompting + format='json' (if supported by model/api, safe to always send)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            # Increased timeout to 300s
            response = httpx.post(url, json=payload, timeout=300.0)
            
            if response.status_code != 200:
                raise LLMException(f"Ollama API Error: {response.status_code} - {response.text}")
                
            data = response.json()
            raw_text = data.get("response", "")
            
            try:
                # Attempt to parse JSON
                json_data = json.loads(raw_text)
                return response_model.model_validate(json_data)
            except json.JSONDecodeError:
                raise LLMException(f"LLM failed to return valid JSON: {raw_text}")
            except ValidationError as e:
                raise LLMException(f"Validation Error: {str(e)}")
                
        except httpx.RequestError as e:
            raise LLMException(f"Connection Error: {str(e)}")
