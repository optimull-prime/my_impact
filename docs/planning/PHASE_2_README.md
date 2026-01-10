> **Note**: This is the initial project plan created at the start of Phase 2. For a comparison of plan vs. actual implementation, compare this document against the current repository state.

# MyImpact Phase 2: Culture-Aligned Goal Generator

**Status**: MVP Demo Phase (Ready for Testing)

## What is MyImpact?

MyImpact is a web application that generates personalized, **culture-aligned career goals**. Users input their context (level, intensity, org focus areas) and receive carefully crafted prompts to paste into any LLM (ChatGPT, Claude, Gemini, etc.)—then get high-quality goals tailored to their company's culture and expectations.

## Key Features (Phase 2 MVP)

✅ **Job Level Aligned Goals** – Goals match your career level expectations (L10–L100+)  
✅ **Culture-Aware** – Reflects your organization's core principles  
✅ **LLM-Agnostic** – Works with ChatGPT, Claude, Gemini, or any LLM  
✅ **Locus of Control** – Goals focus on what you can influence  
✅ **Copy-to-Clipboard** – Instant copy for pasting into your LLM  
✅ **Mobile-Friendly** – Works on phones, tablets, and desktops  
✅ **Zero Setup** – No account or login required  

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Git

### 1. Clone and Setup

```bash
git clone <repo-url>
cd "Company Goal Builder"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -e .
```

### 2. Start Backend API

```bash
# Terminal 1
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Serve Frontend

```bash
# Terminal 2
cd webapp
python -m http.server 8080
```

### 4. Open App

Visit `http://localhost:8080` in your browser.

## How It Works

### User Journey

1. **Land on page** → See hero section with value propositions
2. **Fill form** → Select scale, level, intensity, org, focus area, style
3. **Click "Generate"** → System makes API call to backend
4. **View prompts** → framework prompt + User context shown in collapsible cards
5. **Copy prompts** → Click buttons to copy to clipboard
6. **Paste into LLM** → Open ChatGPT/Claude/Gemini, paste prompts, get goals

### Architecture

```
Frontend (Static Web App)          Backend (FastAPI)
  ↓                                   ↓
  HTML/CSS/JS                    api/main.py
  (Tailwind)                     ↓
  ↓                              assemble_prompt()
  Vanilla JS, no build           ↓
  ↓                              Load culture CSVs
  HTTPS requests                 Load org focus areas
  (CORS enabled)                 Load framework prompt
                                 Return [framework, user]
```

## Project Structure

```
├── api/
│   └── main.py                      # FastAPI backend
├── webapp/                           # Frontend
│   ├── index.html                   # Single-page app
│   ├── js/
│   │   ├── api.js                   # API client
│   │   └── app.js                   # App logic
│   └── staticwebapp.config.json     # Azure deployment
├── myimpact/
│   ├── assembler.py                 # Prompt assembly
│   └── cli.py                       # Command-line interface
├── data/
│   ├── culture_expectations_technical.csv
│   └── culture_expectations_leadership.csv
├── prompts/
│   ├── org_focus_areas_demo.md
│   ├── org_focus_areas_hc.md
│   └── goal_generation_framework_prompt.txt
├── tests/
│   ├── test_api.py
│   ├── test_assembler.py
│   └── test_cli.py
├── Dockerfile                       # Container image
├── LOCAL_DEVELOPMENT.md             # Dev guide
└── README.md                        # This file
```

## API Endpoints

### `GET /api/metadata`
Returns available scales, levels, orgs, intensities, and goal styles.

**Response**:
```json
{
  "scales": ["technical", "leadership"],
  "levels": {
    "technical": ["L10–15 (Entry)", "L20–25 (Developing)", ...],
    "leadership": [...]
  },
  "growth_intensities": ["minimal", "moderate", "aggressive"],
  "goal_styles": ["independent", "progressive"],
  "organizations": ["demo", "hc"]
}
```

### `POST /api/goals/generate`
Generates goal prompts based on user inputs.

**Request**:
```json
{
  "scale": "technical",
  "level": "L30–35 (Career)",
  "growth_intensity": "moderate",
  "org": "demo",
  "focus_area": "Cloud Migration",
  "goal_style": "independent"
}
```

**Response**:
```json
{
  "inputs": { ... },
  "prompts": [
    "Goal framework prompt text...",
    "User context text..."
  ],
  "result": null,
  "powered_by": "prompts-only"
}
```

### `GET /api/health`
Health check for deployment monitoring.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Deployment

### Frontend: Azure Static Web Apps

- Free tier: 100 GB bandwidth/month, automatic HTTPS
- Auto-deploy from GitHub on push
- See: `infra/AZURE_STATIC_WEB_APPS_DEPLOYMENT.md`

```bash
az staticwebapp create \
  --name myimpact-demo \
  --resource-group myimpact-demo \
  --source https://github.com/<owner>/<repo> \
  --branch main \
  --location eastus \
  --login-with-github
```

### Backend: Azure Container Apps

- Serverless containers, pay-per-use pricing
- Auto-scaling (0-3 replicas for demo)
- See: `infra/AZURE_CONTAINER_APPS_DEPLOYMENT.md`

```bash
# Build and push image
docker build -t myimpact-api:latest .
az acr login --name myimpactacr
docker push myimpactacr.azurecr.io/myimpact-api:latest

# Deploy to Container Apps
az containerapp create \
  --name myimpact-api \
  --resource-group myimpact-demo \
  --environment myimpact-env \
  --image myimpactacr.azurecr.io/myimpact-api:latest \
  --target-port 8000 \
  --ingress external
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=myimpact

# Run specific test
pytest tests/test_api.py -v
```

## Configuration

### Culture & Levels

Culture expectations are defined in CSV files:
- `data/culture_expectations_technical.csv`
- `data/culture_expectations_leadership.csv`

Each file maps:
- Cultural Attribute → Level (L10, L20, L30, ...) → Expectation

Example:
```csv
Cultural Attribute,L10,L20,L30
Ownership,"Ask for help","Take initiative","Own outcomes"
```

### Organization Focus Areas

Org-specific focus areas (Markdown files):
- `prompts/org_focus_areas_demo.md`
- `prompts/org_focus_areas_hc.md`

Include strategic focus areas and context relevant to the organization.

### Goal Framework Prompt

Base framework prompt for goal generation:
- `prompts/goal_generation_framework_prompt.txt`

Used for all goal generation requests.

## Environment Variables (Optional)

For Azure OpenAI integration:

```bash
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<api-key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
GEN_TEMPERATURE=0.9
```

If not set, API returns prompts only (no LLM-generated goals).

## Performance & Scalability

### Local Development
- API: Responds in <100ms (culture CSV lookup)
- Frontend: Instant (vanilla JS, CDN CSS)

### Production (Azure)
- Frontend: <2s page load (100 KB HTML/CSS/JS)
- API: <1s prompt generation, <3s if using Azure OpenAI
- Scaling: Automatic (0-3 replicas for demo traffic)

## Browser Support

- ✅ Chrome/Chromium (90+)
- ✅ Firefox (88+)
- ✅ Safari (14+)
- ✅ Edge (90+)
- ✅ Mobile browsers

## Accessibility

- ✅ Keyboard navigable (Tab through form, Enter to submit)
- ✅ Form labels linked to inputs
- ✅ Error messages inline with fields
- ⚠️ WCAG AA compliance: In progress for Phase 3

## Troubleshooting

### Frontend can't reach API
1. Verify API is running: `curl http://localhost:8000/api/health`
2. Check `API_BASE_URL` in `webapp/js/api.js`
3. Verify CORS is enabled in `api/main.py`

### Tests failing
```bash
# Reinstall dependencies
pip install -e .

# Run tests with verbose output
pytest tests/ -v

# Check Python version
python --version  # Should be 3.10+
```

### "Module not found" errors
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate

# Reinstall package
pip install -e .
```

See `LOCAL_DEVELOPMENT.md` for detailed troubleshooting.

## Future Enhancements (Phase 3+)

🔮 **LLM Integration**
- "Open in ChatGPT" button (pre-fill prompts)
- "Open in Claude" button
- "Generate with Azure OpenAI" button

🔮 **Personalization**
- OAuth login (Azure AD B2C)
- Save/load prompt history
- User preferences (default level, org, etc.)

🔮 **Admin Features**
- Edit culture CSVs via web UI
- Manage org focus areas
- Preview changes before publishing

🔮 **Analytics**
- Track form submissions
- Monitor copy events
- Error tracking (Azure Application Insights)

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run tests: `pytest tests/`
4. Commit and push: `git push origin feature/my-feature`
5. Open a pull request

## Security

- No user authentication required (public demo)
- HTTPS enforced in production
- CORS configured for specific origins
- Input validation on all form fields
- No sensitive data stored or logged

## Cost Estimates (Monthly)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Static Web Apps | 100 GB bandwidth | $0 |
| Container Apps | Up to ~3000 requests/month | ~$15 (0.5 CPU, 1 GB RAM, 3 replicas) |
| **Total** | | ~**$15/month** |

## License

See [LICENSE.txt](LICENSE.txt)

## Support

- **Documentation**: See `LOCAL_DEVELOPMENT.md`, `PHASE_2_DESIGN.md`
- **Issues**: Open GitHub issue
- **Questions**: Check Q&A in docs/

## Getting Started

1. **For Development**: See `LOCAL_DEVELOPMENT.md`
2. **For Deployment**: See `infra/AZURE_STATIC_WEB_APPS_DEPLOYMENT.md` and `infra/AZURE_CONTAINER_APPS_DEPLOYMENT.md`
3. **For Architecture**: See `docs/PHASE_2_DESIGN.md`

---

**Built with ❤️ to help people grow.**
