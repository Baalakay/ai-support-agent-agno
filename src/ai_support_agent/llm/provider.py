"""Base provider interface for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')

@dataclass
class LLMResponse(Generic[T]):
    """Response from an LLM provider."""
    content: T
    model: str
    usage: Dict[str, int]


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
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
        """
        pass
    
    @abstractmethod
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
        """
        pass 