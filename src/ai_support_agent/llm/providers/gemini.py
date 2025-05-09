"""Gemini provider implementation."""

import json
import logging
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types.content import Part
from google.generativeai.types.generation_types import GenerationConfig

from ..provider import LLMProvider, LLMResponse
from ...config import get_llm_config

logger = logging.getLogger(__name__)


class GeminiError(Exception):
    """Base error for Gemini operations."""
    pass


class GeminiConfigError(GeminiError):
    """Error raised when Gemini configuration is invalid."""
    pass


class GeminiGenerationError(GeminiError):
    """Error raised when text/JSON generation fails."""
    pass


class GeminiProvider(LLMProvider):
    """Gemini provider implementation.
    
    This provider implements the LLMProvider interface for Google's
    Gemini language model.
    """
    
    def __init__(self):
        """Initialize the Gemini provider.
        
        Raises:
            GeminiConfigError: If configuration is invalid
        """
        try:
            # Load configuration
            self.config = get_llm_config()
            self.model = self.config["model"]
            
            # Configure Gemini
            genai.configure(api_key=self.config["api_key"])
            self._model = genai.GenerativeModel(self.model)
            
            logger.info(f"Initialized Gemini provider with model: {self.model}")
            
        except Exception as e:
            if isinstance(e, GeminiConfigError):
                raise
            raise GeminiConfigError(f"Failed to initialize Gemini provider: {str(e)}")
    
    def _get_token_usage(self, response: GenerateContentResponse) -> Dict[str, int]:
        """Get token usage from response.
        
        Args:
            response: Gemini response
            
        Returns:
            Dict[str, int]: Token usage statistics
        """
        # Note: Gemini doesn't provide token counts directly
        # This is a placeholder for when they add this functionality
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    
    def _handle_response(self, response: GenerateContentResponse, output_type: str = "text") -> Any:
        """Handle Gemini response.
        
        Args:
            response: Gemini response
            output_type: Expected output type ("text" or "json")
            
        Returns:
            Any: Processed response content
            
        Raises:
            GeminiGenerationError: If response processing fails
        """
        try:
            if not response.text:
                raise GeminiGenerationError("Empty response from Gemini")
            
            text = response.text.strip()
            if output_type == "json":
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    raise GeminiGenerationError(f"Invalid JSON response: {str(e)}")
            return text
            
        except Exception as e:
            if isinstance(e, GeminiGenerationError):
                raise
            raise GeminiGenerationError(f"Failed to process {output_type} response: {str(e)}")
    
    def _create_generation_config(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GenerationConfig:
        """Create generation configuration.
        
        Args:
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            GenerationConfig: The generation configuration
            
        Raises:
            GeminiConfigError: If configuration is invalid
        """
        try:
            config = {
                "temperature": temperature or self.config["temperature"],
                "max_output_tokens": max_tokens or self.config["max_tokens"]
            }
            
            # Validate configuration values
            if not 0 <= config["temperature"] <= 1:
                raise GeminiConfigError("Temperature must be between 0 and 1")
            if config["max_output_tokens"] < 1:
                raise GeminiConfigError("Max tokens must be positive")
            
            return GenerationConfig(**config)
            
        except Exception as e:
            if isinstance(e, GeminiConfigError):
                raise
            raise GeminiConfigError(f"Failed to create generation config: {str(e)}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse[str]:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate from
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse[str]: The generated text response
            
        Raises:
            GeminiGenerationError: If generation fails
        """
        try:
            # Create generation configuration
            generation_config = self._create_generation_config(
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Generate response
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Process response
            content = self._handle_response(response, "text")
            usage = self._get_token_usage(response)
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage
            )
            
        except Exception as e:
            if isinstance(e, (GeminiConfigError, GeminiGenerationError)):
                raise
            raise GeminiGenerationError(f"Text generation failed: {str(e)}")
    
    def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse[Dict[str, Any]]:
        """Generate JSON from a prompt.
        
        Args:
            prompt: The prompt to generate from
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse[Dict[str, Any]]: The generated JSON response
            
        Raises:
            GeminiGenerationError: If generation fails
        """
        try:
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\nRespond with valid JSON only."
            
            # Create generation configuration
            generation_config = self._create_generation_config(
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Generate response
            response = self._model.generate_content(
                json_prompt,
                generation_config=generation_config
            )
            
            # Process response
            content = self._handle_response(response, "json")
            usage = self._get_token_usage(response)
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage
            )
            
        except Exception as e:
            if isinstance(e, (GeminiConfigError, GeminiGenerationError)):
                raise
            raise GeminiGenerationError(f"JSON generation failed: {str(e)}") 