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

        context = self._build_negotiation_context(conversation)

        # Add budget context if available
        budget_info = ""
        if request:
            budget_info = f"""
Buyer's Budget Constraints:
- Max Cost: ${request.get('max_cost', 'Not specified')}
- Delivery Deadline: {request.get('latest_delivery_days', 'Not specified')} days
"""

        prompt = f"""You are a vendor negotiating {self.selected_item.get('id')} at ${self.selected_item.get('price')}/unit.

Buyer said: {user_message}

Previous negotiation context:
{context}

Respond in 2-3 sentences. Rules:
1. BE CONSISTENT - if you already stated a discount for this quantity, stick to it
2. DO NOT contradict previous offers or discounts already mentioned
3. Be firm: small orders (under 15 units) = max 5% discount; medium (15-50) = max 8-10% discount
4. If buyer pushes hard, you can slightly increase but acknowledge the change ("Okay, I can improve to...")
5. NO excessive politeness or thanking
6. For refusal: state clearly and offer alternative (e.g., "5% is my final offer, or you can order 50+ for 12%")"""

        response = self.llm.generate(prompt, max_tokens=200)

        result = {
            "role": "vendor",
            "message": response,
            "timestamp": time.time(),
            "latency": time.time() - start_time
        }

        return result

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
