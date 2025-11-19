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
        vendor_opening = self.llm.generate(prompt, max_tokens=300)

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

    def respond_to_offer(self, user_message: str, conversation: List[Dict]) -> Dict:
        """
        Vendor responds to buyer's negotiation message.

        Args:
            user_message: Buyer's proposal or question
            conversation: Current negotiation history

        Returns:
            Vendor's response
        """
        start_time = time.time()

        context = self._build_negotiation_context(conversation)
        prompt = f"""You are a vendor representative negotiating with a buyer about the following item:

Item: {self.selected_item.get('id')} from {self.selected_item.get('vendor')}
Current Price: ${self.selected_item.get('price')}
Current Lead Time: {self.selected_item.get('lead_time_days')} days

Negotiation History:
{context}

Buyer's latest proposal: {user_message}

As the vendor, respond to their proposal. You can:
- Offer small discounts (5-15%) for larger quantities
- Adjust delivery times slightly
- Bundle other components at discounts
- Offer long-term contract terms

Be realistic but willing to negotiate. Keep response concise and professional."""

        response = self.llm.generate(prompt, max_tokens=300)

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

        prompt = f"""You are a vendor representative from {vendor}. A buyer is interested in purchasing {item_id} from us.

Item Details:
- ID: {item_id}
- Price: ${price}
- Lead Time: {lead_time} days
- Reliability: {selected_item.get('reliability')}

The buyer's requirements:
- Max budget: ${request.get('max_cost', 'Not specified')}
- Delivery deadline: {request.get('latest_delivery_days', 'Not specified')} days

Provide a professional opening position. Include:
1. Your current pricing and terms
2. What you can offer in terms of flexibility
3. What you'd need to improve your terms (volume, commitment, etc.)
4. Your value proposition

Be professional, confident, and open to negotiation."""

        return prompt

    def _build_negotiation_context(self, conversation: List[Dict]) -> str:
        """Build context from negotiation history."""
        context_lines = []
        for msg in conversation:
            role = "Buyer" if msg.get("role") == "buyer" else "Vendor"
            context_lines.append(f"{role}: {msg.get('message', '')}")
        return "\n".join(context_lines[-6:])  # Last 3 exchanges only
