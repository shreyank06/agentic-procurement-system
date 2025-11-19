# Procurement Agent Web Application

A modern web interface for the Agentic Procurement System, built with React and FastAPI.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │  HTTP   │                 │  Python │                 │
│  React Frontend ├────────>│  FastAPI Backend├────────>│  Procurement    │
│  (Port 3000)    │         │  (Port 8000)    │         │  Agent Core     │
│                 │<────────┤                 │<────────┤                 │
└─────────────────┘  JSON   └─────────────────┘  Return └─────────────────┘
```

## Features

### Frontend (React + Vite + Tailwind)
- **Request Form**: Interactive form for configuring procurement requests
  - Component type selection
  - Dynamic specification filters
  - Cost and delivery constraints
  - Adjustable scoring weights (sliders)
  - Investigation and negotiation toggles
  - LLM provider selection

- **Results Dashboard**:
  - Selected item with AI justification
  - Ranked candidates list
  - Tool investigation results (price history, availability)
  - Execution trace with timeline visualization
  - Performance metrics with charts
  - Multi-agent negotiation transcript

### Backend (FastAPI)
- **REST API Endpoints**:
  - `GET /` - API information
  - `GET /api/health` - Health check
  - `GET /api/catalog/components` - List available components
  - `GET /api/catalog/vendors` - List vendors
  - `GET /api/catalog/items` - Get catalog items
  - `POST /api/procurement` - Run procurement agent
  - `POST /api/negotiate` - Run negotiation
  - `GET /docs` - Interactive API documentation (Swagger UI)

- **Features**:
  - CORS enabled for cross-origin requests
  - Pydantic models for request/response validation
  - Async support for concurrent requests
  - Auto-generated OpenAPI documentation
  - Error handling with proper HTTP status codes

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Install backend dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Run backend server
cd backend
python api.py

# Or use uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Usage Guide

### Step 1: Configure Request
1. Select a **Component Type** (solar_panel, battery, thruster, comm_module)
2. Add **Technical Specifications** (e.g., power_w ≥ 140)
3. Set **Constraints**:
   - Max Cost (optional)
   - Max Delivery Days (optional)
4. Adjust **Scoring Weights**:
   - Price importance (0-1)
   - Lead time importance (0-1)
   - Reliability importance (0-1)

### Step 2: Configure Options
- **Top K**: Number of candidates to display (1-10)
- **Enable Investigation**: Run price history and availability tools
- **Run Negotiation**: Simulate multi-agent approval process
- **LLM Provider**: Mock (offline) or OpenAI (requires API key)

### Step 3: Submit & View Results
- Click "Run Procurement"
- View selected item with AI justification
- Review all ranked candidates
- Inspect execution trace
- Analyze performance metrics
- Read negotiation transcript (if enabled)

## API Examples

### cURL Examples

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Run Procurement:**
```bash
curl -X POST http://localhost:8000/api/procurement \
  -H "Content-Type: application/json" \
  -d '{
    "component": "solar_panel",
    "spec_filters": {"power_w": 140},
    "max_cost": 6000,
    "latest_delivery_days": 30,
    "top_k": 3,
    "investigate": true,
    "llm_provider": "mock"
  }'
```

**Get Components:**
```bash
curl http://localhost:8000/api/catalog/components
```

### Python Examples

```python
import requests

# Run procurement
response = requests.post('http://localhost:8000/api/procurement', json={
    'component': 'battery',
    'spec_filters': {'capacity_wh': 6000},
    'max_cost': 4000,
    'latest_delivery_days': 20,
    'weights': {'price': 0.5, 'lead_time': 0.2, 'reliability': 0.3},
    'top_k': 3,
    'investigate': True
})

result = response.json()
print(f"Selected: {result['selected']['id']}")
print(f"Justification: {result['justification']}")
```

## Development

### Project Structure

```
.
├── backend/
│   ├── api.py                 # FastAPI application
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main application component
│   │   ├── components/       # React components
│   │   │   ├── RequestForm.jsx
│   │   │   ├── SelectedItem.jsx
│   │   │   ├── CandidatesList.jsx
│   │   │   ├── ExecutionTrace.jsx
│   │   │   ├── MetricsPanel.jsx
│   │   │   └── NegotiationPanel.jsx
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── catalog.json              # Component catalog
├── procurement.py            # Core agent logic
├── llm_adapter.py           # LLM interface
├── docker-compose.yml       # Docker orchestration
└── WEB_APP_README.md        # This file
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

**Backend:**
```bash
# Use production ASGI server
pip install gunicorn
gunicorn backend.api:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Environment Variables

### Backend
- `OPENAI_API_KEY` - OpenAI API key (optional, for real LLM)

### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

## API Documentation

Interactive API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python 3.10+**

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn backend.api:app --port 8001
```

**Import errors:**
```bash
# Ensure parent directory is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Use a different port
npm run dev -- --port 3001
```

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

If you see CORS errors, ensure:
1. Backend CORS middleware is configured correctly
2. Frontend is using correct API URL
3. Both services are running

## Performance

- **Backend**: ~50-200ms response time (depends on investigation tools)
- **Frontend**: Initial load <500ms, interactions <100ms
- **Docker**: ~5s startup time for both services

## Security Considerations

⚠️ **Production Checklist:**
- [ ] Configure specific CORS origins (not `["*"]`)
- [ ] Add authentication/authorization
- [ ] Use HTTPS
- [ ] Validate and sanitize all inputs
- [ ] Set rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring

## License

MIT License - See main README.md

## Support

For issues or questions:
1. Check the main README.md
2. Review API documentation at /docs
3. Check browser console for frontend errors
4. Check backend logs for API errors

---

Built with React + FastAPI for the Agentic Procurement System
