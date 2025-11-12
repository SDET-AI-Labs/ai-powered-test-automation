"""
Locator Repair REST API
=======================

FastAPI-based microservice for AI-powered locator healing.

This allows the repair service to be deployed independently and
consumed by ANY framework through HTTP requests.

Architecture Benefits:
- Language-agnostic (not just Python)
- Independent deployment
- Horizontal scaling
- Load balancing ready
- Easy monitoring and logging

Usage:
    # Start server
    uvicorn services.locator_repair.api:app --reload --port 8000
    
    # Make requests
    curl -X POST http://localhost:8000/api/repair \
      -H "Content-Type: application/json" \
      -d '{
        "framework": "playwright",
        "page_source": "<html>...</html>",
        "failed_locator": "button#wrong",
        "context_hint": "Submit button"
      }'
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional
import uvicorn

from .repair_service import LocatorRepairService, RepairResponse


# ============================================================================
# API Models (Request/Response)
# ============================================================================

class RepairRequestAPI(BaseModel):
    """API request model for locator repair."""
    framework: Literal["playwright", "selenium"] = Field(
        ...,
        description="Framework type (playwright or selenium)"
    )
    page_source: str = Field(
        ...,
        description="HTML content of the page",
        max_length=50000  # Limit to prevent abuse
    )
    failed_locator: str = Field(
        ...,
        description="The locator that failed",
        max_length=1000
    )
    context_hint: str = Field(
        default="",
        description="Optional hint about what element we're looking for",
        max_length=500
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "framework": "playwright",
                "page_source": "<html><button id='submit'>Submit</button></html>",
                "failed_locator": "button#wrong_id",
                "context_hint": "Submit button"
            }
        }


class RepairResponseAPI(BaseModel):
    """API response model for locator repair."""
    success: bool
    original_locator: str
    repaired_locator: Optional[str]
    framework: str
    confidence: str
    timestamp: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "original_locator": "button#wrong_id",
                "repaired_locator": "button#submit",
                "framework": "playwright",
                "confidence": "high",
                "timestamp": "2025-11-11T12:00:00.000000",
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Locator Repair Microservice",
    description="AI-powered locator healing for web automation frameworks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow all origins for microservice)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service (singleton)
repair_service = LocatorRepairService()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - service info."""
    return {
        "status": "online",
        "service": "Locator Repair Microservice",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Locator Repair Microservice",
        "version": "1.0.0"
    }


@app.post("/api/repair", response_model=RepairResponseAPI)
async def repair_locator(request: RepairRequestAPI):
    """
    Repair a broken locator using AI.
    
    This is the main endpoint for locator healing.
    
    Args:
        request: RepairRequestAPI with framework, page_source, failed_locator, context_hint
        
    Returns:
        RepairResponseAPI with repaired locator or error
        
    Example:
        POST /api/repair
        {
            "framework": "playwright",
            "page_source": "<html>...</html>",
            "failed_locator": "button#wrong",
            "context_hint": "Submit button"
        }
    """
    try:
        # Call repair service
        result = repair_service.repair_locator(
            framework=request.framework,
            page_source=request.page_source,
            failed_locator=request.failed_locator,
            context_hint=request.context_hint
        )
        
        # Convert to API response
        return RepairResponseAPI(
            success=result.success,
            original_locator=result.original_locator,
            repaired_locator=result.repaired_locator,
            framework=result.framework,
            confidence=result.confidence,
            timestamp=result.timestamp,
            error=result.error
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/repairs/recent")
async def get_recent_repairs(limit: int = 10):
    """
    Get recent repair attempts for analytics.
    
    Args:
        limit: Number of recent repairs to return (default: 10)
        
    Returns:
        List of recent repair attempts
    """
    try:
        repairs = repair_service.get_recent_repairs(limit=limit)
        return {"repairs": repairs, "count": len(repairs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """
    Get repair service statistics.
    
    Returns:
        Statistics about repairs (success rate, framework breakdown, etc.)
    """
    try:
        repairs = repair_service.get_recent_repairs(limit=100)
        
        if not repairs:
            return {
                "total_repairs": 0,
                "success_rate": 0,
                "by_framework": {}
            }
        
        # Calculate statistics
        total = len(repairs)
        successful = sum(1 for r in repairs if r.get("success", False))
        by_framework = {}
        
        for repair in repairs:
            framework = repair.get("framework", "unknown")
            if framework not in by_framework:
                by_framework[framework] = {"total": 0, "successful": 0}
            by_framework[framework]["total"] += 1
            if repair.get("success", False):
                by_framework[framework]["successful"] += 1
        
        return {
            "total_repairs": total,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "by_framework": by_framework
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Locator Repair Microservice")
    print("=" * 80)
    print()
    print("📝 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("🔧 Repair Endpoint: POST http://localhost:8000/api/repair")
    print()
    print("=" * 80)
    
    uvicorn.run(
        "services.locator_repair.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
