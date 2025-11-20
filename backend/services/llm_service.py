"""
LLM Service - Abstraction layer for LLM providers.

Provides unified interface for interacting with different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text using the LLM.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in the response

        Returns:
            Generated text
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text using OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing (fallback only)."""

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate mock response."""
        return "Mock response: Based on the analysis, I recommend considering cost-benefit tradeoffs and vendor flexibility when making procurement decisions."


class LLMService:
    """Service factory for LLM providers."""

    _providers = {
        "openai": OpenAIProvider,
        "mock": MockLLMProvider,
    }

    @staticmethod
    def get_provider(provider_name: str, api_key: Optional[str] = None) -> Optional[LLMProvider]:
        """Get LLM provider instance.

        Args:
            provider_name: Name of the provider
            api_key: API key for the provider

        Returns:
            LLM provider instance or None
        """
        provider_class = LLMService._providers.get(provider_name.lower())
        if not provider_class:
            return None

        try:
            if provider_name.lower() == "openai":
                return provider_class(api_key)
            else:
                return provider_class()
        except Exception:
            return None

    @staticmethod
    def register_provider(name: str, provider_class):
        """Register a new LLM provider.

        Args:
            name: Provider name
            provider_class: Provider class inheriting from LLMProvider
        """
        LLMService._providers[name.lower()] = provider_class
