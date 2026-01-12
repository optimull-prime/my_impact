from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from myimpact.assembler import (
    assemble_prompt,
    discover_levels,
    discover_orgs,
    discover_scales,
    load_org_focus_areas,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MyImpact API",
    description="Generate culture- and level-aligned prompts for quarterly SMART goal creation",
    version="0.1.0",
    contact={
        "name": "MyImpact Team",
    },
    license_info={
        "name": "MIT",
    },
)

# Attach limiter to app state
app.state.limiter = limiter

# Add SlowAPI middleware for rate limiting enforcement
app.add_middleware(SlowAPIMiddleware)

from fastapi.responses import Response

# Custom exception handler for RateLimitExceeded
async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": str(exc)},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myimpact-demo.azurestaticapps.net",  # Production
        "https://*.azurestaticapps.net",  # Azure Static Web Apps branch previews
        "http://localhost:3000",  # Local dev (frontend)
        "http://localhost:8080",  # Local dev (alternative port)
        "http://localhost:5173",  # Local dev (Vite, if upgraded later)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Request model for prompt generation."""

    scale: str = Field(..., description="Scale/track", examples=["technical", "leadership"])
    level: str = Field(..., description="Job level label", examples=["L30–35 (Career)"])
    growth_intensity: str = Field(
        ..., description="Growth intensity", examples=["minimal", "moderate", "aggressive"]
    )
    org: str = Field("demo", description="Organization name", examples=["demo"])
    focus_area: Optional[str] = Field(None, description="Optional emphasis / focus areas")
    goal_style: str = Field(
        "independent", description="Goal style", examples=["independent", "progressive"]
    )


# Endpoints
@app.get("/api/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "version": app.version}


@app.get("/api/metadata", tags=["Metadata"])
async def metadata():
    scales = discover_scales()
    levels = {scale: discover_levels(scale) for scale in scales}
    return {
        "scales": scales,
        "levels": levels,
        "growth_intensities": ["minimal", "moderate", "aggressive"],
        "goal_styles": ["independent", "progressive"],
        "organizations": discover_orgs(),
    }


@app.get("/api/orgs/{org_name}/focus-areas", tags=["Metadata"])
async def get_org_focus_areas(org_name: str):
    """Get strategic focus areas for an organization."""
    try:
        content = load_org_focus_areas(org_name)
        return {"content": content}
    except FileNotFoundError:
        return {"content": None}


@app.post("/api/goals/generate")
@limiter.limit("10/minute")
async def generate_prompts(request: Request, data: GenerateRequest):
    """Generate goal-setting prompts.
    
    Returns a JSON object containing:
    - framework: The system/instruction prompt.
    - user_context: The data-driven context for the specific user.
    - powered_by: Indicates the generation engine ("prompts-only" for when copy only enabled).
    """
    try:
        framework_prompt, user_context = assemble_prompt(
            scale=data.scale,
            level=data.level,
            growth_intensity=data.growth_intensity,
            org_name=data.org or "demo",
            goal_style=data.goal_style or "independent",
            focus_area=data.focus_area or None,
        )

        return {
            "inputs": {
                "scale": data.scale,
                "level": data.level,
                "growth_intensity": data.growth_intensity,
                "org": data.org or "demo",
                "goal_style": data.goal_style or "independent",
                "focus_area": data.focus_area,
            },
            # modern structured format
            "framework": framework_prompt,
            "user_context": user_context,
            "result": None,
            "powered_by": "prompts-only",
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
