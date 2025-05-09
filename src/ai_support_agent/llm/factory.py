"""Factory for creating LLM providers."""

import logging
from typing import Dict, Type, Optional

from .provider import LLMProvider
from ..config.config import get_llm_config

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers: Dict[str, Type[LLMProvider]] = {}
    _instances: Dict[str, LLMProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """Register a new provider.
        
        Args:
            name: Name of the provider
            provider_class: Provider class to register
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered provider: {name}")
    
    @classmethod
    def create_provider(cls, provider_name: Optional[str] = None) -> LLMProvider:
        """Create a provider instance.
        
        Args:
            provider_name: Name of the provider (defaults to configured provider)
            
        Returns:
            LLMProvider: Provider instance
            
        Raises:
            ValueError: If the provider is not supported
        """
        config = get_llm_config()
        provider_name = provider_name or config["provider"]
        provider_name = provider_name.lower()
        
        # Return cached instance if available
        if provider_name in cls._instances:
            return cls._instances[provider_name]
        
        # Get provider class
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: {supported}"
            )
        
        # Create new instance
        provider = provider_class(config)
        cls._instances[provider_name] = provider
        return provider
    
    @classmethod
    def get_provider(cls, provider_name: Optional[str] = None) -> LLMProvider:
        """Get a provider instance (alias for create_provider).
        
        Args:
            provider_name: Name of the provider (defaults to configured provider)
            
        Returns:
            LLMProvider: Provider instance
        """
        return cls.create_provider(provider_name) 