# Agentic Procurement System

An intelligent Python-based procurement agent that automates hardware component selection for mission-critical systems (aerospace, satellite missions, etc.). The system uses agentic orchestration, deterministic tools, and LLM-based justification to recommend optimal components from vendor catalogs.

## Overview

This system implements a sophisticated procurement decision pipeline that:
- Searches and filters hardware components based on specifications
- Scores candidates using weighted multi-criteria optimization (price, lead time, reliability)
- Optionally investigates candidates using deterministic research tools
- Generates natural language justifications for selections
- Provides detailed execution traces and performance metrics
- Supports optional multi-agent negotiation simulation

## Key Features

### Core Capabilities
- **Intelligent Catalog Search**: Filter components by type and technical specifications
- **Multi-Criteria Scoring**: Weighted scoring system balancing cost, delivery time, and reliability
- **Tool Integration**: Deterministic price history and vendor availability analysis
- **LLM Justification**: Pluggable LLM adapter for natural language explanations
- **Execution Tracing**: Complete audit trail of decision-making process

### Advanced Features
- **LangGraph Integration**: Optional graph-based workflow orchestration with fallback
- **Multi-Agent Negotiation**: Simulated procurement agent/officer dialogue
- **Performance Metrics**: Step-by-step latency tracking and observability
- **Vendor Constraints**: Dynamic filtering based on vendor preferences
- **CLI Interface**: Full-featured command-line tool for interactive use

## Architecture

The system is organized into modular components:

```
catalog.py          # Catalog management and search
procurement.py      # Core agent orchestration and scoring
llm_adapter.py      # Pluggable LLM interface (Mock + OpenAI)
extension_endpoint.py # Vendor constraint filtering
cli.py              # Command-line interface
tests/              # Comprehensive test suite
```

### Agent Workflow

1. **Catalog Search**: Query local JSON catalog with component type and spec filters
2. **Candidate Scoring**: Normalize and score candidates across price, lead time, reliability
3. **Tool Investigation** (optional): Call price history and availability tools
4. **Selection**: Rank candidates and select top option
5. **Justification**: Generate LLM-powered explanation
6. **Negotiation** (optional): Simulate multi-agent approval process

## Installation

### Requirements
- Python 3.8+
- Dependencies: `pytest` (for testing)

### Setup

```bash
# Clone the repository
git clone https://github.com/shreyank06/agentic-procurement-system.git
cd agentic-procurement-system

# Install dependencies
pip install -r requirements.txt

# For development/testing
pip install -r requirements-dev.txt
```

## Usage

### Web Application (NEW!)

The system now includes a modern web interface built with React and FastAPI.

**Quick Start:**
```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Or using the startup script
./start-webapp.sh

# Or manually
# Terminal 1 - Backend
cd backend && python api.py

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev
```

**Access:**
- **Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

See [WEB_APP_README.md](./WEB_APP_README.md) for detailed web app documentation.

### Command Line Interface

Basic usage:
```bash
python cli.py request.json
```

With investigation and negotiation:
```bash
python cli.py request.json --investigate --negotiate --metrics
```

Full options:
```bash
python cli.py <request_file.json> \
  [--investigate]              # Enable tool investigation
  [--top-k N]                  # Return top N candidates (default: 3)
  [--negotiate]                # Run multi-agent negotiation
  [--metrics]                  # Show performance metrics
  [--constraints-file FILE]    # Apply vendor constraints
  [--llm-provider PROVIDER]    # LLM provider (mock/openai)
```

### Request Format

Example `request.json`:
```json
{
  "component": "solar_panel",
  "spec_filters": {"power_w": 140},
  "max_cost": 6000,
  "latest_delivery_days": 30,
  "weights": {
    "price": 0.4,
    "lead_time": 0.3,
    "reliability": 0.3
  }
}
```

### Python API

```python
from procurement import plan_procurement

request = {
    "component": "solar_panel",
    "spec_filters": {"power_w": 140},
    "max_cost": 6000,
    "latest_delivery_days": 30
}

result = plan_procurement(
    request,
    top_k=3,
    investigate=True,
    llm_provider="mock"
)

print(f"Selected: {result['selected']['id']}")
print(f"Justification: {result['justification']}")
```

### LangGraph Workflow

The system automatically uses LangGraph if installed:

```python
from procurement import run_flow

result = run_flow(
    request,
    investigate=True,
    llm=None,  # Uses mock LLM by default
    top_k=3
)
```

## Catalog

The system includes a pre-configured catalog with aerospace components:

- **Solar Panels** (2 vendors): 150-180W, varying lead times
- **Batteries** (2 vendors): 5000-8000Wh capacity
- **Thrusters** (2 vendors): Ion propulsion systems
- **Communication Modules** (2 vendors): 20-50 Mbps bandwidth

See `catalog.json` for full specifications.

## Testing

Run the complete test suite:

```bash
pytest
```

Run specific test modules:
```bash
pytest tests/test_catalog.py          # Catalog search tests
pytest tests/test_procurement.py      # Agent orchestration tests
pytest tests/test_llm_adapter.py      # LLM adapter tests
pytest tests/test_bonus_features.py   # Advanced features
```

All tests are deterministic and run offline without network access.

### Test Coverage

- Catalog search with/without filters
- Scoring algorithm validation
- Tool determinism verification
- Agent flow integration
- LangGraph fallback behavior
- Multi-agent negotiation
- Vendor constraints
- Error handling

## Scoring Algorithm

Components are scored using normalized multi-criteria optimization:

```
score = w_price × norm_price + w_lead × norm_lead + w_reliability × reliability

Where:
- norm_price = 1 - (price - min_price) / (max_price - min_price)
- norm_lead = 1 - (lead_time - min_lead) / (max_lead - min_lead)
- reliability is used directly (0-1 scale)
```

Default weights: `price=0.4, lead_time=0.3, reliability=0.3`

## Tools

### Price History Tool
Returns deterministic historical pricing data based on item ID hash:
```json
{
  "item_id": "SP-100",
  "history": [
    {"date": "2024-08-19", "price": 4650},
    {"date": "2024-09-18", "price": 4800},
    ...
  ]
}
```

### Availability Tool
Returns vendor availability metrics based on vendor name hash:
```json
{
  "vendor": "Helios Dynamics",
  "avg_lead_time_days": 22.0,
  "in_stock": true,
  "lead_time_samples": [19, 24, 21]
}
```

## Example Output

```
==============================================================
Running Procurement Agent
==============================================================

Request:
  Component: solar_panel
  Spec Filters: {'power_w': 140}
  Max Cost: 6000
  Latest Delivery: 30 days

Candidates Found: 2

Candidate 1: SP-100
  Vendor: Helios Dynamics
  Price: $4800
  Lead Time: 21 days
  Reliability: 0.985
  Score: 0.9234

Candidate 2: SP-200
  Vendor: Astra Components
  Price: $5200
  Lead Time: 14 days
  Reliability: 0.975
  Score: 0.8956

==============================================================
SELECTED: SP-100
==============================================================

Justification:
Selected SP-100 from Helios Dynamics. It balances cost ($4800)
and delivery (21 days) with strong reliability (0.985), making
it the best fit for the request considering all weighted criteria.
```

## LLM Providers

### Mock LLM (Default)
Deterministic justification generation for testing and offline use.

### OpenAI Integration (Optional)
Set `OPENAI_API_KEY` environment variable to use real LLM:
```bash
export OPENAI_API_KEY="your-key-here"
python cli.py request.json --llm-provider openai
```

## Advanced Features

### Vendor Constraints
Filter candidates by vendor preferences:
```json
{
  "allowed_vendors": ["Helios Dynamics", "Astra Components"],
  "blocked_vendors": []
}
```

### Multi-Agent Negotiation
Simulates procurement agent and procurement officer dialogue:
```bash
python cli.py request.json --negotiate
```

Output includes negotiation transcript and verdict (APPROVED/ESCALATED).

### Performance Metrics
Track execution performance:
```bash
python cli.py request.json --metrics
```

Shows step latencies, tool call counts, and total execution time.

## Project Structure

```
.
├── catalog.py              # Catalog management
├── catalog.json            # Component catalog data
├── procurement.py          # Agent orchestration
├── llm_adapter.py          # LLM interface
├── extension_endpoint.py   # Vendor constraints
├── cli.py                  # CLI interface
├── tests/
│   ├── test_catalog.py
│   ├── test_procurement.py
│   ├── test_llm_adapter.py
│   └── test_bonus_features.py
├── requirements.txt
├── requirements-dev.txt
├── EVALUATION.md          # Implementation notes
└── README.md
```

## Design Principles

- **Modularity**: Clear separation of concerns across components
- **Testability**: Comprehensive unit tests with deterministic behavior
- **Extensibility**: Pluggable LLM adapters and tool interfaces
- **Observability**: Full execution tracing and metrics
- **Robustness**: Error handling and input validation throughout
- **Offline-First**: All core functionality works without network access

## Contributing

This project was developed as a technical assessment demonstrating:
- Agentic system design
- Multi-criteria optimization
- Tool orchestration
- LLM integration patterns
- Production-quality Python code organization

## License

MIT License - See LICENSE file for details

## Author

Developed by Shreyank06 for Mercanis technical assessment
