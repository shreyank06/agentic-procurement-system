"""
Mock extension endpoint that simulates an HTTP handler for vendor constraints.

This module provides a deterministic mock endpoint that accepts vendor constraints
and returns updated candidate lists without requiring network access.
"""

from typing import Dict, List, Optional


def apply_vendor_constraints(candidates: List[Dict], constraints: Dict) -> List[Dict]:
    """
    Apply vendor constraints to a candidate list.

    Args:
        candidates: List of candidate items from procurement
        constraints: Dict with vendor constraints, e.g., {"excluded_vendors": [...], "preferred_vendors": [...]}

    Returns:
        Filtered candidate list based on constraints
    """
    if not constraints:
        return candidates

    excluded_vendors = constraints.get("excluded_vendors", [])
    preferred_vendors = constraints.get("preferred_vendors", [])
    min_reliability = constraints.get("min_reliability")
    max_lead_time = constraints.get("max_lead_time")

    filtered = []

    for candidate in candidates:
        vendor = candidate.get("vendor", "")

        # Check excluded vendors
        if vendor in excluded_vendors:
            continue

        # Check reliability constraint
        if min_reliability is not None:
            if candidate.get("reliability", 0) < min_reliability:
                continue

        # Check lead time constraint
        if max_lead_time is not None:
            if candidate.get("lead_time_days", 0) > max_lead_time:
                continue

        filtered.append(candidate)

    # Prioritize preferred vendors by reordering
    if preferred_vendors:
        preferred = [c for c in filtered if c.get("vendor") in preferred_vendors]
        non_preferred = [c for c in filtered if c.get("vendor") not in preferred_vendors]
        filtered = preferred + non_preferred

    return filtered


class MockVendorEndpoint:
    """
    Mock HTTP-like endpoint for vendor constraint updates.
    Simulates an external service without requiring network access.
    """

    def __init__(self):
        """Initialize the mock endpoint."""
        self.request_history = []
        self.constraint_cache = {}

    def post_vendor_constraints(self, request_id: str, candidates: List[Dict], constraints: Dict) -> Dict:
        """
        POST handler that applies vendor constraints and returns updated candidates.

        Args:
            request_id: Unique identifier for the request
            candidates: List of candidate items
            constraints: Vendor constraints to apply

        Returns:
            Response dict with updated candidates and metadata
        """
        # Log request
        self.request_history.append({
            "request_id": request_id,
            "constraints": constraints,
            "timestamp": len(self.request_history)  # Deterministic "timestamp"
        })

        # Apply constraints
        filtered_candidates = apply_vendor_constraints(candidates, constraints)

        # Cache the constraints
        self.constraint_cache[request_id] = constraints

        return {
            "status": "success",
            "request_id": request_id,
            "candidates_before": len(candidates),
            "candidates_after": len(filtered_candidates),
            "candidates": filtered_candidates,
            "constraints_applied": constraints
        }

    def get_constraint_history(self, request_id: str) -> Optional[Dict]:
        """
        GET handler that retrieves constraint history for a request.

        Args:
            request_id: Request identifier

        Returns:
            Constraint dict if found, None otherwise
        """
        return self.constraint_cache.get(request_id)

    def bulk_update_constraints(self, requests: List[Dict]) -> Dict:
        """
        Bulk update handler for multiple requests.

        Args:
            requests: List of dicts with request_id, candidates, and constraints

        Returns:
            Response with results for each request
        """
        results = []
        for req in requests:
            result = self.post_vendor_constraints(
                req.get("request_id"),
                req.get("candidates", []),
                req.get("constraints", {})
            )
            results.append(result)

        return {
            "status": "success",
            "total_requests": len(requests),
            "results": results
        }


# Global endpoint instance for singleton access
_endpoint_instance = None


def get_endpoint() -> MockVendorEndpoint:
    """
    Get the global endpoint instance (singleton pattern).

    Returns:
        MockVendorEndpoint instance
    """
    global _endpoint_instance
    if _endpoint_instance is None:
        _endpoint_instance = MockVendorEndpoint()
    return _endpoint_instance
