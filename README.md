# MyImpact

AI-ready quarterly goal generation aligned to company culture, Radford level expectations, and job-family competencies.

## Overview

**MyImpact** generates context-rich prompts to help employees create quarterly SMART goals aligned to:
- **Company cultural principles** (8 attributes: humble, hardworking, continuous learner, world-class, transparency, improvement, respect, ownership)
- **Level expectations** (technical L10–L35+, leadership L70–L100+)
- **Organizational themes** (strategic priorities, focus areas, org level context)

The primary use case is **generating prompts to copy into any LLM** (ChatGPT, Claude, Gemini, etc.) for personalized goal generation.

---

## 🚀 Getting Started

Choose your path based on what you want to do:

### I want to try it quickly (5 minutes)
→ [**Quick Start Guide**](docs/guides/01-quick-start.md)

Set up locally and test the web app in 5 minutes.

### I want to develop locally
→ [**Local Development Guide**](docs/guides/02-local-development.md)

Complete setup guide for developers, with debugging tips and troubleshooting.

### I want to deploy to Azure
→ [**Deployment Guide**](docs/guides/03-deployment.md)

Step-by-step instructions for deploying frontend to Azure Static Web Apps and backend to Azure Container Apps.

### I want to understand the system design
→ [**Architecture Overview**](docs/architecture/overview.md)

System design, component breakdown, data model, and scalability considerations.

### I want to integrate with the API
→ [**API Reference**](docs/api/README.md)

Endpoints, request/response schemas, and integration examples in curl, Python, and JavaScript.

---

## Project Structure

```
myimpact/
├── docs/                              # 📚 All documentation
│   ├── guides/                        # Step-by-step guides
│   │   ├── 01-quick-start.md          # 5-minute setup (START HERE!)
│   │   ├── 02-local-development.md    # Full dev guide
│   │   └── 03-deployment.md           # Deploy to Azure
│   ├── api/                           # API reference
│   │   └── README.md                  # Endpoints, schemas, examples
│   ├── architecture/                  # Technical design
│   │   └── overview.md                # System architecture
│   └── planning/                      # Phase planning docs
│       ├── README.md
│       ├── PHASE_0_1_STATUS.md
│       ├── PHASE_2_BUILD_SUMMARY.md
│       ├── PHASE_2_COMPLETE.md
│       └── PHASE_2_README.md
│
├── myimpact/                          # 🐍 Python package
│   ├── assembler.py                   # Prompt generation logic
│   └── cli.py                         # Command-line interface
│
├── api/                               # 🚀 FastAPI application
│   └── main.py                        # API endpoints
│
├── webapp/                            # 🌐 Static web app
│   ├── index.html                     # Single-page app
│   ├── staticwebapp.config.json       # Azure SWA config
│   └── js/
│       ├── app.js                     # Main logic
│       └── api.js                     # API client
│
├── data/                              # 📊 Culture expectations
│   ├── culture_expectations_technical.csv
│   └── culture_expectations_leadership.csv
│
├── tests/                             # ✅ Test suite
│   ├── test_assembler.py
│   ├── test_api.py
│   └── test_cli.py
│
├── infra/                             # ☁️ Infrastructure (Bicep templates)
│   ├── bicep/                         # IaC definitions
│   └── README.md
│
├── pyproject.toml                     # Python dependencies
├── Dockerfile                         # Container image
├── CONTRIBUTING.md                    # Contributing guidelines
└── LICENSE.txt

```

---

## Quick Reference

### For Users
- **Try it**: [Quick Start Guide](docs/guides/01-quick-start.md)
- **Deploy it**: [Deployment Guide](docs/guides/03-deployment.md)
- **Use the API**: [API Reference](docs/api/README.md)

### For Developers
- **Set up**: [Local Development Guide](docs/guides/02-local-development.md)
- **Understand it**: [Architecture Overview](docs/architecture/overview.md)
- **Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md)

### For the Project
- **Phase planning**: [docs/planning/](docs/planning/)
- **Infrastructure**: [infra/README.md](infra/README.md)

---

## Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML/CSS/JavaScript (Tailwind CSS) |
| **Backend** | Python 3.10+ (FastAPI, Uvicorn) |
| **Data** | CSV files (culture expectations) |
| **Deployment** | Azure Static Web Apps (frontend) + Azure Container Apps (backend) |
| **Containers** | Docker, Azure Container Registry |
| **Testing** | pytest |

---

## Installation

### Option 1: Quick Start (Recommended)
Follow the [Quick Start Guide](docs/guides/01-quick-start.md) for a 5-minute setup.

### Option 2: Full Development Setup
Follow the [Local Development Guide](docs/guides/02-local-development.md).

### Option 3: Deploy to Azure
Follow the [Deployment Guide](docs/guides/03-deployment.md).

---

## Commands

### Package Installation

```bash
# Install with API dependencies
pip install -e ".[api]"

# Install with dev dependencies (testing, formatting, etc.)
pip install -e ".[dev]"

# Install everything (API + Azure + dev)
pip install -e ".[api,dev,azure]"
```

### Running Locally

```bash
# Start the backend API (FastAPI)
uvicorn api.main:app --reload

# In another terminal, serve the frontend
cd webapp
python -m http.server 8080

# Visit http://localhost:8080
```

### Testing

```bash
pytest

# With coverage
pytest --cov=myimpact
```

### CLI

```bash
# List available options
myimpact list-options

# Generate independent goals (technical)
myimpact generate technical L30 moderate

# Generate progressive goals (leadership)
myimpact generate leadership L80 aggressive --org demo --goal-style progressive
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[LICENSE.txt](LICENSE.txt)

---

## Status

🔄 **Phase 2 (MVP)**: Web app demo complete, ready for feedback

See [docs/planning/](docs/planning/) for detailed phase planning and historical phase documents.
