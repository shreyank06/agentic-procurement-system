from abc import ABC, abstractmethod

class LLMAdapter(ABC):
    """
    Abstract base class for LLMAdapter. Contains one abstract method generate.
    """
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        pass


class MockLLM(LLMAdapter):
    """
    A deterministic MockLLM class that inherits from LLMAdapter.
    """
    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        # Your code here
        pass


def select_llm_provider(llm_provider: str):
    """
    Function to select an LLM provider. Returns MockLLM if environment variables for real providers are not present.
    """
    # Your code here
    pass