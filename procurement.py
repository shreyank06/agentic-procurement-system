"""
Procurement Agent - Core orchestration module.

This module provides the main agent orchestration, scoring functions, tool implementations,
and optional LangGraph-based workflow. It handles catalog search, candidate scoring and ranking,
tool invocations for extended research, and LLM-based justification generation.

Key exports:
  - plan_procurement(): Main agent function for procurement planning
  - negotiate_procurement(): Multi-agent negotiation simulation
  - run_flow(): LangGraph orchestration with fallback
  - compute_score(): Candidate scoring function
  - price_history_tool(), availability_tool(): Deterministic tool implementations
"""

import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Union
from catalog import Catalog
from llm_adapter import LLMAdapter, MockLLM, select_llm_provider


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def compute_score(item: dict, request: dict, price_min: float, price_max: float, lead_min: int, lead_max: int) -> float:
    """
    Compute a normalized score for an item based on price, lead time, and reliability.

    Args:
        item: Catalog item dict containing price, lead_time_days, and reliability
        request: Request dict that may contain "weights" mapping criteria to weights
        price_min: Minimum price across the candidate set
        price_max: Maximum price across the candidate set
        lead_min: Minimum lead time across the candidate set
        lead_max: Maximum lead time across the candidate set

    Returns:
        Float score in [0, 1] range
    """
    # Default weights
    default_weights = {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
    weights = request.get("weights", default_weights)

    # Extract item values
    price = item.get("price", 0)
    lead_time = item.get("lead_time_days", 0)
    reliability = item.get("reliability", 0)

    # Normalize price (lower is better, so invert)
    if price_max == price_min:
        normalized_price = 1.0
    else:
        normalized_price = 1 - (price - price_min) / (price_max - price_min)
    normalized_price = max(0.0, min(1.0, normalized_price))

    # Normalize lead time (lower is better, so invert)
    if lead_max == lead_min:
        normalized_lead_time = 1.0
    else:
        normalized_lead_time = 1 - (lead_time - lead_min) / (lead_max - lead_min)
    normalized_lead_time = max(0.0, min(1.0, normalized_lead_time))

    # Calculate weighted score
    score = (
        weights.get("price", default_weights["price"]) * normalized_price +
        weights.get("lead_time", default_weights["lead_time"]) * normalized_lead_time +
        weights.get("reliability", default_weights["reliability"]) * reliability
    )

    return max(0.0, min(1.0, score))


# ============================================================================
# TOOL FUNCTIONS
# ============================================================================

def price_history_tool(item_id: str) -> dict:
    """
    Return deterministic price history for an item.

    Args:
        item_id: The item ID (e.g., "SP-100")

    Returns:
        Dict containing item_id and history with date/price pairs
    """
    # Use hash of item_id to generate deterministic base price
    hash_val = int(hashlib.md5(item_id.encode()).hexdigest(), 16)
    random.seed(hash_val)

    # Generate base price from hash
    base_price = 1000 + (hash_val % 10000)

    # Generate 4 historical data points
    history = []
    current_date = datetime.now()

    for i in range(4):
        # Go back in time
        date = current_date - timedelta(days=30 * (4 - i))
        # Add some variation
        price_variation = random.randint(-200, 200)
        price = base_price + price_variation

        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price
        })

    # Reset random seed to avoid affecting other code
    random.seed()

    return {
        "item_id": item_id,
        "history": history
    }


def availability_tool(vendor: str) -> dict:
    """
    Return deterministic availability information for a vendor.

    Args:
        vendor: The vendor name (e.g., "Helios Dynamics")

    Returns:
        Dict containing vendor, avg_lead_time_days, in_stock, and lead_time_samples
    """
    # Use hash of vendor name to generate deterministic values
    hash_val = int(hashlib.md5(vendor.encode()).hexdigest(), 16)
    random.seed(hash_val)

    # Generate deterministic values
    avg_lead_time_days = 10 + (hash_val % 30)  # Between 10 and 40 days
    in_stock = (hash_val % 2) == 0  # Deterministically true or false

    # Generate 3 lead time samples
    lead_time_samples = []
    for i in range(3):
        sample = avg_lead_time_days + random.randint(-5, 5)
        lead_time_samples.append(max(1, sample))  # Ensure positive

    # Reset random seed
    random.seed()

    return {
        "vendor": vendor,
        "avg_lead_time_days": float(avg_lead_time_days),
        "in_stock": in_stock,
        "lead_time_samples": lead_time_samples
    }


def plan_procurement(request: dict, top_k: int = 3, investigate: bool = False, llm_provider: str = "mock", api_key: str = None) -> dict:
    """
    Plan procurement by searching catalog, scoring candidates, and generating justification.

    Args:
        request: Request dict with component, spec_filters, max_cost, latest_delivery_days, weights
        top_k: Number of top candidates to return
        investigate: Whether to call investigation tools
        llm_provider: LLM provider to use for justification

    Returns:
        Result dict with request, candidates, selected, justification, trace, and metrics
    """
    # Initialize trace and metrics
    trace = []
    metrics = {
        "step_latencies": {},
        "total_candidates": 0,
        "candidates_after_filtering": 0,
        "top_k_selected": 0,
        "tools_called": 0,
        "total_latency": 0.0
    }
    start_time = time.time()

    # Step 1: Load catalog and search
    step_start = time.time()
    try:
        catalog = Catalog("catalog.json")
        metrics["step_latencies"]["catalog_load"] = time.time() - step_start
        trace.append({"step": "catalog_load", "status": "success"})
    except Exception as e:
        metrics["total_latency"] = time.time() - start_time
        return {"error": f"failed to load catalog: {str(e)}", "status": 500, "metrics": metrics}

    component = request.get("component")
    spec_filters = request.get("spec_filters")

    if not component:
        metrics["total_latency"] = time.time() - start_time
        return {"error": "no component specified", "status": 400, "metrics": metrics}

    # Search for candidates
    step_start = time.time()
    candidates = catalog.search(component, spec_filters)
    metrics["step_latencies"]["catalog_search"] = time.time() - step_start
    metrics["total_candidates"] = len(candidates)

    trace.append({
        "step": "catalog_search",
        "input": {"component": component, "spec_filters": spec_filters},
        "result": f"found {len(candidates)} candidates"
    })

    # Step 2: Apply hard constraints (max_cost, latest_delivery_days)
    initial_count = len(candidates)
    max_cost = request.get("max_cost")
    latest_delivery = request.get("latest_delivery_days")

    if max_cost is not None:
        candidates = [c for c in candidates if c.get("price", float('inf')) <= max_cost]
    if latest_delivery is not None:
        candidates = [c for c in candidates if c.get("lead_time_days", float('inf')) <= latest_delivery]

    if initial_count > len(candidates):
        trace.append({
            "step": "constraint_filtering",
            "input": {"max_cost": max_cost, "latest_delivery_days": latest_delivery},
            "result": f"filtered from {initial_count} to {len(candidates)} candidates"
        })

    # Step 3: Check if candidates found
    if not candidates:
        metrics["total_latency"] = time.time() - start_time
        return {"error": "no candidates match constraints", "status": 404, "trace": trace, "metrics": metrics}

    # Step 3: Compute min/max for normalization
    step_start = time.time()
    prices = [item.get("price", 0) for item in candidates]
    lead_times = [item.get("lead_time_days", 0) for item in candidates]

    price_min = min(prices)
    price_max = max(prices)
    lead_min = min(lead_times)
    lead_max = max(lead_times)

    trace.append({
        "step": "compute_bounds",
        "result": f"price: [{price_min}, {price_max}], lead_time: [{lead_min}, {lead_max}]"
    })

    # Step 4: Score each candidate
    for candidate in candidates:
        score = compute_score(candidate, request, price_min, price_max, lead_min, lead_max)
        candidate["score"] = score

    metrics["step_latencies"]["scoring"] = time.time() - step_start
    metrics["candidates_after_filtering"] = len(candidates)

    trace.append({
        "step": "scoring",
        "result": f"scored {len(candidates)} candidates"
    })

    # Step 5: Sort by score and get top_k
    candidates_sorted = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
    top_candidates = candidates_sorted[:top_k]
    metrics["top_k_selected"] = len(top_candidates)

    trace.append({
        "step": "ranking",
        "result": f"selected top {len(top_candidates)} candidates"
    })

    # Step 6: Investigate if requested
    step_start = time.time()
    if investigate:
        for candidate in top_candidates:
            # Call price history tool
            price_history = price_history_tool(candidate["id"])
            metrics["tools_called"] += 1
            trace.append({
                "step": "tool_call",
                "tool": "price_history",
                "input": candidate["id"],
                "summary": f"last price={price_history['history'][-1]['price']}; trend=stable"
            })

            # Call availability tool
            availability = availability_tool(candidate["vendor"])
            metrics["tools_called"] += 1
            trace.append({
                "step": "tool_call",
                "tool": "availability",
                "input": candidate["vendor"],
                "summary": f"avg_lead={availability['avg_lead_time_days']} days; in_stock={availability['in_stock']}"
            })

            # Attach tool results to candidate
            candidate["tools"] = {
                "price_history": price_history,
                "availability": availability
            }

        metrics["step_latencies"]["investigation"] = time.time() - step_start
        trace.append({
            "step": "investigation",
            "result": f"called tools for {len(top_candidates)} candidates"
        })

    # Step 7: Get the selected (top) candidate
    selected = top_candidates[0] if top_candidates else None

    if not selected:
        metrics["total_latency"] = time.time() - start_time
        return {"error": "no candidates after ranking", "status": 404, "trace": trace, "metrics": metrics}

    # Step 8: Generate justification using LLM
    step_start = time.time()
    llm = select_llm_provider(llm_provider, api_key=api_key)

    # Check if LLM provider returned None (API key required)
    if llm is None:
        metrics["total_latency"] = time.time() - start_time
        return {
            "error": f"API key required for {llm_provider}. Please provide an API key.",
            "status": 400,
            "trace": trace,
            "metrics": metrics
        }

    # Create prompt for LLM
    prompt = f"""Selected item details:
ID: {selected['id']}
Vendor: {selected['vendor']}
Price: {selected['price']}
Lead Time: {selected['lead_time_days']} days
Reliability: {selected['reliability']}

Request constraints:
Max Cost: {request.get('max_cost', 'N/A')}
Latest Delivery: {request.get('latest_delivery_days', 'N/A')} days

Please provide a brief justification (2-3 sentences) for why this item is the best choice.
"""

    justification = llm.generate(prompt, max_tokens=150)
    metrics["step_latencies"]["llm_justification"] = time.time() - step_start

    trace.append({
        "step": "llm_justification",
        "result": "generated justification"
    })

    # Step 9: Calculate final metrics
    metrics["total_latency"] = time.time() - start_time

    # Step 10: Build and return result
    return {
        "request": request,
        "candidates": top_candidates,
        "selected": selected,
        "justification": justification,
        "trace": trace,
        "metrics": metrics
    }


def negotiate_procurement(selected_item: dict, request: dict) -> Dict:
    """
    Simulate a deterministic negotiation between procurement agent and procurement officer.

    Args:
        selected_item: The selected item from procurement
        request: The original request

    Returns:
        Dict with negotiation transcript and final verdict
    """
    negotiation_transcript = []
    vendor = selected_item.get("vendor", "Unknown")
    price = selected_item.get("price", 0)
    item_id = selected_item.get("id", "Unknown")
    max_cost = request.get("max_cost", float('inf'))

    # Agent proposes the selection
    agent_message = f"Agent: I recommend {item_id} from {vendor} at ${price}. It has the best overall score considering price, lead time, and reliability."
    negotiation_transcript.append(agent_message)

    # Officer's initial response
    if price <= max_cost * 0.8:
        officer_response = f"Officer: Excellent choice. Price of ${price} is well within budget (max: ${max_cost}). This gives us good cost flexibility."
        verdict = "APPROVED"
        negotiation_transcript.append(officer_response)
    elif price <= max_cost:
        officer_response = f"Officer: The price of ${price} is at the edge of our budget (max: ${max_cost}). Can you verify reliability meets mission-critical needs?"
        agent_justification = f"Agent: Reliability of {selected_item.get('reliability', 0)} is among the best available for this component. Lead time of {selected_item.get('lead_time_days', 0)} days also allows buffer."
        verdict = "APPROVED_WITH_CONDITIONS"
        negotiation_transcript.append(officer_response)
        negotiation_transcript.append(agent_justification)
    else:
        officer_response = f"Officer: Price of ${price} exceeds budget (max: ${max_cost}). This requires executive approval or we need to reconsider alternatives."
        verdict = "ESCALATED"
        negotiation_transcript.append(officer_response)

    # Final approval statement
    final_statement = f"Officer: Procurement decision for {item_id} is {verdict}."
    negotiation_transcript.append(final_statement)

    return {
        "transcript": negotiation_transcript,
        "verdict": verdict,
        "item_id": item_id,
        "vendor": vendor,
        "price": price
    }


def run_flow(request: dict, investigate: bool = False, llm: LLMAdapter = None, top_k: int = 3) -> dict:
    """
    Run the procurement flow with optional LangGraph integration.
    Falls back to plan_procurement if LangGraph is not available.

    Args:
        request: Request dict
        investigate: Whether to investigate with tools
        llm: LLM adapter instance (optional)
        top_k: Number of top candidates

    Returns:
        Result dict matching plan_procurement output
    """
    # Check if langgraph is available
    try:
        from langgraph.graph import StateGraph
        from typing_extensions import TypedDict

        # Define state schema
        class ProcurementState(TypedDict):
            """Typed state dictionary for LangGraph procurement workflow.

            Contains all state needed to flow through the 4-node procurement graph:
            catalog search, scoring, tool invocation, and LLM justification.
            """
            request: dict
            candidates: list
            top_candidates: list
            selected: dict
            justification: str
            trace: list
            metrics: dict
            price_min: float
            price_max: float
            lead_min: float
            lead_max: float
            investigate: bool
            top_k: int

        # Node A: Catalog search
        def node_catalog_search(state: ProcurementState) -> ProcurementState:
            """Search catalog for candidates matching component and spec filters.

            Computes price and lead_time bounds across all candidates for later normalization.
            """
            catalog = Catalog("catalog.json")
            component = state["request"].get("component")
            spec_filters = state["request"].get("spec_filters")

            candidates = catalog.search(component, spec_filters)
            state["candidates"] = candidates

            if candidates:
                prices = [item.get("price", 0) for item in candidates]
                lead_times = [item.get("lead_time_days", 0) for item in candidates]
                state["price_min"] = min(prices)
                state["price_max"] = max(prices)
                state["lead_min"] = min(lead_times)
                state["lead_max"] = max(lead_times)

            return state

        # Node B: Scoring
        def node_scoring(state: ProcurementState) -> ProcurementState:
            """Score all candidates and select top-k based on weighted scoring.

            Normalizes price and lead_time, applies weights (price, lead_time, reliability).
            """
            for candidate in state["candidates"]:
                score = compute_score(
                    candidate,
                    state["request"],
                    state["price_min"],
                    state["price_max"],
                    state["lead_min"],
                    state["lead_max"]
                )
                candidate["score"] = score

            candidates_sorted = sorted(state["candidates"], key=lambda x: x.get("score", 0), reverse=True)
            state["top_candidates"] = candidates_sorted[:state["top_k"]]
            state["selected"] = state["top_candidates"][0] if state["top_candidates"] else None

            return state

        # Node C: Conditional tools
        def node_tools(state: ProcurementState) -> ProcurementState:
            """Call tools (price_history, availability) if investigation enabled.

            Attaches tool results to top candidates for extended analysis.
            """
            if state["investigate"] and state["top_candidates"]:
                for candidate in state["top_candidates"]:
                    price_history = price_history_tool(candidate["id"])
                    availability = availability_tool(candidate["vendor"])
                    candidate["tools"] = {
                        "price_history": price_history,
                        "availability": availability
                    }

            return state

        # Node D: LLM Justification
        def node_llm(state: ProcurementState) -> ProcurementState:
            """Generate natural language justification for selected candidate using LLM.

            Uses pluggable LLM adapter (MockLLM by default).
            """
            if state["selected"]:
                llm_adapter = llm if llm else select_llm_provider("mock")

                prompt = f"""Selected item details:
ID: {state['selected']['id']}
Vendor: {state['selected']['vendor']}
Price: {state['selected']['price']}
Lead Time: {state['selected']['lead_time_days']} days
Reliability: {state['selected']['reliability']}

Request constraints:
Max Cost: {state['request'].get('max_cost', 'N/A')}
Latest Delivery: {state['request'].get('latest_delivery_days', 'N/A')} days

Please provide a brief justification (2-3 sentences) for why this item is the best choice.
"""
                state["justification"] = llm_adapter.generate(prompt, max_tokens=150)

            return state

        # Build graph
        graph = StateGraph(ProcurementState)
        graph.add_node("catalog_search", node_catalog_search)
        graph.add_node("scoring", node_scoring)
        graph.add_node("tools", node_tools)
        graph.add_node("llm", node_llm)

        # Add edges
        graph.add_edge("catalog_search", "scoring")
        graph.add_edge("scoring", "tools")
        graph.add_edge("tools", "llm")
        graph.set_entry_point("catalog_search")
        graph.set_finish_point("llm")

        # Compile and run
        app = graph.compile()

        initial_state = {
            "request": request,
            "candidates": [],
            "top_candidates": [],
            "selected": None,
            "justification": "",
            "trace": [],
            "metrics": {
                "step_latencies": {},
                "total_candidates": 0,
                "candidates_after_filtering": 0,
                "top_k_selected": 0,
                "tools_called": 0,
                "total_latency": 0.0
            },
            "price_min": 0,
            "price_max": 0,
            "lead_min": 0,
            "lead_max": 0,
            "investigate": investigate,
            "top_k": top_k
        }

        result_state = app.invoke(initial_state)

        # Convert to plan_procurement output format
        return {
            "request": result_state["request"],
            "candidates": result_state["top_candidates"],
            "selected": result_state["selected"],
            "justification": result_state["justification"],
            "trace": result_state["trace"],
            "metrics": result_state["metrics"]
        }

    except ImportError:
        # LangGraph not available, fall back to synchronous implementation
        llm_provider = "mock" if llm is None else "mock"
        return plan_procurement(request, top_k=top_k, investigate=investigate, llm_provider=llm_provider)
