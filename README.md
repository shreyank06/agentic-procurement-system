# Agentic Procurement System

An intelligent hardware procurement agent that automates component selection for mission-critical systems (aerospace, satellite missions, etc.). Built with a modern web interface, this system uses agentic orchestration, LLM-powered analysis, and interactive vendor negotiation to recommend and negotiate optimal components from vendor catalogs.

## 🎯 What It Does

The **Agentic Procurement System** helps procurement teams make better hardware decisions faster:

1. **Smart Component Selection** - Automatically searches and ranks components based on specifications, price, delivery time, and reliability
2. **Interactive Vendor Negotiation** - Chat with vendors (LLM-powered) to negotiate prices and delivery terms, with order confirmation and receipts
3. **Cost Analysis** - Analyze selected components for cost optimization opportunities and identify cheaper alternatives
4. **Detailed Justifications** - Get AI-powered explanations for why each component was chosen
5. **Complete Audit Trail** - Full execution traces showing exactly how decisions were made
6. **Performance Metrics** - Track step-by-step timing and resource usage

## Overview

This system implements a sophisticated procurement decision pipeline that:
- Searches and filters hardware components based on specifications and technical requirements
- Scores candidates using weighted multi-criteria optimization (price, lead time, reliability)
- Optionally investigates candidates using deterministic research tools
- Generates natural language justifications for selections using LLMs
- Provides detailed execution traces and performance metrics
- Supports interactive multi-agent vendor negotiation with order confirmation
- Offers cost optimization analysis with savings recommendations

## Key Features

### 🎨 Modern Web Interface
- **Interactive Dashboard** - Beautiful, intuitive UI for procurement decisions
- **Live Chat Negotiation** - Real-time vendor negotiation with LLM-powered responses
- **Order Receipts** - Professional order confirmations with all agreed terms
- **Visual Analytics** - Cost analysis charts and savings recommendations
- **Step-by-Step Guidance** - Welcome screen, step indicators, and guided workflow

### Core Capabilities
- **Intelligent Catalog Search**: Filter components by type and technical specifications
- **Multi-Criteria Scoring**: Weighted scoring system balancing cost, delivery time, and reliability
- **Tool Integration**: Deterministic price history and vendor availability analysis
- **LLM Justification**: OpenAI-powered natural language explanations (with mock fallback)
- **Execution Tracing**: Complete audit trail of decision-making process with timing

### Advanced Features
- **Session-Based Negotiation**: Persistent agent state across chat messages for seamless conversations
- **Multi-Agent Negotiation**: Interactive vendor negotiation with confirmation workflow
- **Performance Metrics**: Step-by-step latency tracking and observability
- **Vendor Constraints**: Dynamic filtering based on vendor preferences
- **Cost Optimization**: AI-powered analysis for cost-saving opportunities
- **Semantic Search**: Find similar products using embeddings (optional with OpenAI)
- **CLI Interface**: Full-featured command-line tool for scripting and automation

## Architecture

The system is organized into a clean, modular architecture:

```
hardware-procurement-agent-wpvuer/
├── backend/                    # Python backend (FastAPI)
│   ├── core/                   # Core business logic
│   │   ├── catalog.py          # Catalog management and search
│   │   ├── procurement.py      # Agent orchestration and scoring
│   │   ├── llm_adapter.py      # LLM interface (OpenAI + Mock)
│   │   └── embeddings.py       # Semantic search embeddings
│   ├── services/               # Service abstractions
│   │   ├── llm_service.py      # LLM service layer
│   │   └── catalog_service.py  # Catalog service layer
│   ├── agents/                 # Intelligent agents
│   │   ├── base_agent.py       # Base agent class
│   │   ├── negotiation_agent.py # Vendor negotiation agent
│   │   └── cost_optimization_agent.py # Cost analysis agent
│   ├── api.py                  # FastAPI application and endpoints
│   ├── requirements.txt        # Python dependencies
│   └── __init__.py
├── frontend/                   # React/Vite web application
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── tests/                      # Comprehensive test suite
│   ├── test_catalog.py
│   ├── test_procurement.py
│   ├── test_llm_adapter.py
│   └── test_bonus_features.py
├── cli.py                      # Command-line interface
├── extension_endpoint.py       # Vendor constraint filtering
├── catalog.json                # Component catalog data
├── requirements.txt
├── docker-compose.yml          # Docker orchestration
└── README.md
```

### Agent Workflow

1. **Catalog Search**: Query local JSON catalog with component type and spec filters
2. **Candidate Scoring**: Normalize and score candidates across price, lead time, reliability
3. **Tool Investigation** (optional): Call price history and availability tools
4. **Selection**: Rank candidates and select top option
5. **Justification**: Generate LLM-powered explanation
6. **Negotiation** (optional): Simulate multi-agent approval process

## Installation & Deployment

### Prerequisites
- **Python** 3.8+ (for backend)
- **Node.js** 14+ (for frontend)
- **Docker & Docker Compose** (optional, for containerized deployment)
- **OpenAI API Key** (optional, for real LLM responses; system works with mock LLM by default)

### Option 1: Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/shreyank06/agentic-procurement-system.git
cd agentic-procurement-system

# Set OpenAI API key (optional, for real LLM)
export OPENAI_API_KEY="your-api-key-here"

# Start everything with Docker Compose
docker-compose up --build

# Access the application
# Web UI: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup (Local Development)

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set OpenAI API key (optional)
export OPENAI_API_KEY="your-api-key-here"

# Start FastAPI server
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
# In a new terminal, install frontend dependencies
cd frontend
npm install

# Start Vite development server
npm run dev

# Access at http://localhost:3000
```

### Option 3: Using the Startup Script
```bash
# Simple one-command startup
chmod +x start-webapp.sh
./start-webapp.sh

# This starts both backend (port 8000) and frontend (port 3000)
```

### Development Setup

For development and testing:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_procurement.py
```

## Usage

### 🌐 Web Application (Interactive UI)

Modern, interactive web interface for procurement decisions with real-time vendor negotiation.

**Start the application** (choose one method above in Installation section)

**Workflow:**
1. **Welcome Screen** - Start with a brief introduction and step guidance
2. **Procurement Request** - Enter component type, specifications, budget, and delivery requirements
3. **Component Selection** - View ranked candidates with scores and details
4. **Vendor Negotiation** - Chat with vendors to negotiate prices and delivery terms
5. **Order Confirmation** - Review and confirm order with professional receipt
6. **Cost Analysis** - Explore cost optimization opportunities and alternatives

**Key Features:**
- Real-time LLM-powered vendor responses
- Professional order receipts with all confirmed terms
- Persistent chat state across messages
- Cost analysis with savings recommendations
- Step-by-step guidance throughout the process
- Mobile-responsive design

**Access Points:**
- **Web UI**: http://localhost:3000 - Interactive procurement dashboard
- **Backend API**: http://localhost:8000 - RESTful API endpoints
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger/OpenAPI docs

For detailed web app features, see [WEB_APP_README.md](./WEB_APP_README.md)

### 💻 Command Line Interface

Perfect for automation, scripting, and integration into other systems.

**Basic usage:**
```bash
python cli.py request.json
```

**With investigation, negotiation, and metrics:**
```bash
python cli.py request.json --investigate --negotiate --metrics
```

**Full options:**
```bash
python cli.py <request_file.json> \
  [--investigate]              # Enable tool investigation (price history, availability)
  [--top-k N]                  # Return top N candidates (default: 3)
  [--negotiate]                # Run multi-agent negotiation simulation
  [--metrics]                  # Show performance metrics and timings
  [--constraints-file FILE]    # Apply vendor constraints from JSON file
  [--llm-provider PROVIDER]    # LLM provider: mock (default) or openai
```

**Examples:**
```bash
# Simple selection with explanation
python cli.py request.json

# Detailed analysis with investigation and metrics
python cli.py request.json --investigate --metrics

# Full workflow with negotiation
python cli.py request.json --investigate --negotiate --metrics

# With custom constraints
python cli.py request.json --constraints-file constraints.json

# Using OpenAI LLM (requires OPENAI_API_KEY)
OPENAI_API_KEY="sk-..." python cli.py request.json --llm-provider openai
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

### 🐍 Python API

Integrate procurement logic directly into your Python applications:

```python
from backend.core.procurement import plan_procurement

request = {
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

# Run procurement with investigation
result = plan_procurement(
    request,
    top_k=3,
    investigate=True,
    llm_provider="openai",  # or "mock" for offline use
    api_key="your-openai-key"
)

# Access results
print(f"Selected: {result['selected']['id']}")
print(f"Justification: {result['justification']}")
print(f"Total candidates: {result['metrics']['total_candidates']}")
print(f"Execution time: {result['metrics']['total_latency']:.2f}s")

# View full decision trace
for step in result['trace']:
    print(f"  - {step['step']}: {step.get('status', step.get('result', ''))}")
```

**API Functions:**
- `plan_procurement()` - Main procurement decision function
- `negotiate_procurement()` - Run vendor negotiation
- `run_flow()` - Execute LangGraph workflow (if installed)

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

## Environment Variables

Configure the system using environment variables:

```bash
# LLM Configuration
export OPENAI_API_KEY="sk-..."              # OpenAI API key (required for real LLM)

# Embeddings Configuration
export ENABLE_EMBEDDINGS="true"             # Enable semantic search (default: true)

# Server Configuration
export HOST="0.0.0.0"                       # Server host
export PORT="8000"                          # Server port
export ENVIRONMENT="production"             # Environment (development/production)
```

**Frontend Environment Variables** (in `.env` file):
```
VITE_API_URL=http://localhost:8000
```

## Project Structure

Complete directory layout with descriptions:

```
hardware-procurement-agent-wpvuer/
├── backend/                           # FastAPI backend application
│   ├── core/                          # Core business logic modules
│   │   ├── catalog.py                 # Hardware catalog management
│   │   ├── procurement.py             # Agent orchestration & scoring
│   │   ├── llm_adapter.py             # LLM interface (OpenAI + Mock)
│   │   └── embeddings.py              # Semantic search embeddings
│   ├── services/                      # Service layer abstractions
│   │   ├── llm_service.py
│   │   └── catalog_service.py
│   ├── agents/                        # Intelligent agents
│   │   ├── base_agent.py              # Base class for all agents
│   │   ├── negotiation_agent.py       # Vendor negotiation agent
│   │   └── cost_optimization_agent.py # Cost analysis agent
│   ├── api.py                         # FastAPI app and endpoints
│   ├── requirements.txt               # Python dependencies
│   └── __init__.py
├── frontend/                          # React/Vite web application
│   ├── src/
│   │   ├── components/                # React UI components
│   │   ├── App.jsx                    # Main app component
│   │   └── main.jsx                   # Entry point
│   ├── public/                        # Static assets
│   ├── package.json                   # NPM dependencies
│   ├── vite.config.js                 # Vite bundler config
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── Dockerfile                     # Frontend Docker image
│   └── .env.example                   # Environment template
├── tests/                             # Comprehensive test suite
│   ├── test_catalog.py                # Catalog tests
│   ├── test_procurement.py            # Procurement logic tests
│   ├── test_llm_adapter.py            # LLM adapter tests
│   └── test_bonus_features.py         # Advanced feature tests
├── cli.py                             # Command-line interface
├── extension_endpoint.py              # Vendor constraint filtering
├── catalog.json                       # Component catalog data (JSON)
├── request.json                       # Sample procurement request
├── requirements.txt                   # Root Python dependencies
├── requirements-dev.txt               # Development dependencies
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile.backend                 # Backend Docker image
├── start-webapp.sh                    # Quick start script
├── EVALUATION.md                      # Implementation notes
├── WEB_APP_README.md                  # Web app documentation
└── README.md                          # This file
```

## Tech Stack & Concepts

### Backend Technologies
- **FastAPI** - Modern Python web framework for building REST APIs
- **Python 3.8+** - Core programming language
- **Pydantic** - Data validation and serialization
- **OpenAI API** - LLM integration for natural language generation and analysis
- **NumPy** - Numerical computations for scoring algorithms
- **Pytest** - Testing framework with comprehensive test coverage

### Frontend Technologies
- **React 18** - UI library for interactive components
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS for styling
- **Axios** - HTTP client for API communication
- **JavaScript ES6+** - Modern JavaScript features

### Key Concepts & Algorithms

#### 1. **Multi-Criteria Decision Making (MCDM)**
- Weighted scoring algorithm that balances three criteria:
  - Price normalization: `1 - (price - min) / (max - min)`
  - Lead time normalization: `1 - (lead_time - min) / (max - min)`
  - Reliability score: Used directly (0-1 scale)
- Final score: `w_price × norm_price + w_lead × norm_lead + w_reliability × reliability`
- Default weights: price=0.4, lead_time=0.3, reliability=0.3 (customizable)

#### 2. **Semantic Search & Vector Embeddings**
- **Vector Embeddings**: Convert text descriptions to numerical vectors using OpenAI's embedding model
- **Cosine Similarity**: Measures semantic similarity between component descriptions and search queries
- **Approximate Nearest Neighbors**: Fast retrieval of similar products
- **Use Case**: Find competitive alternatives and similar products based on meaning, not just keywords
- **Example**: Query "solar power" finds both "solar panel" and "photovoltaic module"
- **Caching**: Embeddings cached locally to avoid redundant API calls

#### 3. **LLM Integration & Prompting**
- **Pluggable LLM Adapter**: Abstracts LLM provider implementation
- **OpenAI API Integration**: GPT-3.5/GPT-4 for justifications and vendor responses
- **Deterministic Mock LLM**: Hash-based responses for testing without API calls
- **Prompt Engineering**: Carefully crafted prompts for consistent, structured responses
- **Token Optimization**: Max tokens limited to keep responses concise and costs low

#### 4. **Agent-Based Architecture**
- **BaseAgent**: Abstract class defining agent interface
- **NegotiationAgent**: Vendor negotiation with stateful conversation tracking
- **CostOptimizationAgent**: Cost analysis and savings recommendations
- **State Management**: Session-based persistence across chat messages
- **Agent Orchestration**: Coordination between multiple agents in procurement workflow

#### 5. **Session Management & State Persistence**
- **In-Memory Sessions**: Dictionary of agent instances keyed by session ID
- **UUID Generation**: Unique identifiers for each negotiation session
- **Stateful Conversations**: Agent maintains confirmation_asked, order_confirmed, and negotiated terms
- **Session Lifecycle**: Sessions persist across multiple API calls for seamless negotiations

#### 6. **Agentic Orchestration**
- **Workflow Steps**: Catalog search → Scoring → Investigation → Justification → Selection
- **Tool Calling**: Deterministic tools (price_history, availability) that simulate research
- **LangGraph Support**: Optional graph-based orchestration with automatic fallback
- **Execution Tracing**: Every step logged with latency and status for audit trail

#### 7. **Deterministic Testing Tools**
- **Price History Tool**: Hash-based deterministic pricing data generation
- **Availability Tool**: Vendor availability metrics based on hash of vendor name
- **Offline-First**: All tools work without external API calls
- **Reproducible**: Same input always produces same output for testing

### Deployment & DevOps
- **Docker** - Container orchestration
- **Docker Compose** - Multi-container application management
- **Environment Variables** - Configuration management
- **CORS** - Cross-Origin Resource Sharing for frontend-backend communication
- **Uvicorn** - ASGI server for FastAPI application

### Development & Testing
- **Pytest** - Comprehensive unit and integration tests
- **Mock Objects** - Simulated LLM and vendor responses for testing
- **Test Coverage** - 49+ test cases covering all major features
- **Deterministic Tests** - No random behavior, all tests reproducible

### Advanced Features
- **Performance Metrics** - Step-by-step timing with nanosecond precision
- **Execution Traces** - Complete decision audit trail in JSON format
- **Error Handling** - Graceful fallbacks and comprehensive validation
- **Logging** - Structured logging for debugging and monitoring

## Design Principles

- **Modularity**: Clear separation of concerns across components (core, services, agents)
- **Testability**: Comprehensive unit tests with deterministic behavior for reproducibility
- **Extensibility**: Pluggable LLM adapters and tool interfaces for easy integration
- **Observability**: Full execution tracing and metrics for decision audit trails
- **Robustness**: Error handling, validation, and graceful degradation throughout
- **Offline-First**: All core functionality works without network access (mock LLM fallback)
- **Session-Based**: Stateful agent management for seamless multi-turn conversations
- **Semantic-Aware**: Vector embeddings for intelligent product comparison and discovery

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
