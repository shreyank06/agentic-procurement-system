#!/usr/bin/env python3
"""
Minimal CLI for procurement agent.

Usage:
    python cli.py <request_file.json> [--investigate] [--top-k N] [--negotiate] [--metrics] [--constraints-file FILE]

Example:
    python cli.py example_request.json --investigate --top-k 3 --negotiate --metrics
"""

import sys
import json
import argparse
from backend.core.procurement import plan_procurement, negotiate_procurement
from extension_endpoint import apply_vendor_constraints


def main():
    """Main CLI entrypoint for procurement agent.

    Parses command-line arguments, loads request from JSON file, runs procurement
    planning, optionally runs investigation tools and negotiation, and displays results
    including metrics and execution trace.
    """
    parser = argparse.ArgumentParser(description="Procurement Agent CLI")
    parser.add_argument("request_file", help="Path to request JSON file")
    parser.add_argument("--investigate", action="store_true", help="Enable tool investigation")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top candidates (default: 3)")
    parser.add_argument("--llm-provider", type=str, default="mock", help="LLM provider (default: mock)")
    parser.add_argument("--negotiate", action="store_true", help="Enable multi-agent negotiation")
    parser.add_argument("--metrics", action="store_true", help="Display performance metrics")
    parser.add_argument("--constraints-file", type=str, help="Path to vendor constraints JSON file")

    args = parser.parse_args()

    # Read request from file
    try:
        with open(args.request_file, 'r') as f:
            request = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{args.request_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.request_file}': {e}")
        sys.exit(1)

    # Get vendor constraints from request or constraints file
    vendor_constraints = request.get("vendor_constraints")

    # Override with constraints file if provided
    if args.constraints_file:
        try:
            with open(args.constraints_file, 'r') as f:
                vendor_constraints = json.load(f)
        except FileNotFoundError:
            print(f"Error: Constraints file '{args.constraints_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.constraints_file}': {e}")
            sys.exit(1)

    # Run procurement
    print(f"\n{'='*60}")
    print(f"Running Procurement Agent")
    print(f"{'='*60}\n")

    result = plan_procurement(
        request,
        top_k=args.top_k,
        investigate=args.investigate,
        llm_provider=args.llm_provider
    )

    # Check for errors
    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    # Print results in readable format
    print(f"Request:")
    print(f"  Component: {result['request'].get('component')}")
    print(f"  Spec Filters: {result['request'].get('spec_filters')}")
    print(f"  Max Cost: {result['request'].get('max_cost')}")
    print(f"  Latest Delivery: {result['request'].get('latest_delivery_days')} days")
    print()

    # Show candidates before constraints
    candidates_before = result['candidates']
    print(f"Candidates Found (before constraints): {len(candidates_before)}\n")

    for i, candidate in enumerate(candidates_before, 1):
        print(f"  {i}. {candidate['id']} - {candidate['vendor']} (reliability: {candidate['reliability']}, lead_time: {candidate['lead_time_days']}d)")
    print()

    # Apply vendor constraints if provided
    candidates = candidates_before
    if vendor_constraints:
        print(f"Applying Vendor Constraints:")
        print(f"  {vendor_constraints}")
        candidates = apply_vendor_constraints(candidates, vendor_constraints)
        print(f"Candidates after filtering: {len(candidates)}\n")
    else:
        print(f"Candidates to select from: {len(candidates)}\n")

    for i, candidate in enumerate(candidates, 1):
        print(f"Candidate {i}: {candidate['id']}")
        print(f"  Vendor: {candidate['vendor']}")
        print(f"  Price: ${candidate['price']}")
        print(f"  Lead Time: {candidate['lead_time_days']} days")
        print(f"  Reliability: {candidate['reliability']}")
        print(f"  Score: {candidate['score']:.4f}")

        if 'tools' in candidate:
            print(f"  Tools Data:")
            if 'price_history' in candidate['tools']:
                ph = candidate['tools']['price_history']
                last_price = ph['history'][-1]['price']
                print(f"    Price History: Last price = ${last_price}")
            if 'availability' in candidate['tools']:
                av = candidate['tools']['availability']
                print(f"    Availability: Avg lead time = {av['avg_lead_time_days']} days, In stock = {av['in_stock']}")
        print()

    print(f"{'='*60}")
    print(f"SELECTED: {result['selected']['id']}")
    print(f"{'='*60}")
    print()

    print(f"Justification:")
    print(f"{result['justification']}")
    print()

    # Display metrics if requested
    if args.metrics and "metrics" in result:
        print(f"{'='*60}")
        print(f"Performance Metrics")
        print(f"{'='*60}")
        metrics = result['metrics']
        print(f"Total Latency: {metrics['total_latency']:.4f}s")
        print(f"Total Candidates: {metrics['total_candidates']}")
        print(f"Candidates After Filtering: {metrics['candidates_after_filtering']}")
        print(f"Top K Selected: {metrics['top_k_selected']}")
        print(f"Tools Called: {metrics['tools_called']}")
        print(f"\nStep Latencies:")
        for step, latency in metrics['step_latencies'].items():
            print(f"  {step}: {latency:.4f}s")
        print()

    # Run negotiation if requested
    if args.negotiate:
        print(f"{'='*60}")
        print(f"Multi-Agent Negotiation")
        print(f"{'='*60}\n")
        negotiation = negotiate_procurement(result['selected'], request)
        print(f"Negotiation Transcript:")
        for msg in negotiation['transcript']:
            print(f"  {msg}")
        print(f"\nNegotiation Verdict: {negotiation['verdict']}\n")

    print(f"Trace ({len(result['trace'])} steps):")
    for step in result['trace']:
        if step.get('step') == 'tool_call':
            print(f"  - {step['tool']}: {step.get('summary', '')}")
        else:
            print(f"  - {step.get('step')}: {step.get('result', step.get('status', ''))}")
    print()


if __name__ == "__main__":
    main()
