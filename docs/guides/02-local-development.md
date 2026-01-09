# Local Development Guide

Complete guide for setting up MyImpact locally for development and testing.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ (optional, for HTTP server)
- Git
- A code editor (VS Code recommended)

## Project Structure

```
myimpact/
├── api/                          # FastAPI backend
│   └── main.py
├── webapp/                        # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── js/
│   │   ├── api.js               # API client
│   │   └── app.js               # Main app logic
│   └── staticwebapp.config.json  # Azure deployment config
├── myimpact/                      # Core library
│   ├── assembler.py             # Prompt assembly logic
│   └── cli.py                   # CLI interface
├── data/                          # Culture CSVs
├── prompts/                       # Org focus area & system prompt
├── Dockerfile                     # Container image
└── pyproject.toml
```

## Step 1: Set Up Python Environment

```bash
# Navigate to project root
cd myimpact

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies with API & dev tools
pip install -e ".[api,dev]"

# Verify installation
python -c "from myimpact import assembler; print('✓ myimpact installed')"
```

## Step 2: Start the Backend API

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Start FastAPI server with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Verify API is working

```bash
# In a new terminal
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","version":"0.1.0"}

curl http://localhost:8000/api/metadata
# Expected: JSON with scales, levels, orgs, etc.
```

## Step 3: Serve the Frontend

Choose one option:

### Option A: Python HTTP Server (Simplest)

```bash
# In another terminal, navigate to webapp
cd webapp

# Serve on port 8080
python -m http.server 8080

# Open: http://localhost:8080
```

### Option B: Node.js HTTP Server (Faster)

```bash
# One-time install
npm install -g http-server

# In webapp directory
cd webapp
http-server -p 8080

# Open: http://localhost:8080
```

### Option C: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"
3. Auto-opens `http://127.0.0.1:5500`

## Step 4: Test the Application

1. Open browser to `http://localhost:8080`
2. You should see the MyImpact landing page
3. Try the form:
   - Select a scale (e.g., "technical")
   - Select a level (e.g., "L30–35 (Career)")
   - Select growth intensity (e.g., "moderate")
   - Select organization (e.g., "demo")
   - Click "Generate Prompt"
4. Verify:
   - Loading spinner appears
   - Prompts are displayed
   - Copy buttons work

## Step 5: Run Tests

```bash
# Make sure venv is activated
.venv\Scripts\activate

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=myimpact

# Run specific test file
pytest tests/test_api.py -v
```

---

## Development Workflow

### Making Backend Changes

1. Edit `api/main.py` or `myimpact/` files
2. FastAPI `--reload` automatically restarts server (watch terminal)
3. Test with API calls:
   ```bash
   curl http://localhost:8000/api/goals/generate \
     -H "Content-Type: application/json" \
     -d '{"scale":"technical","level":"L30–35 (Career)","growth_intensity":"moderate","org":"demo"}'
   ```
4. Verify tests still pass: `pytest`

### Making Frontend Changes

1. Edit files in `webapp/` (HTML, CSS, JS)
2. Refresh browser (Ctrl+R / Cmd+R) to see changes
3. Check browser console (F12) for JavaScript errors
4. Test form submission and copy functionality

### Testing CORS Locally

Frontend at `http://localhost:8080` calls API at `http://localhost:8000`

CORS is already enabled in `api/main.py` for local dev. If you get a CORS error:

1. Verify API is running on `8000`
2. Verify frontend is on an allowed origin (localhost:8080, 5173, 3000, etc.)
3. Check browser console for exact error message
4. Restart both servers if changed CORS config

---

## Debugging

### Backend Debugging

**Add logging**:
```python
# In api/main.py
@app.post("/api/goals/generate")
def generate_goals(payload: GenerateRequest):
    print(f"DEBUG: Received payload: {payload}")  # Will appear in terminal
    # ... rest of function
```

Check terminal where FastAPI is running.

**Interactive debugging with pdb**:
```python
import pdb

@app.post("/api/goals/generate")
def generate_goals(payload: GenerateRequest):
    pdb.set_trace()  # Execution pauses here
    # ... rest of function
```

Then use pdb commands: `n` (next), `c` (continue), `l` (list), `p variable` (print)

### Frontend Debugging

Use browser Developer Tools (F12 / Cmd+Option+I):

1. **Console tab** → Check for JavaScript errors
2. **Network tab** → View API requests/responses
3. **Sources tab** → Set breakpoints and step through code
4. **Elements tab** → Inspect HTML and CSS

**Example: View API request**
1. Open DevTools → Network tab
2. Click "Generate Prompt" in app
3. Look for POST request to `/api/goals/generate`
4. Click to see request body and response

---

## Troubleshooting

### "Connection refused" – Can't reach API

**Problem**: Frontend shows error connecting to backend

**Solution**:
```bash
# 1. Verify API is actually running
curl http://localhost:8000/api/health

# 2. If not, start it
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 3. Check api.js has correct endpoint
# Look at: webapp/js/api.js line with API_BASE_URL
```

### CORS error in browser console

**Problem**: "Cross-Origin Request Blocked" message

**Solution**:
1. Verify frontend is on `localhost:8080` (or another allowed origin)
2. Check `webapp/js/api.js` for correct `API_BASE_URL`:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost'
       ? 'http://localhost:8000'
       : window.location.origin + '/api'
   ```
3. Restart both servers if you edited CORS config

### Form dropdowns are empty

**Problem**: Scale, Level, Org dropdowns show no options

**Solution**:
1. Check browser console (F12) for errors
2. Test metadata endpoint:
   ```bash
   curl http://localhost:8000/api/metadata | python -m json.tool
   ```
   Should return scales, levels, orgs, etc.
3. Verify `initializeApp()` is called in browser console
4. Clear browser cache: Ctrl+Shift+Del, clear all

### "Module not found" Python error

**Problem**: `ImportError: No module named 'myimpact'`

**Solution**:
```bash
# 1. Ensure virtual environment is activated
.venv\Scripts\activate

# 2. Install package in editable mode
pip install -e ".[api,dev]"

# 3. Verify it works
python -c "from myimpact.assembler import assemble_prompt; print('✓')"
```

### Port already in use

**Problem**: `Address already in use` when starting API or frontend

**Solution**:
```bash
# Use a different port
uvicorn api.main:app --reload --port 8001

# Or find and kill process using port 8000
# On Windows:
netstat -ano | findstr :8000

# On macOS/Linux:
lsof -i :8000
```

---

## Optional: Environment Variables

For Azure OpenAI integration (optional), create `.env` in project root:

```bash
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
GEN_TEMPERATURE=0.9
```

Then start FastAPI as usual – it will load `.env` automatically.

---

## Performance Tips

### Slow API responses?

1. Check system resources (CPU, RAM) with Task Manager
2. Verify data files are loaded (check `myimpact/assembler.py`)
3. If using Azure OpenAI, expect 2-3 seconds for LLM response

### Slow frontend?

1. Check browser console for JavaScript errors
2. Disable browser extensions (can block requests)
3. Check Network tab for slow requests
4. Try in incognito/private mode to rule out cache issues

---

## Useful Commands

```bash
# Backend
uvicorn api.main:app --reload                      # Start API with hot reload
uvicorn api.main:app --reload --port 8001          # Start on different port
pytest                                             # Run all tests
pytest tests/test_api.py -v                       # Run specific test
pytest tests/ --cov=myimpact                      # Run with coverage
pip list                                           # Show installed packages
pip install -e ".[api,dev]"                        # Reinstall dependencies

# Frontend
cd webapp && python -m http.server 8080            # Simple HTTP server
cd webapp && npx http-server -p 8080               # Node.js HTTP server

# API Testing
curl http://localhost:8000/api/health              # Health check
curl http://localhost:8000/api/metadata            # List all options
python -c "import requests; print(requests.get('http://localhost:8000/api/health').json())"

# Cleanup
deactivate                                         # Deactivate venv
rm -rf .venv                                       # Remove venv
pip cache purge                                    # Clear pip cache
```

---

## Getting Help

1. **Check backend logs**: Look at terminal where `uvicorn` is running
2. **Check frontend logs**: Browser Console (F12 → Console tab)
3. **Check network**: Browser DevTools → Network tab
4. **Check documentation**: See [../guides/03-deployment.md](03-deployment.md) for deployment help

---

## Next Steps

→ Ready to deploy? See [03-deployment.md](03-deployment.md)

→ Want to understand the architecture? See [../architecture/overview.md](../architecture/overview.md)
