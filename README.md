## Objective

Build a small, well-tested Python agentic system that automates component procurement decisions for mission hardware. The system should load a local catalog of suppliers and items, score and rank candidates against a request, optionally consult lightweight deterministic "tools" (price history, vendor availability), and produce a human-readable procurement plan and justification. Implementation should be modular and include unit tests.

## Brief

You will implement a lightweight agent pipeline in Python that automates selecting procurement candidates for mission hardware requests. The agent will:

- Load and search a local catalog of components and vendors.
- Score and rank candidate items based on numeric and spec constraints.
- Optionally call simple deterministic "tools" (simulated external APIs) to fetch price history or vendor availability.
- Generate a short natural-language justification for the selected item using a pluggable LLM adapter (a deterministic MockLLM is required; wiring a real provider is optional).
- Provide an execution trace that shows tool usage and decision steps.

This challenge tests Python design, data modeling, deterministic agent orchestration (tool calls + decision logic), unit testing, and optional lightweight LLM orchestration. The work should be completable in ~2–4 hours.

Notes about structure (flexible)
- Implement the functionality as a small package/module set. You do not need to follow exact filenames; instead implement logically grouped modules (e.g., catalog handling, scoring utilities, agent orchestration, llm adapter, tools, optional orchestration adapter, CLI/testing harness).
- Keep modules small and focused, with clear docstrings and unit tests.
- The local catalog (below) should be included as a literal JSON resource in your project and loaded from disk relative to the module that reads it.

Catalog JSON (use this content exactly)
[
  {
    "id": "SP-100",
    "component": "solar_panel",
    "vendor": "Helios Dynamics",
    "price": 4800,
    "lead_time_days": 21,
    "reliability": 0.985,
    "specs": {"power_w": 150, "mass_kg": 12}
  },
  {
    "id": "SP-200",
    "component": "solar_panel",
    "vendor": "Astra Components",
    "price": 5200,
    "lead_time_days": 14,
    "reliability": 0.975,
    "specs": {"power_w": 180, "mass_kg": 15}
  },
  {
    "id": "BAT-50",
    "component": "battery",
    "vendor": "Helios Dynamics",
    "price": 2200,
    "lead_time_days": 10,
    "reliability": 0.97,
    "specs": {"capacity_wh": 5000, "mass_kg": 8}
  },
  {
    "id": "BAT-80",
    "component": "battery",
    "vendor": "LunaTech Supplies",
    "price": 3100,
    "lead_time_days": 25,
    "reliability": 0.99,
    "specs": {"capacity_wh": 8000, "mass_kg": 12}
  },
  {
    "id": "THR-1",
    "component": "thruster",
    "vendor": "Astra Components",
    "price": 7600,
    "lead_time_days": 45,
    "reliability": 0.96,
    "specs": {"thrust_n": 30, "isp_s": 320}
  },
  {
    "id": "THR-2",
    "component": "thruster",
    "vendor": "Ionix Works",
    "price": 9400,
    "lead_time_days": 18,
    "reliability": 0.98,
    "specs": {"thrust_n": 28, "isp_s": 380}
  },
  {
    "id": "CM-10",
    "component": "comm_module",
    "vendor": "LunaTech Supplies",
    "price": 1300,
    "lead_time_days": 7,
    "reliability": 0.96,
    "specs": {"bandwidth_mbps": 20, "mass_kg": 3}
  },
  {
    "id": "CM-20",
    "component": "comm_module",
    "vendor": "Helios Dynamics",
    "price": 1700,
    "lead_time_days": 12,
    "reliability": 0.985,
    "specs": {"bandwidth_mbps": 50, "mass_kg": 4}
  }
]

Task 1 — Core agent components (required)
- Implement a Catalog component:
  - Constructor should load the catalog JSON resource from a given path into memory.
  - Methods:
    - search(component: str, spec_filters: dict | None = None) -> List[dict]
      - Return all items whose "component" matches the requested component and whose numeric specs meet (>=) all numeric spec_filters. Example: spec_filters={"power_w": 120} returns solar panels with power_w >= 120.
      - If spec_filters is None, return all items for the component.
    - get(item_id: str) -> dict | None
      - Return the item dict by id or None if not found.
    - list_vendors() -> Set[str]
      - Return unique vendor names present in the catalog.
  - Add a short unit-test that exercises search with and without spec_filters and get(item_id).

- Implement scoring utilities:
  - Provide a function compute_score(item: dict, request: dict, price_min: float, price_max: float, lead_min: int, lead_max: int) -> float
    - Signature and behavior:
      - item: catalog item dict
      - request: dict that may contain "weights" mapping numeric criteria to weights. Default weights: price:0.4, lead_time:0.3, reliability:0.3
      - price_min/price_max and lead_min/lead_max are numeric bounds computed across the candidate set and passed in.
    - Normalizations:
      - normalized_price = clamp(0, 1, 1 - (price - price_min) / (price_max - price_min)) — if price_max == price_min then set normalized_price = 1.
      - normalized_lead_time = clamp(0, 1, 1 - (lead_time - lead_min) / (lead_max - lead_min)) — if lead_max == lead_min then set normalized_lead_time = 1.
      - reliability is used directly (assumed 0..1).
    - Final score = weights.price * normalized_price + weights.lead_time * normalized_lead_time + weights.reliability * reliability
    - Return a float score in [0, 1] (or extremely close due to float rounding).
  - Add unit tests:
    - Ensure scores are within [0,1], and that when weights favor price, lower-priced items have higher scores; when weights favor reliability, higher reliability yields higher score.

- Implement an LLM adapter interface and a MockLLM:
  - Define an abstract interface (or base class) LLMAdapter with method generate(prompt: str, max_tokens: int = 150) -> str.
  - Implement MockLLM that always returns a deterministic justification string based on the prompt contents. For example:
    - If the prompt contains the phrase "choose between", MockLLM returns a paragraph that prefers the higher-scoring item and cites price, lead_time, and reliability.
    - Ensure mock behavior is deterministic and does not require network.
  - Implement a small provider-switcher helper that returns MockLLM if environment variables for real providers are not present; if the environment contains OPENAI_API_KEY (or others), you may optionally wire a real provider adapter, but tests must default to mock.

- Implement the procurement orchestration function plan_procurement(request: dict, top_k: int = 3, investigate: bool = False, llm_provider: str = "mock") -> dict
  - Request format (example):
    {
      "component": "solar_panel",
      "spec_filters": {"power_w": 140},
      "max_cost": 6000,
      "latest_delivery_days": 30,
      "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
    }
  - Steps to implement:
    1. Use the Catalog.search to obtain candidate items matching component/spec_filters.
    2. If no candidates are found, return {"error": "no candidates", "status": 404}.
    3. Compute price_min, price_max, lead_min, lead_max across the candidate set.
    4. Score each candidate using compute_score (pass bounds).
    5. Sort candidates by score descending and pick the top_k.
    6. If investigate is True, call the two deterministic tools (Task 2) for each top candidate and attach their outputs to each candidate under a "tools" key.
    7. Use the selected LLM adapter to generate a short justification for the top candidate. Design a prompt template that includes: item id, price, lead_time, reliability, request constraints (max_cost/latest_delivery), and a short instruction to justify the choice briefly (2–3 sentences).
    8. Build and return a result dict with keys:
       - "request": original request dict
       - "candidates": list of candidate dicts augmented with "score" (float) and optionally "tools"
       - "selected": the top candidate dict (with "score" and "tools" if present)
       - "justification": string produced by LLMAdapter
       - "trace": a list describing key decisions and tool calls (entries should include tool name, input, short result summary)
    - Provide error handling: invalid request structure should raise a clear exception or return a structured error dict.

- Minimal CLI (optional)
  - Create a tiny CLI script or function that reads a request JSON file, calls plan_procurement, and prints the returned dict in a readable format to stdout. This is optional but helpful for manual testing.

Task 2 — Deterministic tools (required)
- Implement two deterministic tool functions and make them callable within the agent when investigate=True:
  - price_history_tool(item_id: str) -> dict
    - Return {"item_id": item_id, "history": [{"date": "YYYY-MM-DD", "price": int}, ...]}
    - Provide at least 4 historical points with some variability.
    - Determinism: make the results deterministic based on item_id (e.g., compute base price from item id characters and derive a small sequence).
  - availability_tool(vendor: str) -> dict
    - Return {"vendor": vendor, "avg_lead_time_days": float, "in_stock": bool, "lead_time_samples": [int, int, int]}
    - Deterministic based on vendor name (e.g., hash vendor string to produce values).
- Agent behavior when investigate=True:
  - For each top candidate, call both tools and attach results to candidate["tools"] = {"price_history": ..., "availability": ...}.
  - Append an entry to agent["trace"] for each tool call indicating tool name, input, and a short summary (e.g., "price_history: last price=4800; trend=stable").
- Tests:
  - Verify tools return the expected structure and are deterministic across repeated calls.
  - Verify that plan_procurement(..., investigate=True) includes tool outputs in candidates and has trace entries for those calls.

Task 3 — Optional orchestration integration (optional but encouraged)
- If the langgraph library is installed in the environment at runtime, provide an adapter that composes the steps into a simple directed flow with distinct nodes:
  - Node A: Catalog.search
  - Node B: scoring across results
  - Node C: conditional tools calls (if investigate=True)
  - Node D: LLM justification
- Implement a function run_flow(request: dict, investigate: bool, llm: LLMAdapter) -> dict that runs the flow and returns the same output shape as plan_procurement.
- If langgraph is not installed, run_flow must gracefully fall back to the synchronous plan_procurement implementation.
- Provide a small adapter module for this behavior and unit tests:
  - test_langgraph_fallback: ensure run_flow works when langgraph is not installed (fallback).
  - Optionally simulate a present langgraph by monkeypatching imports or toggling a flag to exercise the flow composition branch.

Testing requirements
- Use pytest for all tests. Tests must run offline and deterministically.
- Required tests (examples):
  - test_catalog_search_and_get: exercise Catalog.search with spec filters and Catalog.get behavior.
  - test_compute_score: with a small set of representative items, verify scores fall in [0,1] and that weight changes affect relative ordering as expected.
  - test_tools: call price_history_tool and availability_tool and assert keys and deterministic outputs.
  - test_agent_basic_flow: run plan_procurement with the example request and assert the result includes keys "request", "candidates", "selected", "justification", "trace", and that selected matches top-ranked candidate.
  - test_agent_investigate_trace: run plan_procurement(..., investigate=True) and assert trace includes tool calls and that candidates include "tools" data.
  - test_langgraph_fallback: ensure run_flow works when langgraph isn't installed (fallback).
- Provide a requirements-dev.txt that lists pytest and any optional dependencies you used. Keep dependencies minimal so tests run locally without network access.

Example request for manual testing (use this in CLI/tests)
{
  "component": "solar_panel",
  "spec_filters": {"power_w": 140},
  "max_cost": 6000,
  "latest_delivery_days": 30,
  "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
}

Expected behavior for the example:
- Both SP-100 and SP-200 match the spec_filters; agent computes min/max price and lead_time across these candidates; computes normalized scores; returns a ranked list and picks the top candidate; and produces a short justification such as:
  "Selected SP-100 from Helios Dynamics. It balances cost (4800) and delivery (21 days) with strong reliability (0.985), making it the best fit for the request."

Bonus objectives (optional)
- Semantic search fallback: implement a deterministic embedding function (hash to small numeric vector) and a simple nearest-neighbor search for free-text specification queries. Wire it as an alternate search mode in Catalog (e.g., search_semantic(query: str)).
- Metrics and observability: compute and include simple metrics (e.g., precision@k if ground-truth mapping provided in tests), log step latencies, and include a metrics summary in the returned result under key "metrics".
- Mock extension endpoint: create a small function that simulates an HTTP handler accepting vendor constraints and returning updated candidate lists (no real network required — tests can call the handler directly).
- Multi-agent negotiation (toy): implement a small deterministic negotiation between a "procurement agent" and a "procurement officer" that returns a short negotiation transcript included in trace.

### Evaluation Criteria

Submissions will be evaluated on:
- Correctness: Does the agent perform search, scoring, ranking, and return the required keys and behavior?
- Clarity and modularity: Is the code organized into clear modules with well-named functions and docstrings?
- Tests: Are there meaningful unit tests? Do they run offline and deterministically?
- Agentic design: Is tool usage implemented and traced? Is the LLM adapter pluggable and deterministic by default?
- Robustness: Proper error handling and input validation.
- Optional: LangGraph integration, semantic search, metrics/observability, or multi-agent simulation.

### CodeSubmit

Please organize, design, test, and document your code as if it were going into production - then push your changes to the master branch.

Have fun coding! 🚀

The Mercanis Team