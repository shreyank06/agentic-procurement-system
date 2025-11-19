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

# Load catalog at startup
catalog_path = Path(__file__).parent.parent / "catalog.json"
catalog = Catalog(str(catalog_path))


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

        # Check if OpenAI is selected but no API key
        import os
        import sys
        api_key_to_use = request.api_key
        if request.llm_provider.lower() == "openai" and not request.api_key:
            # Use environment variable as fallback
            api_key_to_use = os.getenv("OPENAI_API_KEY")
            # Force output to appear in logs immediately
            print(f"DEBUG: Checking OPENAI_API_KEY from env: {api_key_to_use is not None}", flush=True)
            print(f"DEBUG: All env vars containing OPENAI: {[k for k in os.environ.keys() if 'OPENAI' in k]}", flush=True)
            sys.stdout.flush()
            if not api_key_to_use:
                print(f"DEBUG: OPENAI_API_KEY not found in environment!", flush=True)
                raise HTTPException(
                    status_code=400,
                    detail=f"OpenAI API key is required. Env vars found: {[k for k in os.environ.keys() if 'OPENAI' in k]}"
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


@app.post("/api/negotiate")
async def run_negotiation(request: NegotiationRequest):
    """
    Run multi-agent negotiation for selected item.

    Returns negotiation transcript and verdict.
    """
    try:
        result = negotiate_procurement(
            selected_item=request.selected_item,
            request=request.request
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation failed: {str(e)}")


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
