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

        msg_lower = user_message.lower()

        # Pattern 1: "X units" or "X unit"
        match = re.search(r'(\d+)\s+units?', msg_lower)
        if match:
            return int(match.group(1))

        # Pattern 2: "buy X" or "want X" or "need X" or "order X"
        match = re.search(r'(?:buy|want|need|order|purchase|commit to)\s+(\d+)', msg_lower)
        if match:
            return int(match.group(1))

        # Pattern 3: "for X" when talking about quantity (e.g., "10% for 15 units")
        match = re.search(r'(?:for|on)\s+(\d+)\s+(?:unit|item)', msg_lower)
        if match:
            return int(match.group(1))

        # Pattern 4: Look back in conversation for most recent quantity mention
        for msg in reversed(conversation):
            msg_text = msg.get('message', '').lower()
            # Look for "X units" pattern
            match = re.search(r'(\d+)\s+units?', msg_text)
            if match:
                qty = int(match.group(1))
                # Skip if this looks like a price calculation (more than 5 digits before "units")
                if qty < 1000:
                    return qty

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
        import re

        price = self.selected_item.get('price', 5200)
        lead_time = self.selected_item.get('lead_time_days', 8)
        discount_pct = int(discount * 100)
        discounted_price = price * (1 - discount)
        total_price = discounted_price * quantity if quantity > 0 else discounted_price

        msg_lower = user_message.lower()

        # Detect different types of questions
        wants_more_discount = any(word in msg_lower for word in ['10%', '12%', '15%', 'more', 'higher', 'better', 'increase', 'can you give', 'can you offer'])
        asking_delivery = any(word in msg_lower for word in ['how many days', 'delivery', 'how long', 'time', 'days', 'when', 'requirement', '6 day', '7 day', '8 day'])
        asking_confirmation = any(word in msg_lower for word in ['is final', 'thats final', 'confirm', 'sure', 'correct'])
        requesting_custom_delivery = any(word in msg_lower for word in ['want', 'need', 'require', 'i want', 'but my requirement', 'in 6', 'in 7', 'in 8', 'in 5'])
        refusing = any(word in msg_lower for word in ['not interested', 'not intersted', 'not intrested', 'no', 'cant', 'cannot', 'refuse', 'sorry', 'too high', 'too expensive'])
        negotiating_surcharge = any(word in msg_lower for word in ['surcharge', '20%', '30%', '40%'])

        # Extract any mentioned number (for delivery days request)
        numbers = re.findall(r'\b(\d+)\s*days?\b', msg_lower)
        requested_days = int(numbers[0]) if numbers else None

        # If asking for confirmation of price - confirm it
        if asking_confirmation and 'delivery' not in msg_lower:
            if last_offer and quantity > 0:
                last_discount = last_offer.get('discount', 0)
                return f"Yes, {last_discount}% off for {quantity} units is our final offer at this volume. Total: ${total_price:,.0f}."
            else:
                return f"Yes, {discount_pct}% is correct for {quantity} units. That brings your total to ${total_price:,.0f}."

        # If requesting custom delivery time
        if requesting_custom_delivery and requested_days:
            if requested_days < lead_time:
                # Customer wants faster than standard
                expedited_days = lead_time - 2
                if requested_days < expedited_days:
                    # Want even faster than expedited - need special handling
                    surcharge = int((lead_time - requested_days) * 5)  # $5 per day expediting fee
                    return f"A {requested_days}-day delivery is aggressive for {quantity} units. I can arrange it for a {surcharge}% surcharge on top of the current pricing."
                else:
                    # Fits within expedited
                    return f"We can accommodate {requested_days} days delivery with our expedited service at a small premium."
            else:
                # Standard or slower is fine
                return f"{requested_days} days works - that's within our standard {lead_time}-day timeline."

        # If negotiating surcharge (after getting surcharge offer)
        if negotiating_surcharge and last_offer:
            last_msg = last_offer.get('message', '')
            # Check if last message mentioned a surcharge
            if 'surcharge' in last_msg:
                # Extract surcharge percentage from last offer
                surcharge_match = re.search(r'(\d+)%\s*surcharge', last_msg)
                if surcharge_match:
                    last_surcharge = int(surcharge_match.group(1))
                    # Try to find requested days from last message or conversation
                    last_days_match = re.search(r'(\d+)-day', last_msg)
                    days_for_delivery = int(last_days_match.group(1)) if last_days_match else requested_days

                    # User is negotiating surcharge down
                    if '20%' in msg_lower and last_surcharge > 20:
                        return f"I can work with 25% surcharge for expedited {days_for_delivery}-day delivery on {quantity} units. That's a fair compromise."
                    elif '30%' in msg_lower and last_surcharge > 30:
                        return f"We can do 35% surcharge for the {days_for_delivery}-day timeline. That's the best I can offer for expedited service."
                    elif 'too high' in msg_lower or 'expensive' in msg_lower:
                        return f"I understand. The minimum I can offer for {days_for_delivery}-day delivery is {max(20, last_surcharge - 10)}% surcharge. Standard {lead_time}-day delivery is complimentary."

        # If asking about delivery/timeline - answer that question
        if asking_delivery and 'price' not in msg_lower and 'discount' not in msg_lower and 'cost' not in msg_lower:
            if quantity > 0:
                return f"For {quantity} units, we offer {lead_time} days standard lead time, or {lead_time - 2} days expedited. What timeline works for you?"
            else:
                return f"Our standard lead time is {lead_time} days for most orders."

        # If last offer exists and same quantity, buyer wants more discount
        if last_offer and quantity > 0:
            last_discount = last_offer.get('discount', 0)
            last_msg = last_offer.get('message', '')

            # Check if we already offered this quantity
            if f"{quantity} units" in last_msg or f"For {quantity}" in last_msg:
                # Same quantity, buyer asking for better discount
                if wants_more_discount and not refusing:
                    # Don't improve, stay firm
                    return f"As stated, {last_discount}% is my best offer for {quantity} units (${total_price:,.0f}). This is firm at this volume."

                # Buyer is refusing the offer
                if refusing:
                    return f"Understood. The best I can do for {quantity} units is {last_discount}% (${total_price:,.0f}). For better pricing, consider ordering {quantity + 25}+ units."

        # Standard offer (no prior offer for this quantity)
        if quantity > 0:
            return f"For {quantity} units, I can offer {discount_pct}% off, bringing the unit price to ${discounted_price:,.0f} and total to ${total_price:,.0f}."
        else:
            return f"I can offer discounts based on volume. What quantity are you interested in?"

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

    def find_competing_products(self) -> List[Dict]:
        """Find competing products from other vendors using semantic search.

        Returns:
            List of competing products
        """
        if not self.catalog or not self.selected_item:
            return []

        competitors = self.catalog.find_competing_products(self.selected_item)
        return competitors[:3]  # Top 3 competitors
