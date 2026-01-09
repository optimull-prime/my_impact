# MyImpact API (Phase 1)

## Overview
FastAPI server that exposes endpoints to generate goals and list configuration metadata. Uses Azure OpenAI when configured, otherwise returns assembled prompts only.

## Endpoints

### GET /api/metadata
Returns available scales, levels, growth intensities, goal styles, and organizations.

Response:
```json
{
  "scales": ["technical", "leadership"],
  "levels": {"technical": ["L10–15 (Entry)", ...], "leadership": ["L70–75 (Director)", ...]},
  "growth_intensities": ["minimal", "moderate", "aggressive"],
  "goal_styles": ["independent", "progressive"],
  "organizations": ["demo"]
}
```

### POST /api/goals/generate
Generates goals using the prompt assembler and Azure OpenAI (if configured).

Request body:
```json
{
  "scale": "technical",
  "level": "L30",
  "growth_intensity": "moderate",
  "org": "demo",
  "framework": "Standardize for Speed and Interchangeability",
  "goal_style": "independent"
}
```

Response:
```json
{
  "inputs": { /* echo of request */ },
  "prompts": { "framework": "...", "user": "..." },
  "result": "... goal text ...",
  "powered_by": "Azure OpenAI" | "prompts-only"
}
```

## Run Locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server (from repo root):
```bash
uvicorn api.main:app --reload
```

Optional: Configure Azure OpenAI via environment or `.env`:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION` (default: 2024-08-01-preview)
- `GEN_TEMPERATURE` (default: 0.9)
