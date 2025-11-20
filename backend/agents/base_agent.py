"""
Base Agent Class - Abstract base class for all agents.

Provides common functionality and interface for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import time


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None, catalog: Optional[Any] = None):
        """Initialize base agent.

        Args:
            llm_provider: LLM provider to use (e.g., 'openai')
            api_key: API key for the LLM provider
            catalog: Optional catalog instance for semantic search
        """
        from backend.services.llm_service import LLMService

        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = LLMService.get_provider(llm_provider, api_key)
        self.catalog = catalog
        self.context = {}
        self.state = {}

    def generate_response(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate response using the configured LLM.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in the response

        Returns:
            Generated response text
        """
        if self.llm is None:
            raise RuntimeError(f"LLM provider '{self.llm_provider}' failed to initialize")
        return self.llm.generate(prompt, max_tokens=max_tokens)

    def build_prompt(self, **kwargs) -> str:
        """Build a prompt for the LLM. To be implemented by subclasses.

        Returns:
            Formatted prompt string
        """
        raise NotImplementedError("Subclasses must implement build_prompt()")

    @abstractmethod
    def process(self, *args, **kwargs) -> Dict:
        """Main processing method. To be implemented by subclasses.

        Returns:
            Processing result dictionary
        """
        pass

    def measure_time(func):
        """Decorator to measure execution time."""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            if isinstance(result, dict):
                result['latency'] = elapsed
            return result
        return wrapper
