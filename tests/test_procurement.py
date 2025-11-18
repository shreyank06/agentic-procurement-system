# tests/test_procurement.py
import pytest
from catalog import Catalog
from procurement import compute_score, plan_procurement, price_history_tool, availability_tool, run_flow
from llm_adapter import LLMAdapter, MockLLM

def test_catalog_search_and_get():
    # Test Catalog search and get methods
    catalog = Catalog("catalog.json")

    # Test search without filters
    solar_panels = catalog.search("solar_panel")
    assert len(solar_panels) == 2

    # Test search with spec filters
    results = catalog.search("solar_panel", {"power_w": 140})
    assert len(results) == 2

    results = catalog.search("solar_panel", {"power_w": 180})
    assert len(results) == 1
    assert results[0]["id"] == "SP-200"

    # Test get method
    item = catalog.get("SP-100")
    assert item is not None
    assert item["id"] == "SP-100"

    item = catalog.get("INVALID")
    assert item is None

def test_compute_score():
    # Test compute_score function
    item = {
        "price": 1000,
        "lead_time_days": 10,
        "reliability": 0.95
    }
    request = {
        "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
    }

    score = compute_score(item, request, 1000, 2000, 10, 20)
    assert 0.0 <= score <= 1.0

def test_llm_adapter():
    # Test MockLLM
    llm = MockLLM()
    result = llm.generate("Test prompt")

    assert isinstance(result, str)
    assert len(result) > 0

    # Test determinism
    result2 = llm.generate("Test prompt")
    assert result == result2

def test_price_history_tool():
    # Test price_history_tool
    result = price_history_tool("SP-100")

    assert "item_id" in result
    assert "history" in result
    assert result["item_id"] == "SP-100"
    assert len(result["history"]) == 4

    # Test determinism
    result2 = price_history_tool("SP-100")
    assert result == result2

def test_availability_tool():
    # Test availability_tool
    result = availability_tool("Helios Dynamics")

    assert "vendor" in result
    assert "avg_lead_time_days" in result
    assert "in_stock" in result
    assert "lead_time_samples" in result
    assert len(result["lead_time_samples"]) == 3

    # Test determinism
    result2 = availability_tool("Helios Dynamics")
    assert result == result2

def test_plan_procurement():
    # Test basic plan_procurement flow
    request = {
        "component": "solar_panel",
        "spec_filters": {"power_w": 140},
        "max_cost": 6000,
        "latest_delivery_days": 30,
        "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
    }

    result = plan_procurement(request, top_k=3, investigate=False)

    # Check required keys
    assert "request" in result
    assert "candidates" in result
    assert "selected" in result
    assert "justification" in result
    assert "trace" in result

    # Check candidates
    assert len(result["candidates"]) > 0
    assert len(result["candidates"]) <= 3

    # Check selected is top candidate
    assert result["selected"] == result["candidates"][0]

    # Check selected has score
    assert "score" in result["selected"]

def test_plan_procurement_investigate():
    # Test plan_procurement with investigate=True
    request = {
        "component": "solar_panel",
        "spec_filters": {"power_w": 140},
        "max_cost": 6000,
        "latest_delivery_days": 30,
        "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
    }

    result = plan_procurement(request, top_k=2, investigate=True)

    # Check that tools data is attached
    for candidate in result["candidates"]:
        assert "tools" in candidate
        assert "price_history" in candidate["tools"]
        assert "availability" in candidate["tools"]

    # Check that trace includes tool calls
    tool_calls = [t for t in result["trace"] if t.get("step") == "tool_call"]
    assert len(tool_calls) > 0

def test_run_flow():
    # Test run_flow function (should work even without langgraph)
    request = {
        "component": "battery",
        "spec_filters": None,
        "max_cost": 5000,
        "latest_delivery_days": 20
    }

    result = run_flow(request, investigate=False, llm=None, top_k=2)

    # Should have same structure as plan_procurement
    assert "request" in result
    assert "candidates" in result
    assert "selected" in result
    assert "justification" in result
    assert "trace" in result


def test_plan_procurement_no_candidates():
    """Test error handling when no candidates match."""
    request = {
        "component": "nonexistent_component",
        "spec_filters": None,
        "max_cost": 5000,
        "latest_delivery_days": 30
    }

    result = plan_procurement(request)

    # Should return error
    assert "error" in result
    assert result["status"] == 404
    assert "no candidates" in result["error"].lower()
    assert "trace" in result


def test_plan_procurement_no_component():
    """Test error handling when component is missing."""
    request = {
        "spec_filters": None,
        "max_cost": 5000,
        "latest_delivery_days": 30
    }

    result = plan_procurement(request)

    # Should return error for missing component
    assert "error" in result
    assert result["status"] == 400


def test_plan_procurement_with_metrics():
    """Test that metrics are included in response."""
    request = {
        "component": "battery",
        "spec_filters": None,
        "max_cost": 3500,
        "latest_delivery_days": 20
    }

    result = plan_procurement(request, investigate=False)

    # Should include metrics
    assert "metrics" in result
    metrics = result["metrics"]

    # Verify all metric fields
    assert "step_latencies" in metrics
    assert "total_candidates" in metrics
    assert "candidates_after_filtering" in metrics
    assert "top_k_selected" in metrics
    assert "tools_called" in metrics
    assert "total_latency" in metrics

    # Verify latencies dict
    assert isinstance(metrics["step_latencies"], dict)
    assert "catalog_load" in metrics["step_latencies"]
    assert "catalog_search" in metrics["step_latencies"]
    assert "scoring" in metrics["step_latencies"]


def test_plan_procurement_metrics_with_investigation():
    """Test metrics tracking with investigation enabled."""
    request = {
        "component": "thruster",
        "spec_filters": None,
        "max_cost": 10000,
        "latest_delivery_days": 50
    }

    result = plan_procurement(request, investigate=True, top_k=2)

    # Should have investigation metrics
    assert "metrics" in result
    metrics = result["metrics"]

    # Tools should have been called
    assert metrics["tools_called"] > 0
    assert "investigation" in metrics["step_latencies"]


def test_plan_procurement_respects_top_k():
    """Test that top_k parameter is respected."""
    request = {
        "component": "battery",
        "spec_filters": None,
        "max_cost": 5000,
        "latest_delivery_days": 30
    }

    # Request top_k=1
    result = plan_procurement(request, top_k=1)
    assert len(result["candidates"]) == 1

    # Request top_k=2
    result = plan_procurement(request, top_k=2)
    assert len(result["candidates"]) <= 2


def test_plan_procurement_custom_weights():
    """Test that custom weights affect scoring."""
    request = {
        "component": "solar_panel",
        "spec_filters": None,
        "max_cost": 6000,
        "latest_delivery_days": 30,
        "weights": {"price": 0.9, "lead_time": 0.05, "reliability": 0.05}  # Price focused
    }

    result = plan_procurement(request, top_k=2)

    # With price-focused weights, should prefer lower price
    # SP-100 (4800) should score higher than SP-200 (5200)
    assert result["selected"]["id"] == "SP-100"
    assert result["selected"]["price"] == 4800


def test_plan_procurement_trace_completeness():
    """Test that trace contains all key steps."""
    request = {
        "component": "comm_module",
        "spec_filters": None,
        "max_cost": 3000,
        "latest_delivery_days": 20
    }

    result = plan_procurement(request, investigate=False)

    trace = result["trace"]
    trace_steps = [t.get("step") for t in trace]

    # Should have key steps
    assert "catalog_load" in trace_steps
    assert "catalog_search" in trace_steps
    assert "scoring" in trace_steps
    assert "ranking" in trace_steps
    assert "llm_justification" in trace_steps


# ============================================================================
# SCORING TESTS (from test_scoring.py)
# ============================================================================

class TestScoring:
    """Test scoring functionality."""

    def test_compute_score_range(self):
        """Test that scores are in [0, 1] range."""
        item1 = {
            "id": "TEST-1",
            "price": 1000,
            "lead_time_days": 10,
            "reliability": 0.95
        }
        item2 = {
            "id": "TEST-2",
            "price": 2000,
            "lead_time_days": 20,
            "reliability": 0.98
        }
        request = {
            "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
        }

        score = compute_score(item1, request, 1000, 2000, 10, 20)
        assert 0.0 <= score <= 1.0

        score2 = compute_score(item2, request, 1000, 2000, 10, 20)
        assert 0.0 <= score2 <= 1.0

    def test_compute_score_favors_price(self):
        """When weights favor price, lower-priced items should score higher."""
        item1 = {
            "id": "TEST-1",
            "price": 1000,
            "lead_time_days": 10,
            "reliability": 0.95
        }
        item2 = {
            "id": "TEST-2",
            "price": 2000,
            "lead_time_days": 20,
            "reliability": 0.98
        }
        price_focused_request = {
            "weights": {"price": 0.8, "lead_time": 0.1, "reliability": 0.1}
        }

        score1 = compute_score(item1, price_focused_request, 1000, 2000, 10, 20)
        score2 = compute_score(item2, price_focused_request, 1000, 2000, 10, 20)

        # item1 has lower price, so should score higher
        assert score1 > score2

    def test_compute_score_favors_reliability(self):
        """When weights favor reliability, higher reliability items should score higher."""
        item_low_rel = {
            "id": "TEST-A",
            "price": 1500,
            "lead_time_days": 15,
            "reliability": 0.85
        }
        item_high_rel = {
            "id": "TEST-B",
            "price": 1500,
            "lead_time_days": 15,
            "reliability": 0.98
        }
        reliability_focused_request = {
            "weights": {"price": 0.1, "lead_time": 0.1, "reliability": 0.8}
        }

        score1 = compute_score(item_low_rel, reliability_focused_request, 1000, 2000, 10, 20)
        score2 = compute_score(item_high_rel, reliability_focused_request, 1000, 2000, 10, 20)

        # item_high_rel has higher reliability, so should score higher
        assert score2 > score1


# ============================================================================
# TOOL TESTS (from test_tools.py)
# ============================================================================

class TestTools:
    """Test tool functions."""

    def test_price_history_tool_structure(self):
        """Test that price_history_tool returns expected structure."""
        result = price_history_tool("SP-100")

        # Check structure
        assert "item_id" in result
        assert "history" in result
        assert result["item_id"] == "SP-100"

        # Check history is a list with 4 entries
        assert isinstance(result["history"], list)
        assert len(result["history"]) == 4

        # Check each entry has date and price
        for entry in result["history"]:
            assert "date" in entry
            assert "price" in entry
            assert isinstance(entry["price"], int)

    def test_price_history_tool_determinism(self):
        """Test that price_history_tool is deterministic."""
        result1 = price_history_tool("SP-100")
        result2 = price_history_tool("SP-100")

        assert result1 == result2

    def test_availability_tool_structure(self):
        """Test that availability_tool returns expected structure."""
        result = availability_tool("Helios Dynamics")

        # Check structure
        assert "vendor" in result
        assert "avg_lead_time_days" in result
        assert "in_stock" in result
        assert "lead_time_samples" in result

        assert result["vendor"] == "Helios Dynamics"
        assert isinstance(result["avg_lead_time_days"], float)
        assert isinstance(result["in_stock"], bool)
        assert isinstance(result["lead_time_samples"], list)
        assert len(result["lead_time_samples"]) == 3

    def test_availability_tool_determinism(self):
        """Test that availability_tool is deterministic."""
        result1 = availability_tool("Helios Dynamics")
        result2 = availability_tool("Helios Dynamics")

        assert result1 == result2