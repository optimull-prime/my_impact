#  Quick Start Guide (5 Minutes)

Welcome to MyImpact! This guide gets you up and running locally in minutes.

## Prerequisites

- Python 3.10+ installed
- Git

## Setup (5 Minutes)

### Step 0: Create Virtual Environment (First Time Only)

If you haven't created a virtual environment yet:

```powershell
# Windows PowerShell
python -m venv .venv

# macOS/Linux
python3 -m venv .venv
```

This creates a `.venv` folder in your project directory. You only need to do this once.

### Step 1: Activate Virtual Environment

```powershell
# Windows PowerShell
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -e ".[api,dev]"
```

### Step 3: Start Backend API (Terminal 1)

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 4: Start Frontend (Terminal 2)

```bash
cd webapp
python -m http.server 8080
```

### Step 5: Open in Browser

Visit: **http://localhost:8080**

You should see the MyImpact landing page! 🎉

---

## What You'll See

1. **Landing Page** - Hero section with value propositions
2. **Input Form** - 6 dropdown/radio fields
3. **Results Section** - Two collapsible cards with prompts
4. **Copy Buttons** - Copy-to-clipboard functionality

---

## Test It

1. **Fill the form**:
   - Select a scale (e.g., "technical")
   - Select a level (e.g., "L30–35 (Career)")
   - Select growth intensity (e.g., "moderate")
   - Select organization (e.g., "demo")
   - Click "Generate Prompt"

2. **Watch the loading spinner** appear while the API processes

3. **View the results** - Two collapsible sections with goal framework prompt and user context

4. **Copy buttons** - Click to copy prompts to clipboard

---

## File Locations

| File | Purpose |
|------|---------|
| `webapp/index.html` | Frontend landing page + form |
| `webapp/js/app.js` | Form logic and results display |
| `webapp/js/api.js` | API client wrapper |
| `api/main.py` | FastAPI backend (CORS + endpoints) |

---

## Verify Everything Works

### Test API Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"healthy","version":"0.1.0"}
```

### Test Metadata

```bash
curl http://localhost:8000/api/metadata | python -m json.tool
```

Expected response:
```json
{
  "scales": ["technical", "leadership"],
  "levels": {
    "technical": ["L10–15 (Entry)", ...],
    "leadership": [...]
  },
  "growth_intensities": ["minimal", "moderate", "aggressive"],
  "goal_styles": ["independent", "progressive"],
  "organizations": ["demo"]
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 8000 already in use** | Change port: `uvicorn api.main:app --reload --port 8001` |
| **"Cannot find module" error** | Activate venv: `.\.venv\Scripts\activate` |
| **Frontend shows empty dropdowns** | Ensure API is running on `http://localhost:8000` |
| **CORS error in browser console** | Verify API CORS middleware is enabled (it is!) |
| **"Connection refused"** | Make sure both API (8000) and Frontend (8080) are running |

For more help, see [02-local-development.md](02-local-development.md).

---

## Next Steps

1. **Got it working?** → Proceed to [02-local-development.md](02-local-development.md) for detailed setup
2. **Ready to deploy?** → Go to [03-deployment.md](03-deployment.md)
3. **Want API docs?** → See [docs/api/](../api/)
4. **Want to understand the architecture?** → See [docs/architecture/](../architecture/)

---

## What's Next After Quick Start?

### To Develop
→ Read [02-local-development.md](02-local-development.md)

### To Deploy to Azure
→ Read [03-deployment.md](03-deployment.md)

### To Understand the Code
→ Read [docs/architecture/overview.md](../architecture/overview.md)