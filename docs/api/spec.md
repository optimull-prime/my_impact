# MyImpact — API Specification

## Overview
This document describes the REST API endpoints for MyImpact goal generation service.

Base URL: `http://localhost:8000` (development)

---

## POST /api/generate

Generate SMART quarterly goals based on role expectations and growth intensity.

### Request Body
```json
{
  "tenant_id": "string",
  "position_id": "string", 
  "level_code": "string",
  "growth_intensity": "minimal" | "moderate" | "aggressive",
  "user_context": "string (optional)"
}
```

### Parameters
- **tenant_id** (required): Tenant identifier (e.g., "myorg")
- **position_id** (required): Job family code (e.g., "SWE", "PM", "DS")
- **level_code** (required): Career level (e.g., "L3", "L4", "L5")
- **growth_intensity** (required): Growth trajectory preference
  - `minimal`: Sustaining current level performance
  - `moderate`: Balanced growth toward next level
  - `aggressive`: Accelerated advancement focus
- **user_context** (optional): Additional context about the user's current projects, interests, or constraints

### Response
```json
{
  "goals": [
    {
      "category": "string",
      "goal": "string",
      "rationale": "string",
      "smart_evaluation": {
        "specific": "string",
        "measurable": "string",
        "achievable": "string",
        "relevant": "string",
        "time_bound": "string"
      }
    }
  ],
  "metadata": {
    "tenant_id": "string",
    "position_id": "string",
    "level_code": "string",
    "growth_intensity": "string",
    "timestamp": "string (ISO 8601)",
    "model": "string",
    "total_goals": "integer"
  }
}
```

### Process Flow
1. **Resolve expectation profile**: Load culture expectations (technical/leadership) for the specified level
2. **Assemble prompt**: Combine system prompt with user context and expectations
3. **Call Azure OpenAI**: Use GPT-4 to generate 6-9 SMART quarterly goals
4. **Parse & validate**: Extract structured JSON response with goals and SMART evaluations
5. **Return**: Goals with metadata for tracking and audit

### Example Request
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "radford",
    "position_id": "SWE",
    "level_code": "L4",
    "growth_intensity": "moderate",
    "user_context": "Working on distributed systems and mentoring junior engineers"
  }'
```

### Error Responses
- **400 Bad Request**: Invalid parameters or missing required fields
- **404 Not Found**: Tenant or expectation profile not found
- **500 Internal Server Error**: LLM invocation or processing error

---

## GET /health

Health check endpoint for service monitoring.

### Response
```json
{
  "status": "healthy"
}
```

---

## Future Endpoints (Planned)

### POST /api/goals/refine
**Status**: Not yet implemented

Inputs:
- `goal_set_id`: Identifier for existing goal set
- `operations`: Array of refinement operations
  - `tighten_metric`: Make metrics more specific
  - `split_goal`: Divide goal into sub-goals
  - `merge_goals`: Combine related goals
  - `adjust_growth_intensity`: Recalibrate difficulty

Process:
- Apply deterministic transforms; re-evaluate SMART criteria
- Optionally call LLM for phrasing improvements

### GET /api/goals/export
**Status**: Not yet implemented

Inputs:
- `goal_set_id`: Identifier for goal set
- `format`: `markdown` | `csv` | `json`

Process:
- Render goals in requested format
- Return as downloadable file

---

## Architecture Notes

- **LLM Provider**: Azure OpenAI (GPT-4 via `openai` SDK)
- **Configuration**: Environment variables (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`)
- **Data Sources**: CSV files in `data/` directory for culture expectations
- **Prompt Assembly**: Uses [`myimpact/assembler.py`](../../myimpact/assembler.py) module
- **Web Framework**: FastAPI with CORS enabled for local development

---

## Security Considerations

- API keys stored in environment variables (never committed)
- CORS configured for localhost during development
- Input validation on all parameters
- LLM outputs parsed defensively with error handling

---

## Testing

See [`tests/test_api.py`](../../tests/test_api.py) for API integration tests.

```bash
# Run API tests
pytest tests/test_api.py -v

# Start development server
uvicorn api.main:app --reload --port 8000
```
