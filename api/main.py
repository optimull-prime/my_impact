from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from myimpact.assembler import assemble_prompt, discover_levels, discover_orgs, discover_scales

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
    theme: Optional[str] = Field(None, description="Optional emphasis / focus theme")
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


@app.post("/api/goals/generate", tags=["Goals"])
async def generate_prompts(request: GenerateRequest):
    system_prompt, user_context = assemble_prompt(
        scale=request.scale,
        level=request.level,
        growth_intensity=request.growth_intensity,
        org_name=request.org,
        theme=request.theme,
        goal_style=request.goal_style,
    )

    return {
        "inputs": request.model_dump(),
        "prompts": [system_prompt, user_context],
        "result": None,
        "powered_by": "prompts-only",
    }
