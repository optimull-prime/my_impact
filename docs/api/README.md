# API Reference

Complete reference for MyImpact API endpoints.

## Base URL

```
Local Development: http://localhost:8000
Production (Azure): https://<container-app-name>.azurecontainerapps.io
```

## Authentication

**Current Phase 2 MVP**: No authentication required. All endpoints are public.

(Future: Will add JWT-based authentication for user data persistence)

---

## Endpoints

### Health Check

#### `GET /api/health`

Health check for load balancers and monitoring.

**Request**:
```bash
curl http://localhost:8000/api/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Use Case**: Container Apps health probes, monitoring dashboards

---

### Metadata

#### `GET /api/metadata`

Fetch form metadata (scales, levels, intensities, goal styles, organizations).

Used by frontend to populate dropdowns dynamically.

**Request**:
```bash
curl http://localhost:8000/api/metadata
```

**Response** (200 OK):
```json
{
  "scales": [
    "technical",
    "leadership"
  ],
  "levels": {
    "technical": [
      "L10–15 (Entry)",
      "L20–25 (Developing)",
      "L30–35 (Career)",
      "L35+ (Principal)"
    ],
    "leadership": [
      "L70–75 (Director)",
      "L80–85 (VP)",
      "L90–95 (SVP)",
      "L100+ (C-Suite)"
    ]
  },
  "growth_intensities": [
    "minimal",
    "moderate",
    "aggressive"
  ],
  "goal_styles": [
    "independent",
    "progressive"
  ],
  "organizations": [
    "demo"
  ]
}
```

**Frontend Usage**:

```javascript
// Fetch on page load
const metadata = await fetch('/api/metadata').then(r => r.json());

// Populate Scale dropdown
document.getElementById('scale-select').innerHTML = metadata.scales
  .map(s => `<option>${s}</option>`)
  .join('');

// When Scale changes, populate Level dropdown
document.getElementById('scale-select').addEventListener('change', (e) => {
  const scale = e.target.value;
  const levels = metadata.levels[scale];
  document.getElementById('level-select').innerHTML = levels
    .map(l => `<option>${l}</option>`)
    .join('');
});
```

---

### Goal Generation

#### `POST /api/goals/generate`

Generate culture-aligned goal prompts based on user inputs.

**Request**:

```bash
curl -X POST http://localhost:8000/api/goals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scale": "technical",
    "level": "L30–35 (Career)",
    "growth_intensity": "moderate",
    "org": "demo",
    "focus_area": "Cloud Architecture",
    "goal_style": "independent"
  }'
```

**Request Schema**:

| Field | Type | Required | Values | Example |
|-------|------|----------|--------|---------|
| `scale` | string | ✅ | "technical", "leadership" | "technical" |
| `level` | string | ✅ | From `/api/metadata.levels[scale]` | "L30–35 (Career)" |
| `growth_intensity` | string | ✅ | "minimal", "moderate", "aggressive" | "moderate" |
| `org` | string | ✅ | From `/api/metadata.organizations` | "demo" |
| `focus_area` | string | ❌ | Any text (bias for goal generation) | "Cloud Architecture" |
| `goal_style` | string | ✅ | "independent", "progressive" | "independent" |

**Response** (200 OK):

```json
{
  "inputs": {
    "scale": "technical",
    "level": "L30–35 (Career)",
    "growth_intensity": "moderate",
    "org": "demo",
    "focus_area": "Cloud Architecture",
    "goal_style": "independent"
  },
  "prompts": [
    "You are an expert goal generation system specializing in career development...",
    "Scale: Technical (Individual Contributor)\nLevel: L30–35 (Career)\nIntensity: Moderate growth\n\nOrganization Focus Areas:\n- Innovation\n- Ownership\n- Excellence\n\nCultural Expectations:\n- Drives technical direction...\n..."
  ],
  "result": null,
  "powered_by": "prompts-only"
}
```

**Response Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `inputs` | object | Echo of request (for confirmation) |
| `prompts` | array[2] | `[system_prompt, user_context]` |
| `result` | null | Reserved for future LLM integration |
| `powered_by` | string | "prompts-only" (or "llm" when integrated) |

**Error Responses**:

**400 Bad Request** (Invalid Input):
```json
{
  "detail": [
    {
      "loc": ["body", "level"],
      "msg": "ensure this value is in ('L10–15 (Entry)', 'L20–25 (Developing)', ...)",
      "type": "value_error.enum"
    }
  ]
}
```

**Example Bad Request**:
```bash
curl -X POST http://localhost:8000/api/goals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scale": "invalid",
    "level": "L30–35 (Career)",
    "growth_intensity": "moderate",
    "org": "demo",
    "goal_style": "independent"
  }'
# Returns 400 Bad Request
```

**500 Internal Server Error** (Server Exception):
```json
{
  "detail": "Internal server error. Please try again later."
}
```

---

## Frontend Integration

### Basic Integration

```javascript
// 1. Fetch metadata on page load
async function loadMetadata() {
  const response = await fetch('/api/metadata');
  const metadata = await response.json();
  
  // Populate dropdowns...
  populateScaleDropdown(metadata.scales);
}

// 2. Generate prompts on form submit
async function generatePrompts(formData) {
  const response = await fetch('/api/goals/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  
  if (!response.ok) {
    console.error('API error:', await response.json());
    return null;
  }
  
  const result = await response.json();
  return {
    systemPrompt: result.prompts[0],
    userContext: result.prompts[1]
  };
}

// 3. Copy to clipboard
async function copyToClipboard(text) {
  await navigator.clipboard.writeText(text);
  showToast('Copied to clipboard!');
}
```

### Handling Errors

```javascript
async function generateWithErrorHandling(formData) {
  try {
    const response = await fetch('/api/goals/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      if (response.status === 400) {
        showError('Invalid form input: ' + error.detail[0].msg);
      } else {
        showError('Server error. Please try again.');
      }
      return null;
    }
    
    const result = await response.json();
    return result;
  } catch (err) {
    console.error('Network error:', err);
    showError('Connection error. Check your internet.');
    return null;
  }
}
```

---

## CORS & Local Development

### CORS Headers

In production, the backend includes CORS headers:

```
Access-Control-Allow-Origin: https://<static-web-app>.azurestaticapps.net
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Local Development

For local development, all origins are allowed (see `api/main.py`):

```python
allow_origins=[
    "http://localhost:3000",      # npm dev server
    "http://localhost:8080",      # http.server
    "http://localhost:5173",      # Vite dev server
]
```

**Testing with curl**:

```bash
# Test from command line (doesn't care about CORS)
curl -X POST http://localhost:8000/api/goals/generate \
  -H "Content-Type: application/json" \
  -d '{...}'

# Test from browser (respects CORS)
# Open DevTools and run the JavaScript from above
```

---

## Rate Limiting

**Current Phase 2**: No rate limiting.

(Future: May add rate limiting for production usage)

---

## Versions & Changelog

### Version 0.1.0 (Current)

- `GET /api/health` - Health check
- `GET /api/metadata` - Form metadata
- `POST /api/goals/generate` - Goal prompt generation
- CORS enabled
- No authentication
- No rate limiting

---

## Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Metadata
curl http://localhost:8000/api/metadata | python -m json.tool

# Generate goals
curl -X POST http://localhost:8000/api/goals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scale": "technical",
    "level": "L30–35 (Career)",
    "growth_intensity": "moderate",
    "org": "demo",
    "focus_area": "Cloud Architecture",
    "goal_style": "independent"
  }' | python -m json.tool
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
resp = requests.get(f"{BASE_URL}/api/health")
print(resp.json())

# Metadata
metadata = requests.get(f"{BASE_URL}/api/metadata").json()
print(metadata)

# Generate goals
payload = {
    "scale": "technical",
    "level": "L30–35 (Career)",
    "growth_intensity": "moderate",
    "org": "demo",
    "focus_area": "Cloud Architecture",
    "goal_style": "independent"
}
result = requests.post(f"{BASE_URL}/api/goals/generate", json=payload).json()
print(result["prompts"][0])  # System prompt
print(result["prompts"][1])  # User context
```

### Using JavaScript (in browser)

```javascript
const BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://<production-url>';

// Health check
fetch(`${BASE_URL}/api/health`)
  .then(r => r.json())
  .then(d => console.log(d));

// Generate goals
fetch(`${BASE_URL}/api/goals/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scale: 'technical',
    level: 'L30–35 (Career)',
    growth_intensity: 'moderate',
    org: 'demo',
    goal_style: 'independent'
  })
})
  .then(r => r.json())
  .then(d => console.log(d.prompts[0]));
```

---

## OpenAPI/Swagger Documentation

The API automatically exposes interactive OpenAPI docs:

**Swagger UI**: `http://localhost:8000/docs`

**ReDoc**: `http://localhost:8000/redoc`

Visit these URLs to:
- See all endpoints
- View request/response schemas
- Test endpoints interactively (with Try It Out)

---

## Troubleshooting

### 502 Bad Gateway

**Cause**: Backend service is down or unreachable

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# If local development:
# - Is uvicorn running? Check terminal for errors
# - Did you install dependencies? pip install -e ".[api,dev]"

# If production:
# - Check Container Apps logs: az containerapp logs show --name myimpact-api ...
```

### CORS Error: "Access to XMLHttpRequest... blocked by CORS policy"

**Cause**: Frontend origin is not in CORS allow list

**Solution** (local development):
- Frontend running on unexpected port? Check `api/main.py` allow_origins list
- Add your local frontend URL to CORS config

**Solution** (production):
- Check that Static Web Apps domain matches CORS allow list
- Redeploy backend with updated CORS origins

### 400 Bad Request

**Cause**: Invalid request payload

**Solution**:
- Check that all required fields are present
- Verify field values match enum values from `/api/metadata`
- Use `/api/metadata` to see valid values

---

## FAQ

**Q: Can I call the API from JavaScript in my browser?**

A: Yes! CORS is enabled. See the JavaScript example above.

**Q: Do I need an API key?**

A: Not in Phase 2 MVP. All endpoints are public.

**Q: Can I cache API responses?**

A: `/api/metadata` is static and can be cached aggressively. `/api/goals/generate` responses can be cached by user input hash.

**Q: Is there a webhook or real-time API?**

A: Not yet. Phase 3+ may add WebSocket support.

---

## Next Steps

→ Ready to develop? See [02-local-development.md](02-local-development.md)

→ Want to deploy? See [03-deployment.md](03-deployment.md)

→ Want to understand the architecture? See [../architecture/overview.md](../architecture/overview.md)
