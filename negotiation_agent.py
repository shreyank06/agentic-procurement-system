"""
Negotiation Agent - Single LLM-powered agent for vendor negotiation.

Simulates vendor responses and negotiates terms with the buyer.
"""

import json
import time
from typing import List, Dict, Optional
from llm_adapter import select_llm_provider


class NegotiationAgent:
    """Single LLM-powered agent representing vendor in negotiations."""

    def __init__(self, llm_provider: str = "mock", api_key: str = None):
        """Initialize the negotiation agent as a vendor."""
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = select_llm_provider(llm_provider, api_key)
        self.selected_item = None
        self.negotiation_state = {
            "discount_offered": 0,
            "delivery_adjusted": False,
            "bulk_commitment": False
        }

    def start_negotiation(self, selected_item: Dict, request: Dict) -> Dict:
        """
        Start negotiation with vendor opening offer.

        Args:
            selected_item: The selected component from procurement
            request: Original procurement request

        Returns:
            Dict with vendor's opening position
        """
        self.selected_item = selected_item
        start_time = time.time()

        prompt = self._build_opening_prompt(selected_item, request)
        vendor_opening = self.llm.generate(prompt, max_tokens=200)

        result = {
            "selected_item": selected_item,
            "vendor_opening": vendor_opening,
            "conversation": [
                {
                    "role": "vendor",
                    "message": vendor_opening,
                    "timestamp": time.time()
                }
            ],
            "latency": time.time() - start_time
        }

        return result

    def respond_to_offer(self, user_message: str, conversation: List[Dict], request: Dict = None) -> Dict:
        """
        Vendor responds to buyer's negotiation message.

        Args:
            user_message: Buyer's proposal or question
            conversation: Current negotiation history
            request: Original procurement request (for context)

        Returns:
            Vendor's response
        """
        start_time = time.time()

        # Extract quantity from conversation or message
        quantity = self._extract_quantity(user_message, conversation)

        # Calculate appropriate discount based on quantity
        discount = self._calculate_vendor_discount(quantity)

        # Determine if this is a repeated request
        last_offer = self._get_last_offer(conversation)

        # Generate response based on negotiation state
        response = self._generate_negotiation_response(user_message, quantity, discount, last_offer)

        result = {
            "role": "vendor",
            "message": response,
            "timestamp": time.time(),
            "latency": time.time() - start_time
        }

        return result

    def _extract_quantity(self, user_message: str, conversation: List[Dict]) -> int:
        """Extract order quantity from message or conversation."""
        import re
        # Look for numbers in the current message
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            return int(numbers[0])

        # Look back in conversation for mentioned quantity
        for msg in reversed(conversation):
            numbers = re.findall(r'\d+', msg.get('message', ''))
            if numbers:
                return int(numbers[0])

        return 0

    def _calculate_vendor_discount(self, quantity: int) -> float:
        """Calculate appropriate discount based on quantity."""
        if quantity < 10:
            return 0.05  # 5% for very small
        elif quantity < 15:
            return 0.05  # 5% for small
        elif quantity < 30:
            return 0.08  # 8% for medium
        elif quantity < 50:
            return 0.10  # 10% for larger medium
        else:
            return 0.12  # 12% for large

    def _get_last_offer(self, conversation: List[Dict]) -> dict:
        """Get the last vendor offer from conversation."""
        for msg in reversed(conversation):
            if msg.get('role') == 'vendor':
                text = msg.get('message', '')
                # Extract discount percentage if mentioned
                import re
                discounts = re.findall(r'(\d+)%', text)
                if discounts:
                    return {
                        "discount": int(discounts[0]),
                        "message": text
                    }
        return None

    def _generate_negotiation_response(self, user_message: str, quantity: int, discount: float, last_offer: dict) -> str:
        """Generate vendor response based on negotiation state."""
        price = self.selected_item.get('price', 5200)
        discount_pct = int(discount * 100)
        discounted_price = price * (1 - discount)
        total_price = discounted_price * quantity if quantity > 0 else discounted_price

        # Detect buyer behavior
        wants_more = any(word in user_message.lower() for word in ['more', 'higher', 'increase', 'better', 'can you give'])
        asking_alternative = any(word in user_message.lower() for word in ['alternative', 'option', 'else', 'other'])
        refusing = any(word in user_message.lower() for word in ['no', 'not interested', 'cant', 'cannot', 'refuse', 'sorry'])

        # If last offer exists and buyer is asking for more
        if last_offer and wants_more:
            last_discount = last_offer.get('discount', 0)
            if last_discount >= discount_pct:
                # Stick to what we already offered
                return f"As I stated, {last_discount}% is the best I can offer for {quantity} units, bringing the total to ${total_price:,.0f}. This is firm unless you can commit to a larger volume."
            else:
                # Can only marginally improve
                improved_discount = min(last_discount + 2, discount_pct)
                improved_price = price * (1 - (improved_discount / 100))
                improved_total = improved_price * quantity if quantity > 0 else improved_price
                return f"Okay, I can improve to {improved_discount}% for {quantity} units, totaling ${improved_total:,.0f}. This is my final offer at this volume."

        # If buyer is refusing
        if refusing:
            return f"Understood. If you reconsider, {discount_pct}% remains available for {quantity} units (${total_price:,.0f}), or we can discuss larger volumes for better pricing."

        # Standard offer
        if quantity > 0:
            return f"For {quantity} units, I can offer {discount_pct}% off, bringing the unit price to ${discounted_price:,.0f} and total to ${total_price:,.0f}. Let me know if this works for you."
        else:
            return f"I can offer {discount_pct}% discount for volume purchases. Just let me know your quantity and we'll finalize the terms."

    def _build_opening_prompt(self, selected_item: Dict, request: Dict) -> str:
        """Build the opening negotiation prompt."""
        vendor = selected_item.get("vendor", "Unknown")
        item_id = selected_item.get("id")
        price = selected_item.get("price")
        lead_time = selected_item.get("lead_time_days")

        prompt = f"""You are a vendor rep from {vendor} opening negotiations for {item_id}.
Current price: ${price}/unit, {lead_time} day lead time, 0.975 reliability.

State your opening position directly (2-3 sentences). DO NOT use "thank you" or excessive politeness.
Simply state the price, what makes this a good product, and ONE condition for better pricing (volume, long-term contract, etc.)"""

        return prompt

    def _build_negotiation_context(self, conversation: List[Dict]) -> str:
        """Build context from negotiation history - include full conversation for consistency."""
        context_lines = []
        for msg in conversation:
            role = "Buyer" if msg.get("role") == "buyer" else "Vendor"
            message = msg.get('message', '')
            # Extract just the discount/price info to keep it concise
            context_lines.append(f"{role}: {message}")
        # Include full conversation history to ensure consistency
        return "\n".join(context_lines)
