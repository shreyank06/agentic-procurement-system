"""
Negotiation Agent - Single LLM-powered agent for vendor negotiation.

Simulates vendor responses and negotiates terms with the buyer.
"""

import json
import time
from typing import List, Dict, Optional
from llm_adapter import select_llm_provider


class NegotiationAgent:
    """Single LLM-powered agent representing vendor in negotiations with semantic awareness."""

    def __init__(self, llm_provider: str = "mock", api_key: str = None, catalog=None):
        """Initialize the negotiation agent as a vendor.

        Args:
            llm_provider: LLM provider to use
            api_key: API key for LLM provider
            catalog: Catalog instance for finding competitive alternatives
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = select_llm_provider(llm_provider, api_key)
        self.selected_item = None
        self.catalog = catalog
        self.negotiation_state = {
            "discount_offered": 0,
            "delivery_adjusted": False,
            "bulk_commitment": False,
            "confirmation_asked": False,
            "order_confirmed": False
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
        Vendor responds to buyer's negotiation message using LLM.

        Args:
            user_message: Buyer's proposal or question
            conversation: Current negotiation history
            request: Original procurement request (for context)

        Returns:
            Vendor's response with order confirmation workflow
        """
        start_time = time.time()
        import re

        # Check if user is confirming or rejecting order
        msg_lower = user_message.lower()

        # If order was confirmed, submit it
        if self.negotiation_state.get("confirmation_asked"):
            if any(word in msg_lower for word in ['yes', 'confirm', 'accept', 'proceed', 'go ahead', 'submit']):
                self.negotiation_state["order_confirmed"] = True
                return {
                    "role": "vendor",
                    "message": f"Perfect! Order confirmed. Your order for {self.selected_item.get('id')} has been submitted. You will receive a confirmation email shortly.",
                    "timestamp": time.time(),
                    "latency": time.time() - start_time,
                    "order_status": "confirmed",
                    "order_details": self._get_order_details()
                }
            elif any(word in msg_lower for word in ['no', 'cancel', 'wait', 'hold', 'reconsider', "don't"]):
                # Reset confirmation state, wait for user input
                self.negotiation_state["confirmation_asked"] = False
                return {
                    "role": "vendor",
                    "message": "Understood. No problem - what would you like to adjust or discuss further?",
                    "timestamp": time.time(),
                    "latency": time.time() - start_time,
                    "order_status": "waiting"
                }

        # Build context from conversation
        context = self._build_negotiation_context(conversation)

        # Build the negotiation prompt
        prompt = self._build_negotiation_response_prompt(
            user_message=user_message,
            context=context,
            selected_item=self.selected_item,
            request=request
        )

        # Generate response using LLM
        response = self.llm.generate(prompt, max_tokens=200)

        # Add order confirmation request at the end of vendor response
        confirmation_request = self._build_confirmation_request()
        final_response = f"{response}\n\n{confirmation_request}"

        # Mark confirmation as asked
        self.negotiation_state["confirmation_asked"] = True

        result = {
            "role": "vendor",
            "message": final_response,
            "timestamp": time.time(),
            "latency": time.time() - start_time,
            "order_status": "negotiating",
            "order_details": self._get_order_details()
        }

        return result


    def _build_negotiation_response_prompt(self, user_message: str, context: str, selected_item: Dict, request: Dict = None) -> str:
        """Build prompt for vendor's response to buyer's message."""
        vendor = selected_item.get("vendor", "Unknown")
        item_id = selected_item.get("id")
        price = selected_item.get("price")
        lead_time = selected_item.get("lead_time_days")
        reliability = selected_item.get("reliability", 0.975)

        item_context = f"""
You are a sales representative from {vendor}.
Product: {item_id}
Standard Price: ${price}/unit
Lead Time: {lead_time} days
Reliability: {reliability}

Your negotiation goals:
1. Protect pricing for small orders
2. Offer meaningful discounts only for volume commitments (50+ units)
3. Be flexible on delivery timelines but charge for expedited shipping
4. Maintain professional but firm tone
5. Remember all previous offers made in this conversation"""

        if context:
            item_context += f"""

Negotiation History:
{context}"""

        prompt = f"""{item_context}

Buyer's Latest Message: {user_message}

Respond as the vendor. Be dynamic and natural. Consider the buyer's request carefully:
- If asking about price, reference specific quantities and offer tiered discounts
- If asking about delivery, discuss timelines and potential expediting fees
- If negotiating on previous offers, acknowledge their position but stay firm on your business model
- Keep response to 2-3 sentences, direct and professional"""

        return prompt

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

    def _build_confirmation_request(self) -> str:
        """Build order confirmation request with pricing and delivery details."""
        if not self.selected_item:
            return "Would you like to confirm this order?"

        item = self.selected_item
        price = item.get('price', 'N/A')
        lead_time = item.get('lead_time_days', 'N/A')
        item_id = item.get('id', 'N/A')

        confirmation_text = f"""
---
Would you like to confirm your order?

📋 Order Summary:
• Item: {item_id}
• Unit Price: ${price}
• Lead Time: {lead_time} days
• Reliability: {item.get('reliability', 'N/A')}

Please confirm (YES) or make adjustments (NO)"""
        return confirmation_text

    def _get_order_details(self) -> Dict:
        """Get current order details with pricing and delivery terms."""
        if not self.selected_item:
            return {}

        item = self.selected_item
        return {
            "item_id": item.get('id'),
            "vendor": item.get('vendor'),
            "unit_price": item.get('price'),
            "lead_time_days": item.get('lead_time_days'),
            "reliability": item.get('reliability'),
            "order_confirmed": self.negotiation_state.get("order_confirmed", False)
        }

    def find_competing_products(self) -> List[Dict]:
        """Find competing products from other vendors using semantic search.

        Returns:
            List of competing products
        """
        if not self.catalog or not self.selected_item:
            return []

        competitors = self.catalog.find_competing_products(self.selected_item)
        return competitors[:3]  # Top 3 competitors
