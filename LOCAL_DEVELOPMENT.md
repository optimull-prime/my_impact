# MyImpact Phase 2 - Local Development Guide

This guide covers running the MyImpact web app locally for development and testing.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ (optional, for HTTP server)
- Git
- A code editor (VS Code recommended)

## Project Structure

```
Company Goal Builder/
├── api/                          # FastAPI backend
│   └── main.py
├── webapp/                        # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── js/
│   │   ├── api.js               # API client
│   │   └── app.js               # Main app logic
│   ├── css/
│   │   └── style.css            # Custom styles (if needed)
│   └── staticwebapp.config.json  # Azure deployment config
├── myimpact/                      # Core library
│   ├── assembler.py             # Prompt assembly logic
│   └── ...
├── data/                          # Culture CSVs
├── prompts/                       # Org themes & system prompt
├── Dockerfile                     # Container image
└── pyproject.toml
```

## Step 1: Set Up Python Environment

```bash
# Navigate to project root
cd "MyImpact"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[api,dev]"

# Verify installation
python -c "from myimpact import assembler; print('✓ myimpact installed')"
```

## Step 2: Start the Backend API

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Test the API:
```bash
# In a new terminal
curl http://localhost:8000/api/health
# Expected response: {"status":"healthy","version":"0.1.0"}

curl http://localhost:8000/api/metadata
# Expected response: JSON with scales, levels, orgs, etc.
```

## Step 3: Serve the Frontend

You have two options:

### Option A: Using Python's built-in HTTP server (Simplest)

```bash
# In another terminal, navigate to webapp directory
cd webapp

# Serve on port 8080
python -m http.server 8080

# Now open: http://localhost:8080
```

### Option B: Using Node.js HTTP server (Faster)

```bash
# Install http-server globally (one-time)
npm install -g http-server

# In webapp directory
cd webapp
http-server -p 8080

# Now open: http://localhost:8080
```

### Option C: Using VS Code Live Server Extension

1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"
3. VS Code opens `http://127.0.0.1:5500`

## Step 4: Test the Application

1. Open browser to `http://localhost:8080` (or `5500` for Live Server)
2. You should see the MyImpact landing page
3. Scroll to the form and test:
   - Select a scale (e.g., "technical")
   - Select a level (e.g., "L30–35 (Career)")
   - Select growth intensity (e.g., "moderate")
   - Select organization (e.g., "demo")
   - Click "Generate Prompt"
4. Verify:
   - Loading spinner appears
   - Prompts are displayed
   - Copy buttons work (check browser console)

## Step 5: Run Tests

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=myimpact

# Run specific test file
pytest tests/test_api.py -v
```

## Development Workflow

### Making Backend Changes

1. Edit `api/main.py` or `myimpact/` files
2. FastAPI with `--reload` automatically restarts server
3. Test with API calls: `curl http://localhost:8000/api/...`
4. Verify tests still pass: `pytest`

### Making Frontend Changes

1. Edit files in `webapp/` (HTML, CSS, JS)
2. Refresh browser (Ctrl+R / Cmd+R) to see changes
3. Check browser console (F12) for any JavaScript errors
4. Test form submission and copy functionality

### Testing CORS Locally

The frontend (`http://localhost:8080`) calls the API (`http://localhost:8000`).

CORS is enabled for local development in `api/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    ...
]
```

If you get a CORS error:
1. Check that API is running on `8000`
2. Verify the frontend is on one of the allowed origins
3. Check browser console for the exact error

## Debugging

### Backend Debugging

Add breakpoints in `api/main.py`:

```python
# Example: log incoming request
@app.post("/api/goals/generate")
def generate_goals(payload: GenerateRequest):
    print(f"DEBUG: Received request: {payload}")  # ← Add logging
    # ... rest of function
```

Then check terminal output where FastAPI is running.

For advanced debugging, use **pdb**:

```python
import pdb

@app.post("/api/goals/generate")
def generate_goals(payload: GenerateRequest):
    pdb.set_trace()  # ← Execution pauses here
    # ... rest of function
```

Then use pdb commands in the terminal (n = next, c = continue, etc.)

### Frontend Debugging

Use browser Developer Tools (F12 / Cmd+Option+I):

1. **Console tab**: Check for JavaScript errors
2. **Network tab**: View API requests/responses
3. **Sources tab**: Set breakpoints and step through code
4. **Elements tab**: Inspect HTML and CSS

Example: View network request to API
1. Open DevTools → Network tab
2. Click "Generate Prompt"
3. Look for the POST request to `/api/goals/generate`
4. View the request/response JSON

## Troubleshooting

### "Connection refused" when frontend calls API

**Problem**: Frontend can't reach backend API
**Solution**:
```bash
# Verify API is running
curl http://localhost:8000/api/health

# If it fails, check that FastAPI is still running
# Start it: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### CORS error in browser console

**Problem**: "Cross-Origin Request Blocked"
**Solution**:
1. Verify frontend is running on `localhost:8080` (or allowed origin)
2. Verify `api.js` has correct `API_BASE_URL`:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost'
       ? 'http://localhost:8000'
       : ...
   ```
3. Restart both servers

### Form not populating dropdowns

**Problem**: Scale/Level/Org dropdowns are empty
**Solution**:
1. Check browser console for errors
2. Verify API `/api/metadata` endpoint works:
   ```bash
   curl http://localhost:8000/api/metadata | python -m json.tool
   ```
3. Check that `initializeApp()` is being called in browser console

### "Module not found" Python error

**Problem**: `ImportError: No module named 'myimpact'`
**Solution**:
```bash
# Install package in editable mode
pip install -e .

# Verify installation
python -c "from myimpact.assembler import assemble_prompt; print('✓')"
```

## Environment Variables (Optional)

For Azure OpenAI integration, create a `.env` file in project root:

```bash
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
GEN_TEMPERATURE=0.9
```

Then start FastAPI:
```bash
# Load .env and start API
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Performance Tips

### Slow API responses?

1. Check system resources (CPU, RAM) with Task Manager / Activity Monitor
2. Verify data files are loaded (check `myimpact/assembler.py`)
3. If using Azure OpenAI, add latency for API call (2-3 seconds is normal)

### Slow frontend?

1. Check browser console for JavaScript errors
2. Disable browser extensions (can interfere with requests)
3. Check network tab in DevTools for slow requests
4. Try in incognito/private mode

## Next Steps

1. **Test locally** following these steps
2. **Make code changes** as needed
3. **Run tests** to verify changes
4. **Deploy to Azure** (see deployment guides in `infra/`)

## Useful Commands

```bash
# Backend
uvicorn api.main:app --reload                      # Start API with hot reload
pytest                                             # Run tests
pytest tests/test_api.py -v                       # Run specific test file
pip list                                           # Show installed packages

# Frontend
cd webapp && python -m http.server 8080            # Simple HTTP server
cd webapp && npx http-server -p 8080               # Node.js HTTP server

# API Testing
curl http://localhost:8000/api/health              # Health check
curl http://localhost:8000/api/metadata            # Metadata endpoint

# Cleanup
deactivate                                         # Deactivate virtual environment
rm -rf .venv                                       # Remove virtual environment
```

## Getting Help

1. **Check logs**: 
   - Backend: Terminal where `uvicorn` is running
   - Frontend: Browser Console (F12)

2. **Check Network**:
   - Browser DevTools → Network tab
   - View request/response for API calls

3. **Re-read this guide**:
   - Most issues are covered in Troubleshooting section

4. **Check PHASE_2_DESIGN.md**:
   - Architecture and design overview
