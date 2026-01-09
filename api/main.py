from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from myimpact.assembler import (
    assemble_prompt,
    discover_levels,
    discover_orgs,
    discover_scales,
    load_org_focus_areas,
)

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
async def generate_prompts(request: GenerateRequest):
    """Generate goal-setting prompts"""
    try:
        framework_prompt, user_context = assemble_prompt(
            scale=request.scale,
            level=request.level,
            growth_intensity=request.growth_intensity,
            org_name=request.org or "demo",
            goal_style=request.goal_style or "independent",
            focus_area=request.focus_area or None,
        )

        return {
            "inputs": {
                "scale": request.scale,
                "level": request.level,
                "growth_intensity": request.growth_intensity,
                "org": request.org or "demo",
                "goal_style": request.goal_style or "independent",
                "focus_area": request.focus_area,
            },
            "prompts": [framework_prompt, user_context],
            "framework": framework_prompt,
            "user_context": user_context,
            "result": None,
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
