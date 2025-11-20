"""
Tests for bonus features:
- Semantic search
- Metrics and observability
- Mock extension endpoint
- Multi-agent negotiation
"""

import pytest
from backend.core.catalog import Catalog
from backend.core.procurement import plan_procurement, negotiate_procurement, price_history_tool, availability_tool
from extension_endpoint import MockVendorEndpoint, apply_vendor_constraints, get_endpoint


class TestSemanticSearch:
    """Test semantic search functionality in Catalog."""

    def test_search_semantic_basic(self):
        """Test basic semantic search."""
        catalog = Catalog("catalog.json")
        results = catalog.search_semantic("solar power", top_k=3)

        assert len(results) > 0
        assert len(results) <= 3
        for item in results:
            assert "id" in item
            assert "component" in item

    def test_search_semantic_deterministic(self):
        """Test that semantic search is deterministic."""
        catalog = Catalog("catalog.json")
        results1 = catalog.search_semantic("battery capacity", top_k=2)
        results2 = catalog.search_semantic("battery capacity", top_k=2)

        # Should return same items in same order
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1["id"] == r2["id"]

    def test_search_semantic_returns_items(self):
        """Test that semantic search returns valid items."""
        catalog = Catalog("catalog.json")
        results = catalog.search_semantic("thruster engine", top_k=5)

        assert len(results) <= 5
        for item in results:
            assert "id" in item
            assert "vendor" in item
            assert "price" in item


class TestMetricsAndObservability:
    """Test metrics and observability features."""

    def test_plan_procurement_includes_metrics(self):
        """Test that plan_procurement returns metrics."""
        request = {
            "component": "solar_panel",
            "spec_filters": {"power_w": 140},
            "max_cost": 6000,
            "latest_delivery_days": 30,
            "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
        }

        result = plan_procurement(request, top_k=2, investigate=False)

        # Check metrics are included
        assert "metrics" in result
        metrics = result["metrics"]

        # Check required metrics
        assert "step_latencies" in metrics
        assert "total_candidates" in metrics
        assert "candidates_after_filtering" in metrics
        assert "top_k_selected" in metrics
        assert "tools_called" in metrics
        assert "total_latency" in metrics

    def test_metrics_step_latencies(self):
        """Test that step latencies are recorded."""
        request = {
            "component": "battery",
            "spec_filters": None,
            "max_cost": 5000,
            "latest_delivery_days": 30
        }

        result = plan_procurement(request, top_k=2, investigate=False)

        metrics = result["metrics"]
        latencies = metrics["step_latencies"]

        # Check that key steps have timing data
        assert "catalog_load" in latencies
        assert "catalog_search" in latencies
        assert "scoring" in latencies

        # All latencies should be positive numbers
        for step, latency in latencies.items():
            assert isinstance(latency, float)
            assert latency >= 0

    def test_metrics_with_investigation(self):
        """Test metrics when investigation tools are called."""
        request = {
            "component": "solar_panel",
            "spec_filters": None,
            "max_cost": 6000,
            "latest_delivery_days": 30
        }

        result = plan_procurement(request, top_k=2, investigate=True)

        metrics = result["metrics"]

        # Tools should have been called
        assert metrics["tools_called"] > 0
        assert "investigation" in metrics["step_latencies"]

    def test_metrics_values_reasonable(self):
        """Test that metric values are reasonable."""
        request = {
            "component": "comm_module",
            "spec_filters": None,
            "max_cost": 3000,
            "latest_delivery_days": 20
        }

        result = plan_procurement(request, top_k=3, investigate=False)

        metrics = result["metrics"]

        # Check reasonable values
        assert metrics["total_candidates"] > 0
        assert metrics["candidates_after_filtering"] > 0
        assert metrics["top_k_selected"] > 0
        assert metrics["total_latency"] > 0

        # top_k_selected should be <= candidates
        assert metrics["top_k_selected"] <= metrics["candidates_after_filtering"]


class TestMockVendorEndpoint:
    """Test mock vendor extension endpoint."""

    def test_apply_vendor_constraints_basic(self):
        """Test basic vendor constraint filtering."""
        candidates = [
            {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800, "lead_time_days": 21, "reliability": 0.985},
            {"id": "SP-200", "vendor": "Astra Components", "price": 5200, "lead_time_days": 14, "reliability": 0.975},
        ]

        constraints = {"excluded_vendors": ["Astra Components"]}
        result = apply_vendor_constraints(candidates, constraints)

        assert len(result) == 1
        assert result[0]["vendor"] == "Helios Dynamics"

    def test_apply_vendor_constraints_reliability(self):
        """Test reliability constraint filtering."""
        candidates = [
            {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800, "reliability": 0.985},
            {"id": "SP-200", "vendor": "Astra Components", "price": 5200, "reliability": 0.975},
        ]

        constraints = {"min_reliability": 0.98}
        result = apply_vendor_constraints(candidates, constraints)

        assert len(result) == 1
        assert result[0]["id"] == "SP-100"

    def test_apply_vendor_constraints_lead_time(self):
        """Test lead time constraint filtering."""
        candidates = [
            {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800, "lead_time_days": 21},
            {"id": "SP-200", "vendor": "Astra Components", "price": 5200, "lead_time_days": 14},
        ]

        constraints = {"max_lead_time": 15}
        result = apply_vendor_constraints(candidates, constraints)

        assert len(result) == 1
        assert result[0]["id"] == "SP-200"

    def test_mock_vendor_endpoint_post(self):
        """Test MockVendorEndpoint POST handler."""
        endpoint = MockVendorEndpoint()

        candidates = [
            {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800, "reliability": 0.985},
            {"id": "SP-200", "vendor": "Astra Components", "price": 5200, "reliability": 0.975},
        ]

        constraints = {"excluded_vendors": ["Astra Components"]}
        response = endpoint.post_vendor_constraints("req-001", candidates, constraints)

        assert response["status"] == "success"
        assert response["request_id"] == "req-001"
        assert response["candidates_before"] == 2
        assert response["candidates_after"] == 1
        assert len(response["candidates"]) == 1

    def test_mock_vendor_endpoint_get(self):
        """Test MockVendorEndpoint GET handler."""
        endpoint = MockVendorEndpoint()

        candidates = [
            {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800},
        ]
        constraints = {"excluded_vendors": ["Other Vendor"]}

        endpoint.post_vendor_constraints("req-001", candidates, constraints)
        retrieved = endpoint.get_constraint_history("req-001")

        assert retrieved == constraints
        assert endpoint.get_constraint_history("non-existent") is None

    def test_mock_vendor_endpoint_bulk_update(self):
        """Test MockVendorEndpoint bulk update handler."""
        endpoint = MockVendorEndpoint()

        requests = [
            {
                "request_id": "bulk-1",
                "candidates": [
                    {"id": "SP-100", "vendor": "Helios Dynamics", "price": 4800},
                    {"id": "SP-200", "vendor": "Astra Components", "price": 5200},
                ],
                "constraints": {"excluded_vendors": ["Astra Components"]}
            },
            {
                "request_id": "bulk-2",
                "candidates": [
                    {"id": "BAT-50", "vendor": "Helios Dynamics", "price": 2200},
                    {"id": "BAT-80", "vendor": "LunaTech Supplies", "price": 3100},
                ],
                "constraints": {"min_reliability": 0.99}
            }
        ]

        response = endpoint.bulk_update_constraints(requests)

        assert response["status"] == "success"
        assert response["total_requests"] == 2
        assert len(response["results"]) == 2

    def test_endpoint_singleton(self):
        """Test that endpoint singleton works correctly."""
        ep1 = get_endpoint()
        ep2 = get_endpoint()

        # Should be same instance
        assert ep1 is ep2

        # Should retain state
        candidates = [{"id": "SP-100", "vendor": "Helios Dynamics"}]
        constraints = {"excluded_vendors": ["Other"]}
        ep1.post_vendor_constraints("test-req", candidates, constraints)

        retrieved = ep2.get_constraint_history("test-req")
        assert retrieved == constraints


class TestMultiAgentNegotiation:
    """Test multi-agent negotiation functionality."""

    def test_negotiate_procurement_basic(self):
        """Test basic negotiation flow."""
        selected_item = {
            "id": "SP-100",
            "vendor": "Helios Dynamics",
            "price": 4800,
            "lead_time_days": 21,
            "reliability": 0.985
        }
        request = {"max_cost": 6000}

        result = negotiate_procurement(selected_item, request)

        assert "transcript" in result
        assert "verdict" in result
        assert "item_id" in result
        assert "vendor" in result
        assert "price" in result

    def test_negotiate_procurement_approved(self):
        """Test negotiation with approval."""
        selected_item = {
            "id": "SP-100",
            "vendor": "Helios Dynamics",
            "price": 4000,  # Well within budget
            "lead_time_days": 21,
            "reliability": 0.985
        }
        request = {"max_cost": 6000}

        result = negotiate_procurement(selected_item, request)

        assert result["verdict"] == "APPROVED"
        assert len(result["transcript"]) > 0
        # Should have agent proposal and officer response
        assert any("Agent:" in msg for msg in result["transcript"])
        assert any("Officer:" in msg for msg in result["transcript"])

    def test_negotiate_procurement_approved_with_conditions(self):
        """Test negotiation with conditions."""
        selected_item = {
            "id": "SP-100",
            "vendor": "Helios Dynamics",
            "price": 5800,  # Near max budget
            "lead_time_days": 21,
            "reliability": 0.985
        }
        request = {"max_cost": 6000}

        result = negotiate_procurement(selected_item, request)

        assert result["verdict"] == "APPROVED_WITH_CONDITIONS"

    def test_negotiate_procurement_escalated(self):
        """Test negotiation that gets escalated."""
        selected_item = {
            "id": "THR-2",
            "vendor": "Ionix Works",
            "price": 9400,  # Exceeds budget
            "lead_time_days": 18,
            "reliability": 0.98
        }
        request = {"max_cost": 8000}

        result = negotiate_procurement(selected_item, request)

        assert result["verdict"] == "ESCALATED"

    def test_negotiate_procurement_transcript_content(self):
        """Test negotiation transcript has meaningful content."""
        selected_item = {
            "id": "SP-100",
            "vendor": "Helios Dynamics",
            "price": 4800,
            "lead_time_days": 21,
            "reliability": 0.985
        }
        request = {"max_cost": 6000}

        result = negotiate_procurement(selected_item, request)

        transcript = result["transcript"]

        # Should mention item ID
        transcript_text = " ".join(transcript)
        assert "SP-100" in transcript_text
        assert "Helios Dynamics" in transcript_text

    def test_negotiate_procurement_deterministic(self):
        """Test that negotiation is deterministic."""
        selected_item = {
            "id": "SP-100",
            "vendor": "Helios Dynamics",
            "price": 4800,
            "lead_time_days": 21,
            "reliability": 0.985
        }
        request = {"max_cost": 6000}

        result1 = negotiate_procurement(selected_item, request)
        result2 = negotiate_procurement(selected_item, request)

        assert result1["verdict"] == result2["verdict"]
        assert result1["transcript"] == result2["transcript"]


class TestIntegrationWithMetrics:
    """Integration tests combining multiple bonus features."""

    def test_procurement_with_negotiation_and_metrics(self):
        """Test that negotiation can use metrics from procurement."""
        request = {
            "component": "solar_panel",
            "spec_filters": {"power_w": 140},
            "max_cost": 6000,
            "latest_delivery_days": 30,
            "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
        }

        result = plan_procurement(request, top_k=2, investigate=False)

        # Verify metrics are present
        assert "metrics" in result
        assert result["metrics"]["total_latency"] > 0

        # Run negotiation on selected item
        negotiation = negotiate_procurement(result["selected"], request)
        assert negotiation["verdict"] in ["APPROVED", "APPROVED_WITH_CONDITIONS", "ESCALATED"]

    def test_extension_endpoint_with_procurement_results(self):
        """Test extension endpoint filtering procurement results."""
        request = {
            "component": "solar_panel",
            "spec_filters": None,
            "max_cost": 6000,
            "latest_delivery_days": 30
        }

        result = plan_procurement(request, top_k=3, investigate=False)
        candidates = result["candidates"]

        # Apply vendor constraints
        constraints = {"excluded_vendors": ["Astra Components"]}
        filtered = apply_vendor_constraints(candidates, constraints)

        # Should have fewer or equal items
        assert len(filtered) <= len(candidates)
        # Should not have Astra Components
        assert all(c["vendor"] != "Astra Components" for c in filtered)
