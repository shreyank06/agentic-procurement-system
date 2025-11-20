"""
Cost Optimization Agent - Single LLM-powered agent for cost analysis.

Uses LLM to generate contextual, dynamic cost optimization strategies.
"""

import json
import time
from typing import List, Dict, Optional
from llm_adapter import select_llm_provider


class CostOptimizationAgent:
    """Single LLM-powered agent for cost optimization analysis with semantic search."""

    def __init__(self, llm_provider: str = "mock", api_key: str = None, catalog=None):
        """Initialize the cost optimization agent.

        Args:
            llm_provider: LLM provider to use
            api_key: API key for LLM provider
            catalog: Catalog instance for semantic search and alternatives
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = select_llm_provider(llm_provider, api_key)
        self.conversation_history = []
        self.catalog = catalog

    def analyze_costs(self, selected_item: Dict, request: Dict) -> Dict:
        """
        Analyze and provide cost optimization strategies for the selected item.

        Args:
            selected_item: The selected component from procurement
            request: Original procurement request

        Returns:
            Dict with analysis and cost saving recommendations
        """
        start_time = time.time()

        # Create initial analysis prompt
        prompt = self._build_analysis_prompt(selected_item, request)

        # Get initial analysis from LLM
        analysis = self.llm.generate(prompt, max_tokens=300)

        # Calculate estimated savings
        savings = self._calculate_savings(selected_item)

        result = {
            "selected_item": selected_item,
            "analysis": analysis,
            "estimated_savings": savings,
            "conversation": [
                {
                    "role": "agent",
                    "message": analysis,
                    "timestamp": time.time()
                }
            ],
            "latency": time.time() - start_time
        }

        self.conversation_history.append(("agent", analysis))
        return result

    def chat(self, user_message: str, conversation: List[Dict], selected_item: Dict = None, request: Dict = None) -> Dict:
        """
        Handle user follow-up questions about cost optimization.

        Args:
            user_message: User's question or feedback
            conversation: Current conversation history
            selected_item: The selected component (for context)
            request: Original procurement request (for context)

        Returns:
            Agent response with updated conversation
        """
        start_time = time.time()

        # Build context from conversation
        context = self._build_chat_context(conversation)

        # Build item context if available
        item_context = ""
        if selected_item:
            item_context = f"""
Selected Item Context:
- ID: {selected_item.get('id', 'Unknown')}
- Vendor: {selected_item.get('vendor', 'Unknown')}
- Current Price: ${selected_item.get('price', 0)}
- Lead Time: {selected_item.get('lead_time_days', 0)} days
- Reliability: {selected_item.get('reliability', 0)}
"""

        # Create response prompt
        prompt = f"""You are a cost optimization analyst. Answer the user's question CONCISELY in 2-3 sentences.

{item_context}

Previous Discussion:
{context}

User's Question: {user_message}

Rules:
- Be flexible and practical, not rigid
- Adjust recommendations based on actual quantity mentioned by buyer
- Provide realistic discount estimates (typical ranges: 2-5% for small orders, 5-10% for larger)
- If they ask about a specific quantity, calculate discount for THAT quantity, don't contradict earlier advice
- Be helpful and give actionable answers, not "you need 100 units"
- Short, direct answer with specific numbers."""

        # Get response from LLM
        response = self.llm.generate(prompt, max_tokens=250)

        result = {
            "role": "agent",
            "message": response,
            "timestamp": time.time(),
            "latency": time.time() - start_time
        }

        return result

    def _build_analysis_prompt(self, selected_item: Dict, request: Dict) -> str:
        """Build the initial cost analysis prompt."""
        item_price = selected_item.get("price", 0)
        vendor = selected_item.get("vendor", "Unknown")
        component = selected_item.get("component", "component")
        lead_time = selected_item.get("lead_time_days", 0)
        specs = json.dumps(selected_item.get("specs", {}), indent=2)

        prompt = f"""You are a cost optimization analyst. Provide CONCISE cost reduction strategies for this procurement.

Item: {component} ({selected_item.get('id')}) from {vendor}
Price: ${item_price}, Lead: {lead_time} days, Reliability: {selected_item.get('reliability', 0.0)}

Provide a SHORT list (3-5 actionable strategies) with realistic numbers:
- Be practical: suggest discounts for typical quantities (5, 10, 25, 50 units)
- Don't require unrealistic minimums
- Focus on what's achievable for a buyer
- Use realistic discount ranges: 2-5% small orders, 5-15% large orders
No lengthy explanations."""

        return prompt

    def _build_chat_context(self, conversation: List[Dict]) -> str:
        """Build context string from conversation history."""
        context_lines = []
        for msg in conversation:
            role = "User" if msg.get("role") == "user" else "Agent"
            context_lines.append(f"{role}: {msg.get('message', '')}")
        return "\n".join(context_lines)

    def _calculate_savings(self, selected_item: Dict) -> Dict:
        """Calculate potential cost savings estimates."""
        item_price = selected_item.get("price", 0)

        return {
            "current_cost": item_price,
            "vendor_negotiation_savings": round(item_price * 0.15, 2),
            "spec_relaxation_savings": round(item_price * 0.20, 2),
            "bulk_ordering_savings": round(item_price * 0.10, 2),
            "logistics_savings": round(item_price * 0.08, 2),
            "total_potential_savings": round(item_price * 0.50, 2),
            "cost_after_optimization": round(item_price * 0.50, 2),
            "savings_percentage": 50
        }

    def find_cheaper_alternatives(self, selected_item: Dict) -> List[Dict]:
        """Find semantically similar items that are cheaper using catalog.

        Args:
            selected_item: The selected component

        Returns:
            List of cheaper alternatives
        """
        if not self.catalog:
            return []

        alternatives = self.catalog.find_cheaper_alternatives(selected_item)
        return alternatives[:3]  # Top 3 alternatives
