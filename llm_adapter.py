"""
LLM Adapter module - Pluggable LLM interface and implementations.

Provides an abstract LLM adapter interface for generating natural language responses,
with a deterministic MockLLM implementation for testing and a provider selector for
swapping between different LLM backends.

Key exports:
  - LLMAdapter: Abstract base class
  - MockLLM: Deterministic implementation using hash-based generation
  - select_llm_provider(): Factory function to select LLM provider
"""

from abc import ABC, abstractmethod
import re

class LLMAdapter(ABC):
    """
    Abstract base class for LLMAdapter. Contains one abstract method generate.
    """
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate a response to the given prompt.

        Args:
            prompt: Input prompt string
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated response string
        """
        pass


class MockLLM(LLMAdapter):
    """
    A deterministic MockLLM class that inherits from LLMAdapter.
    Prefers higher-scoring items when multiple options are presented.
    """

    def _calculate_score(self, price: float, lead_time: float, reliability: float) -> float:
        """
        Calculate a simple score for comparison.

        Args:
            price: Item price
            lead_time: Lead time in days
            reliability: Reliability score (0-1)

        Returns:
            Score combining all factors
        """
        # Simple scoring: lower price and lead_time are better, higher reliability is better
        # Normalize to 0-1 range
        price_score = max(0, 1 - (price / 10000))  # Assume max price around 10000
        lead_score = max(0, 1 - (lead_time / 100))  # Assume max lead time around 100 days
        reliability_score = reliability

        # Weighted average (same as in procurement.py)
        return 0.4 * price_score + 0.3 * lead_score + 0.3 * reliability_score

    def _extract_items_from_prompt(self, prompt: str) -> list:
        """
        Extract all items from prompt (handles multiple items).

        Args:
            prompt: The prompt string

        Returns:
            List of item dicts with extracted details
        """
        items = []
        lines = prompt.split('\n')
        current_item = {}

        for line in lines:
            line_lower = line.lower()

            if "id:" in line_lower:
                # New item detected
                if current_item:
                    items.append(current_item)
                current_item = {}
                parts = line.split(':')
                if len(parts) > 1:
                    current_item['id'] = parts[1].strip()

            if "vendor:" in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    current_item['vendor'] = parts[1].strip()

            if "price:" in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    price_str = parts[1].strip()
                    try:
                        current_item['price'] = float(re.findall(r'\d+', price_str)[0])
                    except (IndexError, ValueError):
                        current_item['price'] = 0

            if "lead_time" in line_lower or "delivery" in line_lower:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    current_item['lead_time'] = float(numbers[0])

            if "reliability:" in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    try:
                        current_item['reliability'] = float(parts[1].strip())
                    except ValueError:
                        current_item['reliability'] = 0

        if current_item:
            items.append(current_item)

        return items

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """
        Generate a deterministic justification based on the prompt content.
        When multiple items are presented, prefers the higher-scoring item.

        Args:
            prompt: The prompt string containing item details
            max_tokens: Maximum tokens to generate (not used in mock)

        Returns:
            Deterministic justification string
        """
        # Check if this is a decision prompt
        if "choose between" in prompt.lower() or "selected" in prompt.lower():
            # Extract all items from prompt
            items = self._extract_items_from_prompt(prompt)

            if not items:
                return "Unable to parse items from prompt."

            # Score all items and select the best one
            best_item = None
            best_score = -1

            for item in items:
                price = item.get('price', 0)
                lead_time = item.get('lead_time', 0)
                reliability = item.get('reliability', 0)

                score = self._calculate_score(price, lead_time, reliability)

                if score > best_score:
                    best_score = score
                    best_item = item

            if not best_item:
                return "Unable to determine best item."

            # Generate justification for selected item
            item_id = best_item.get('id', 'Unknown')
            vendor = best_item.get('vendor', 'Unknown')
            price = best_item.get('price')
            lead_time = best_item.get('lead_time')
            reliability = best_item.get('reliability')

            # Build response
            response = f"Selected {item_id} from {vendor}."

            justification = "It balances"
            factors = []
            if price:
                factors.append(f"cost ({int(price)})")
            if lead_time:
                factors.append(f"delivery ({int(lead_time)} days)")
            if reliability:
                factors.append(f"strong reliability ({reliability})")

            if factors:
                justification += " " + " and ".join(factors)
                justification += ", making it the best fit for the request."
            else:
                justification = "It provides the best balance of price, delivery time, and reliability for the requirements."

            return response + " " + justification

        # Default response
        return "Based on the analysis, this item provides the best value considering price, lead time, and reliability metrics."


class OpenAILLM(LLMAdapter):
    """OpenAI LLM adapter using GPT models."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI adapter with API key.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate response using OpenAI API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a procurement expert helping to justify component selection decisions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"


def select_llm_provider(llm_provider: str = "mock", api_key: str = None) -> LLMAdapter:
    """
    Function to select an LLM provider.

    Args:
        llm_provider: Provider name ("mock", "openai", etc.)
        api_key: Optional API key for the provider

    Returns:
        LLMAdapter instance
    """
    import os

    if llm_provider.lower() == "openai":
        # Use provided API key or check environment
        key = api_key or os.getenv("OPENAI_API_KEY")
        if key:
            return OpenAILLM(api_key=key)
        else:
            # Return None to signal that API key is required
            return None
    else:
        # Default to MockLLM
        return MockLLM()