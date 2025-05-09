"""LLM module for AI Support Agent."""

from .provider import LLMProvider, LLMResponse
from .factory import LLMProviderFactory

# Import providers to ensure registration
from . import providers

# Convenience function to get a provider instance
def get_provider(provider_name: str = None) -> LLMProvider:
    """Get an LLM provider instance.
    
    Args:
        provider_name: Optional name of the provider (defaults to configured provider)
        
    Returns:
        LLMProvider: Provider instance
    """
    return LLMProviderFactory.get_provider(provider_name)

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "get_provider"
] 