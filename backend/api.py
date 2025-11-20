"""
FastAPI Backend for Procurement Agent Web Application.

Provides REST API endpoints for the procurement agent system.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path to import procurement modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from catalog import Catalog
from procurement import plan_procurement, negotiate_procurement
from llm_adapter import select_llm_provider
from cost_optimizer import CostOptimizer
from cost_optimization_agent import CostOptimizationAgent
from negotiation_agent import NegotiationAgent

# Initialize FastAPI app
app = FastAPI(
    title="Procurement Agent API",
    description="Intelligent hardware procurement system with agentic decision-making",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load catalog at startup with embeddings enabled
import os
catalog_path = Path(__file__).parent.parent / "catalog.json"
enable_embeddings = os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true"
openai_key = os.getenv("OPENAI_API_KEY")
catalog = Catalog(str(catalog_path), enable_embeddings=enable_embeddings, api_key=openai_key)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ProcurementRequest(BaseModel):
    """Request model for procurement endpoint."""
    component: str = Field(..., description="Component type to procure")
    spec_filters: Optional[Dict[str, float]] = Field(None, description="Technical specification filters")
    max_cost: Optional[float] = Field(None, description="Maximum cost constraint")
    latest_delivery_days: Optional[int] = Field(None, description="Latest delivery constraint in days")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Scoring weights for price, lead_time, reliability"
    )
    top_k: int = Field(3, description="Number of top candidates to return")
    investigate: bool = Field(False, description="Enable tool investigation")
    llm_provider: str = Field("mock", description="LLM provider (mock or openai)")
    api_key: Optional[str] = Field(None, description="API key for LLM provider (required for OpenAI)")

    class Config:
        schema_extra = {
            "example": {
                "component": "solar_panel",
                "spec_filters": {"power_w": 140},
                "max_cost": 6000,
                "latest_delivery_days": 30,
                "weights": {"price": 0.4, "lead_time": 0.3, "reliability": 0.3},
                "top_k": 3,
                "investigate": False,
                "llm_provider": "mock",
                "api_key": None
            }
        }


class NegotiationRequest(BaseModel):
    """Request model for negotiation endpoint."""
    selected_item: Dict = Field(..., description="Selected item from procurement")
    request: Dict = Field(..., description="Original procurement request")


class AnalysisRequest(BaseModel):
    """Request model for initial analysis endpoints (cost optimization and negotiation start)."""
    selected_item: Dict = Field(..., description="Selected item context")
    request: Dict = Field(..., description="Original procurement request")
    llm_provider: str = Field("mock", description="LLM provider (mock or openai)")
    api_key: Optional[str] = Field(None, description="API key for LLM provider")


class ChatRequest(BaseModel):
    """Request model for interactive chat endpoints."""
    user_message: str = Field(..., description="User message in the chat")
    conversation: List[Dict] = Field(default_factory=list, description="Conversation history")
    selected_item: Dict = Field(..., description="Selected item context")
    request: Dict = Field(..., description="Original procurement request")
    llm_provider: str = Field("mock", description="LLM provider (mock or openai)")
    api_key: Optional[str] = Field(None, description="API key for LLM provider")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Procurement Agent API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "procurement": "/api/procurement",
            "catalog": "/api/catalog",
            "negotiate": "/api/negotiate",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "catalog_loaded": True}


@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables."""
    return {
        "VITE_API_URL": os.getenv("VITE_API_URL", "NOT SET"),
        "BACKEND_URL": os.getenv("BACKEND_URL", "NOT SET"),
        "OPENAI_API_KEY": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "NOT SET"),
        "catalog_loaded": catalog is not None,
        "catalog_items": len(catalog.items) if catalog else 0
    }


@app.get("/api/catalog/components")
async def get_components():
    """Get list of available component types."""
    try:
        # Get all items and extract unique component types
        all_items = catalog.items
        components = list(set(item["component"] for item in all_items))

        # Get count for each component
        component_details = {}
        for comp in components:
            items = [item for item in all_items if item["component"] == comp]
            component_details[comp] = {
                "count": len(items),
                "vendors": list(set(item["vendor"] for item in items)),
                "price_range": [
                    min(item["price"] for item in items),
                    max(item["price"] for item in items)
                ]
            }

        return {
            "components": components,
            "details": component_details,
            "total_items": len(all_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch components: {str(e)}")


@app.get("/api/catalog/vendors")
async def get_vendors():
    """Get list of available vendors."""
    try:
        vendors = list(catalog.list_vendors())

        # Get item count per vendor
        vendor_details = {}
        for vendor in vendors:
            items = [item for item in catalog.items if item["vendor"] == vendor]
            vendor_details[vendor] = {
                "item_count": len(items),
                "components": list(set(item["component"] for item in items))
            }

        return {
            "vendors": vendors,
            "details": vendor_details,
            "total_vendors": len(vendors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendors: {str(e)}")


@app.get("/api/catalog/items")
async def get_catalog_items(component: Optional[str] = None):
    """Get all catalog items, optionally filtered by component type."""
    try:
        if component:
            items = catalog.search(component)
        else:
            items = catalog.items

        return {
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch items: {str(e)}")


@app.post("/api/procurement")
async def run_procurement(request: ProcurementRequest):
    """
    Run procurement agent to select optimal component.

    Returns selected item, candidates, justification, trace, and metrics.
    """
    try:
        # Convert request to dict
        request_dict = {
            "component": request.component,
            "spec_filters": request.spec_filters,
            "max_cost": request.max_cost,
            "latest_delivery_days": request.latest_delivery_days,
            "weights": request.weights or {"price": 0.4, "lead_time": 0.3, "reliability": 0.3}
        }

        # Handle API key for OpenAI provider
        import os
        import sys
        api_key_to_use = None

        if request.llm_provider.lower() == "openai":
            # Use provided API key or fall back to environment variable
            api_key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")

            if not api_key_to_use:
                all_env_keys = sorted(list(os.environ.keys()))
                raise HTTPException(
                    status_code=400,
                    detail=f"OpenAI API key required. Total env vars: {len(all_env_keys)}, OPENAI vars: {[k for k in all_env_keys if 'OPENAI' in k.upper()]}"
                )

        # Run procurement
        result = plan_procurement(
            request=request_dict,
            top_k=request.top_k,
            investigate=request.investigate,
            llm_provider=request.llm_provider,
            api_key=api_key_to_use
        )

        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=result.get("status", 500),
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Procurement failed: {str(e)}")


@app.post("/api/negotiate/start")
async def start_negotiation(request: AnalysisRequest):
    """
    Start vendor negotiation for selected item.

    Returns vendor's opening position.
    """
    try:
        # Validate LLM provider and API key
        if request.llm_provider.lower() == "openai":
            api_key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key_to_use:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key required. Please provide api_key or set OPENAI_API_KEY environment variable"
                )

        # Initialize agent with LLM provider, API key, and catalog for semantic search
        agent = NegotiationAgent(
            llm_provider=request.llm_provider,
            api_key=request.api_key,
            catalog=catalog
        )

        # Check if LLM initialization failed
        if agent.llm is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize LLM provider. Please check API key."
            )

        # Start negotiation
        result = agent.start_negotiation(
            selected_item=request.selected_item,
            request=request.request
        )

        # Find competing products using semantic search
        competitors = agent.find_competing_products()
        if competitors:
            result["competitors"] = competitors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation failed: {str(e)}")


@app.post("/api/negotiate/chat")
async def negotiate_chat(request: ChatRequest):
    """
    Continue vendor negotiation with buyer proposals.

    User can make offers and negotiate terms with the vendor.
    """
    try:
        # Validate LLM provider and API key
        if request.llm_provider.lower() == "openai":
            api_key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key_to_use:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key required. Please provide api_key or set OPENAI_API_KEY environment variable"
                )

        # Initialize agent with catalog for semantic search
        agent = NegotiationAgent(
            llm_provider=request.llm_provider,
            api_key=request.api_key,
            catalog=catalog
        )

        # Check if LLM initialization failed
        if agent.llm is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize LLM provider. Please check API key."
            )

        # Set context from conversation
        if request.conversation:
            agent.selected_item = request.selected_item

        # Get vendor response with full context
        response = agent.respond_to_offer(
            request.user_message,
            request.conversation,
            request=request.request
        )

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation chat failed: {str(e)}")


@app.post("/api/cost-optimize/start")
async def start_cost_optimization(request: AnalysisRequest):
    """
    Start cost optimization analysis with semantic search for alternatives.

    Returns initial cost analysis and savings recommendations.
    """
    try:
        # Validate LLM provider and API key
        if request.llm_provider.lower() == "openai":
            api_key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key_to_use:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key required. Please provide api_key or set OPENAI_API_KEY environment variable"
                )

        # Initialize agent with LLM provider, API key, and catalog for semantic search
        agent = CostOptimizationAgent(
            llm_provider=request.llm_provider,
            api_key=request.api_key,
            catalog=catalog
        )

        # Check if LLM initialization failed
        if agent.llm is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize LLM provider. Please check API key."
            )

        # Get initial analysis
        result = agent.analyze_costs(
            selected_item=request.selected_item,
            request=request.request
        )

        # Find cheaper alternatives using semantic search
        alternatives = agent.find_cheaper_alternatives(request.selected_item)
        if alternatives:
            result["alternatives"] = alternatives

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost optimization failed: {str(e)}")


@app.post("/api/cost-optimize/chat")
async def cost_optimize_chat(request: ChatRequest):
    """
    Continue cost optimization discussion with follow-up questions.

    User can ask specific questions about cost optimization strategies.
    """
    try:
        # Validate LLM provider and API key
        if request.llm_provider.lower() == "openai":
            api_key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key_to_use:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key required. Please provide api_key or set OPENAI_API_KEY environment variable"
                )

        # Initialize agent with catalog for semantic search
        agent = CostOptimizationAgent(
            llm_provider=request.llm_provider,
            api_key=request.api_key,
            catalog=catalog
        )

        # Check if LLM initialization failed
        if agent.llm is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize LLM provider. Please check API key."
            )

        # Get agent response with full context
        response = agent.chat(
            request.user_message,
            request.conversation,
            selected_item=request.selected_item,
            request=request.request
        )

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost optimization chat failed: {str(e)}")


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    print("🚀 Procurement Agent API starting...")
    print(f"📁 Catalog loaded: {len(catalog.items)} items")
    print(f"🏪 Vendors: {len(catalog.list_vendors())}")
    print("✅ API ready at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down Procurement Agent API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
