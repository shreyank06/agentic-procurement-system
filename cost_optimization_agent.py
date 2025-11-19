"""
Cost Optimization Agent - Single LLM-powered agent for cost analysis.

Uses LLM to generate contextual, dynamic cost optimization strategies.
"""

import json
import time
from typing import List, Dict, Optional
from llm_adapter import select_llm_provider


class CostOptimizationAgent:
    """Single LLM-powered agent for cost optimization analysis."""

    def __init__(self, llm_provider: str = "mock", api_key: str = None):
        """Initialize the cost optimization agent."""
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = select_llm_provider(llm_provider, api_key)
        self.conversation_history = []

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
        analysis = self.llm.generate(prompt, max_tokens=500)

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

    def chat(self, user_message: str, conversation: List[Dict]) -> Dict:
        """
        Handle user follow-up questions about cost optimization.

        Args:
            user_message: User's question or feedback
            conversation: Current conversation history

        Returns:
            Agent response with updated conversation
        """
        start_time = time.time()

        # Build context from conversation
        context = self._build_chat_context(conversation)

        # Create response prompt
        prompt = f"""You are a cost optimization analyst helping to reduce procurement costs.

Previous discussion:
{context}

User question: {user_message}

Provide a helpful, specific response addressing their question. Consider:
- Vendor negotiation strategies
- Specification relaxation opportunities
- Bulk ordering benefits
- Long-term contract advantages
- Logistics and delivery cost optimization

Keep response concise and actionable."""

        # Get response from LLM
        response = self.llm.generate(prompt, max_tokens=400)

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

        prompt = f"""You are a cost optimization analyst. Analyze the following selected procurement and provide comprehensive cost optimization strategies.

Selected Item:
- ID: {selected_item.get('id')}
- Component: {component}
- Vendor: {vendor}
- Price: ${item_price}
- Lead Time: {lead_time} days
- Reliability: {selected_item.get('reliability', 0.0)}
- Specifications: {specs}

Original Request:
- Max Cost: ${request.get('max_cost', 'Not specified')}
- Delivery Deadline: {request.get('latest_delivery_days', 'Not specified')} days

Please provide:
1. Specific cost reduction opportunities (target 20-40% savings)
2. Vendor negotiation strategies
3. Specification relaxation possibilities
4. Bulk ordering and long-term contract benefits
5. Logistics and delivery optimization
6. Estimated total savings percentage

Be specific and actionable."""

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
