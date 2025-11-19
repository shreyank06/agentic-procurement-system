"""
Cost Optimization Multi-Agent Chat Module.

Simulates a multi-agent discussion for cost optimization strategies.
Agents: Cost Analyst, Supply Chain Manager, Requirements Engineer, Logistics Officer
"""

import json
import time
from typing import List, Dict, Optional
from llm_adapter import select_llm_provider


class CostOptimizer:
    """Multi-agent cost optimization discussion."""

    def __init__(self, llm_provider: str = "mock", api_key: str = None):
        """Initialize the cost optimizer with an LLM provider."""
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.llm = select_llm_provider(llm_provider, api_key)
        self.agents = {
            "cost_analyst": "Cost Analyst - Finds cheaper alternatives and identifies price opportunities",
            "supply_chain": "Supply Chain Manager - Proposes bulk deals, long-term contracts, vendor negotiations",
            "requirements": "Requirements Engineer - Questions if specs can be relaxed to save costs",
            "logistics": "Logistics Officer - Optimizes delivery strategy to reduce expediting costs"
        }

    def generate_strategy(self, agent_name: str, selected_item: Dict, request: Dict, context: str) -> str:
        """Generate a cost optimization strategy from a specific agent."""

        strategies = {
            "cost_analyst": self._cost_analyst_strategy,
            "supply_chain": self._supply_chain_strategy,
            "requirements": self._requirements_strategy,
            "logistics": self._logistics_strategy
        }

        if agent_name in strategies:
            return strategies[agent_name](selected_item, request, context)
        return "Unable to generate strategy."

    def _cost_analyst_strategy(self, selected_item: Dict, request: Dict, context: str) -> str:
        """Cost Analyst strategy: Find cheaper alternatives."""
        item_price = selected_item.get("price", 0)
        potential_savings = item_price * 0.15  # Estimate 15% savings potential

        strategy = f"I've analyzed the pricing. The current selection at ${item_price} shows potential for {potential_savings:.0f}$ in savings. "
        strategy += f"I recommend comparing with at least 2-3 other vendors to leverage competitive pricing. "
        strategy += f"If we negotiate volume discounts (10+ units), we could reduce the unit cost by 10-20%."

        return strategy

    def _supply_chain_strategy(self, selected_item: Dict, request: Dict, context: str) -> str:
        """Supply Chain Manager strategy: Bulk deals and contracts."""
        vendor = selected_item.get("vendor", "Unknown")
        component = selected_item.get("component", "unknown")

        strategy = f"From a supply chain perspective, {vendor} is a reliable partner for {component}. "
        strategy += f"I propose a long-term supply agreement for 50+ units over 12 months, "
        strategy += f"which typically yields 15-25% volume discounts. Additionally, we should consolidate "
        strategy += f"our orders with this vendor to get preferred pricing on complementary components."

        return strategy

    def _requirements_strategy(self, selected_item: Dict, request: Dict, context: str) -> str:
        """Requirements Engineer strategy: Relax specs to save costs."""
        specs = selected_item.get("specs", {})
        component = selected_item.get("component", "component")

        strategy = f"Let me challenge the specifications. For {component}, do we really need all the specs we defined? "
        strategy += f"Current specs: {json.dumps(specs)}. "
        strategy += f"I suggest revisiting the 'nice-to-have' requirements. Relaxing any non-critical spec by 10-15% "
        strategy += f"could open up cheaper alternatives from tier-2 vendors at 20-30% lower cost."

        return strategy

    def _logistics_strategy(self, selected_item: Dict, request: Dict, context: str) -> str:
        """Logistics Officer strategy: Optimize delivery."""
        lead_time = selected_item.get("lead_time_days", 0)
        max_delivery = request.get("latest_delivery_days", 999)

        strategy = f"On the logistics side, the current {lead_time}-day lead time is within our {max_delivery}-day requirement. "
        strategy += f"However, if we relax the deadline to {lead_time + 10} days, we can shift to economy shipping and "
        strategy += f"consolidate shipments, saving approximately 8-12% on logistics costs. "
        strategy += f"Alternatively, we could negotiate free expedited shipping with volume commitments."

        return strategy

    def optimize(self, selected_item: Dict, request: Dict, top_k: int = 3) -> Dict:
        """
        Run multi-agent cost optimization discussion.

        Args:
            selected_item: The selected component from procurement
            request: Original procurement request
            top_k: Number of agents to include in discussion

        Returns:
            Dict with discussion history and recommendations
        """
        discussion = []
        start_time = time.time()

        # Start with cost analyst
        cost_analysis = self.generate_strategy(
            "cost_analyst",
            selected_item,
            request,
            ""
        )
        discussion.append({
            "agent": "Cost Analyst",
            "role": self.agents["cost_analyst"],
            "message": cost_analysis,
            "timestamp": time.time()
        })

        # Supply chain response
        supply_chain_response = self.generate_strategy(
            "supply_chain",
            selected_item,
            request,
            cost_analysis
        )
        discussion.append({
            "agent": "Supply Chain Manager",
            "role": self.agents["supply_chain"],
            "message": supply_chain_response,
            "timestamp": time.time()
        })

        # Requirements response
        requirements_response = self.generate_strategy(
            "requirements",
            selected_item,
            request,
            supply_chain_response
        )
        discussion.append({
            "agent": "Requirements Engineer",
            "role": self.agents["requirements"],
            "message": requirements_response,
            "timestamp": time.time()
        })

        # Logistics response
        logistics_response = self.generate_strategy(
            "logistics",
            selected_item,
            request,
            requirements_response
        )
        discussion.append({
            "agent": "Logistics Officer",
            "role": self.agents["logistics"],
            "message": logistics_response,
            "timestamp": time.time()
        })

        # Generate summary recommendation
        summary = self._generate_summary(selected_item, discussion)
        discussion.append({
            "agent": "Optimization Summary",
            "role": "Multi-Agent Consensus",
            "message": summary,
            "timestamp": time.time()
        })

        return {
            "selected_item": selected_item,
            "discussion": discussion,
            "total_latency": time.time() - start_time,
            "estimated_savings": self._calculate_savings(selected_item)
        }

    def _generate_summary(self, selected_item: Dict, discussion: List[Dict]) -> str:
        """Generate a summary of cost optimization opportunities."""
        item_price = selected_item.get("price", 0)

        summary = f"Based on our multi-agent analysis for {selected_item.get('id')} (${item_price}), "
        summary += f"we've identified the following cost optimization opportunities:\n\n"
        summary += f"1. Vendor negotiation & volume discounts: 15-25% savings potential\n"
        summary += f"2. Specification relaxation: 20-30% cost reduction via alternative vendors\n"
        summary += f"3. Logistics optimization: 8-12% savings on delivery costs\n"
        summary += f"4. Long-term supply agreements: 15-25% annual savings\n\n"
        summary += f"Recommended action: Negotiate with current vendor for volume discounts while evaluating "
        summary += f"alternative vendors that meet relaxed specifications."

        return summary

    def _calculate_savings(self, selected_item: Dict) -> Dict:
        """Calculate potential cost savings."""
        item_price = selected_item.get("price", 0)

        return {
            "current_cost": item_price,
            "vendor_negotiation_savings": round(item_price * 0.20, 2),
            "spec_relaxation_savings": round(item_price * 0.25, 2),
            "logistics_savings": round(item_price * 0.10, 2),
            "total_potential_savings": round(item_price * 0.55, 2),
            "cost_after_optimization": round(item_price * 0.45, 2)
        }
