from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os

# Make project root importable
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from myimpact.assembler import (
    assemble_prompt,
    discover_scales,
    discover_levels,
    discover_orgs,
)

# Azure OpenAI (optional)
AOAI_ENABLED = bool(
    os.getenv("AZURE_OPENAI_ENDPOINT")
    and os.getenv("AZURE_OPENAI_API_KEY")
    and os.getenv("AZURE_OPENAI_DEPLOYMENT")
)
client = None
if AOAI_ENABLED:
    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        )
    except Exception:
        AOAI_ENABLED = False

app = FastAPI(
    title="MyImpact API",
    version="0.1.0",
    description="Generate SMART goal prompts aligned to culture, Radford levels, and org themes. "
    "Primary mode: Returns prompts for users to paste into their LLM of choice. "
    "Optional: Direct Azure OpenAI integration if credentials configured.",
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
    scale: str = Field(..., examples=["technical", "leadership"])
    level: str = Field(..., examples=["L30", "L80"])
    growth_intensity: str = Field(..., examples=["minimal", "moderate", "aggressive"])
    org: str = Field("demo", examples=["demo"])
    theme: Optional[str] = Field(None, description="Optional strategic theme bias")
    goal_style: str = Field("independent", examples=["independent", "progressive"])


@app.get("/api/metadata")
def get_metadata():
    return {
        "scales": discover_scales(),
        "levels": {s: discover_levels(s) for s in discover_scales()},
        "growth_intensities": ["minimal", "moderate", "aggressive"],
        "goal_styles": ["independent", "progressive"],
        "organizations": discover_orgs(),
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/goals/generate")
def generate_goals(payload: GenerateRequest):
    """
    Generate goal prompts for the specified context.

    **Primary Use**: Returns crafted prompts (system + user) for copying into any LLM.

    **Optional Azure OpenAI**: If AZURE_OPENAI_ENDPOINT configured, also returns
    LLM-generated goals in the 'result' field. Otherwise, 'result' is null.
    """
    # Assemble prompts
    system_prompt, user_context = assemble_prompt(
        payload.scale,
        payload.level,
        payload.growth_intensity,
        payload.org,
        payload.theme,
        payload.goal_style,
    )

    result_text = None

    if AOAI_ENABLED and client is not None:
        try:
            # Higher temperature for creativity per MVP
            completion = client.chat.completions.create(
                model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                temperature=float(os.getenv("GEN_TEMPERATURE", 0.9)),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context},
                ],
            )
            result_text = completion.choices[0].message.content
        except Exception as e:
            # Fallback to returning prompts if AOAI call fails
            raise HTTPException(status_code=502, detail=f"Azure OpenAI error: {e}")

    return {
        "inputs": payload.model_dump(),
        "prompts": [system_prompt, user_context],  # Return as list, not tuple
        "result": result_text,  # May be None if AOAI isn't configured
        "powered_by": "Azure OpenAI" if AOAI_ENABLED else "prompts-only",
    }
