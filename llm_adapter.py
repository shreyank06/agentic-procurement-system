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
        Generate a deterministic response based on the prompt content.
        Handles both procurement justification and agent conversations.

        Args:
            prompt: The prompt string containing context
            max_tokens: Maximum tokens to generate (not used in mock)

        Returns:
            Deterministic response string
        """
        prompt_lower = prompt.lower()

        # Check if this is a cost optimization question
        if "cost optimi" in prompt_lower or "reduce cost" in prompt_lower or "save money" in prompt_lower or "cheaper" in prompt_lower:
            return self._generate_cost_optimization_response(prompt)

        # Check if this is a negotiation prompt
        if "vendor" in prompt_lower and ("negotiat" in prompt_lower or "offer" in prompt_lower or "discount" in prompt_lower):
            return self._generate_negotiation_response(prompt)

        # Check if this is a decision/selection prompt
        if "choose between" in prompt_lower or "selected" in prompt_lower:
            items = self._extract_items_from_prompt(prompt)
            if items:
                return self._generate_selection_justification(items)
            return "Unable to parse items from prompt."

        # Default response for general questions
        return "Based on the analysis, I recommend considering cost-benefit tradeoffs and vendor flexibility when making procurement decisions."

    def _generate_cost_optimization_response(self, prompt: str) -> str:
        """Generate cost optimization advice."""
        # Extract budget and item info from prompt
        responses = [
            "To reduce costs further, I recommend: (1) Negotiate volume discounts if ordering multiple units - typically 10-15% for bulk orders, (2) Explore alternative vendors with similar specs but lower pricing, (3) Consider relaxing non-critical specifications to access cheaper tier products, (4) Request extended payment terms which can reduce effective cost.",
            "Here are concrete cost reduction strategies: (1) Bulk purchasing power - negotiate for 15-20% discount on orders of 50+ units, (2) Long-term contracts - commit to 12-month supply agreements for 12-18% savings, (3) Logistics optimization - consolidate shipments or use slower shipping to save 8-12%, (4) Specification flexibility - minor relaxation of lead time or reliability specs can reduce costs by 20-30%.",
            "For this specific item, I suggest: (1) Direct vendor negotiation for volume discounts, (2) Requesting bundle deals with complementary components, (3) Timing flexibility - if you can wait longer, economy shipping saves 10-15%, (4) Comparing with tier-2 vendors that meet 80% of specs at 30-40% lower cost.",
            "To optimize cost while maintaining quality: (1) Negotiate based on your budget constraints, (2) Ask for quantity-based pricing breaks, (3) Explore supplier consolidation benefits, (4) Consider phased purchasing if possible, (5) Leverage competitive bids from 2-3 vendors to drive pricing down by 15-20%."
        ]
        # Return different responses based on hash of prompt for variety
        idx = hash(prompt) % len(responses)
        return responses[idx]

    def _generate_negotiation_response(self, prompt: str) -> str:
        """Generate vendor negotiation response."""
        responses = [
            "We can offer a 10% discount for orders of 50+ units or a 12-month commitment. For the delivery timeline, we can adjust to 10 days if needed with a slight expediting fee. We also offer bundle discounts if you're ordering multiple items.",
            "Thank you for your offer. We can work with you on pricing - we typically offer volume discounts (5-15% for larger orders) or 8% off for long-term contracts. On delivery, we're flexible and can accelerate to 3 days for an additional 5% fee if necessary.",
            "We appreciate the interest. Given your requirements, I can offer: 12% discount for 100+ unit orders, or 8% for 50+ units. We can also commit to 5-day delivery standard at no extra cost. Would you be interested in discussing a quarterly supply agreement?",
            "That's a fair point. We can definitely improve our offer: 15% volume discount (minimum 75 units), free expedited shipping to 3 days for orders over $10K, or 10% discount with a 6-month commitment. What aspects are most important for your procurement?"
        ]
        # Return different responses based on hash of prompt for variety
        idx = hash(prompt) % len(responses)
        return responses[idx]

    def _generate_selection_justification(self, items: list) -> str:
        """Generate justification for item selection."""
        if not items:
            return "Unable to determine best item."

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