import os
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel
from google import genai
from google.genai import types

class AIService:
    """
    AIService abstracts all LLM interactions. It uses the official Google GenAI SDK
    and provides methods for text generation and structured JSON schema outputs.
    """
    
    def __init__(self):
        # Retrieve the API key from environment variables
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Instantiate client if key is configured, else delay till invocation
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            
        # Default model is Gemini 2.5 Flash as per specifications
        self.default_model = "gemini-2.5-flash"

    def get_client(self) -> genai.Client:
        """
        Returns the genai.Client instance. Raises ValueError if API key is not configured.
        """
        if not self.client:
            raise ValueError(
                "Gemini API key is not configured. Please set a valid GEMINI_API_KEY "
                "in your backend/.env file and restart the server."
            )
        return self.client

    def generate_text(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Submits a text prompt and returns the string response.
        """
        client = self.get_client()
        model_name = model or self.default_model
        
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API text generation failed: {str(e)}")

    def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[BaseModel], 
        model: Optional[str] = None, 
        system_instruction: Optional[str] = None
    ) -> BaseModel:
        """
        Uses Gemini's structured output capability to extract facts directly mapped
        to a specified Pydantic data schema class.
        """
        client = self.get_client()
        model_name = model or self.default_model
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            # Parse the JSON string into the Pydantic schema
            return response_schema.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Gemini structured extraction failed: {str(e)}")
