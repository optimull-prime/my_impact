# MyImpact Cloud Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INTERNET (OpenSpace Demo)                   │
└────────────────┬──────────────────────────────────────────────────────┘
                 │
         ┌───────┴──────────┐
         │                  │
    ┌────▼────┐      ┌─────▼─────┐
    │ Browser │      │ Browser   │
    │ Demo    │      │ Mobile    │
    └────┬────┘      └─────┬─────┘
         │                  │
         └───────┬──────────┘
                 │ HTTPS
         ┌───────▼─────────────────────┐
         │  Azure Static Web Apps       │
         │  (myimpact-demo.azureSWA)    │
         │  webapp/ directory           │
         │  ✓ index.html                │
         │  ✓ js/api.js                 │
         │  ✓ js/app.js                 │
         │  FREE tier: 100GB bandwidth  │
         └───────┬─────────────────────┘
                 │
                 │ HTTP Request
                 │ /api/goals/generate
                 │ /api/metadata
                 │
         ┌───────▼──────────────────────────┐
         │  Azure Container Apps            │
         │  (myimpact-demo-api.region.ACA)  │
         │  Consumption Plan                │
         │  ✓ 0.5 vCPU, 1 GB RAM            │
         │  ✓ Auto-scale: 1-3 replicas      │
         │  ✓ Port 8000 (FastAPI/Uvicorn)   │
         │  ✓ Health checks every 30s       │
         │  ✓ Rate limiting: 10 req/min     │
         │  ✓ CORS configured               │
         └───────┬──────────────────────────┘
                 │
                 │ Pull Image
                 │
         ┌───────▼─────────────────────┐
         │  Azure Container Registry    │
         │  (myimpactdemo[ID].ACR)      │
         │  Standard SKU - $5/month     │
         │  Stores:                     │
         │  ✓ myimpact-api:latest       │
         │  ✓ myimpact-api:sha[commit]  │
         └─────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline (GitHub)                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Developer pushes code to main branch                                │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────┐                            │
│  │ GitHub Actions Workflows Triggered  │                            │
│  └──────────┬────────────────┬─────────┘                            │
│             │                │                                       │
│  ┌──────────▼──────┐  ┌──────▼──────────┐                           │
│  │ Test Backend    │  │ Build & Deploy  │                           │
│  │ (test-backend)  │  │ Backend         │                           │
│  │                 │  │ (deploy-backend)│                           │
│  │ • Linting       │  │                 │                           │
│  │ • Unit tests    │  │ • Build Docker  │                           │
│  │ • Coverage      │  │ • Push to ACR   │                           │
│  │ • Py 3.10,11,12│  │ • Deploy to ACA │                           │
│  │ • 77 tests ✓   │  │ • Health check  │                           │
│  └─────────────────┘  └────────┬────────┘                           │
│                                │                                     │
│                  ┌─────────────▼──────────┐                          │
│                  │ Deploy Frontend        │                          │
│                  │ (deploy-frontend)      │                          │
│                  │                        │                          │
│                  │ • Deploy to SWA        │                          │
│                  │ • Branch previews      │                          │
│                  │ • Auto-HTTPS           │                          │
│                  └────────────────────────┘                          │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘


                    Infrastructure Deployment
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │        Bicep Templates (IaC)              │
    ├───────────────────────────────────────────┤
    │ • main.bicep - Core resources             │
    │ • deploy.bicep - Subscription wrapper     │
    │                                           │
    │ Deploy one-time:                          │
    │ az deployment group create \              │
    │   --template-file main.bicep              │
    └───────────────────────────────────────────┘
```

---

## Data Flow: Form Submission

```
User in Browser (webapp)
        │
        ▼
webapp/index.html renders form
        │
        ▼
User fills out form:
- Scale (technical, leadership)
- Level (L30-35, L36-40, etc.)
- Growth Intensity (minimal, moderate, aggressive)
- Organization (demo, ...)
- Optional Focus Area
        │
        ▼
User clicks "Generate Goals"
        │
        ▼
webapp/js/app.js calls api.generate()
        │
        ▼
HTTPS POST to /api/goals/generate
https://<CONTAINER_APP_FQDN>/api/goals/generate
        │
        ▼
Rate Limiter checks:
- IP address
- Request count in last minute
- If > 10: Return 429 (Too Many Requests)
- If ≤ 10: Continue
        │
        ▼
FastAPI validates input (GenerateRequest model)
        │
        ▼
myimpact.assembler.assemble_prompt()
        │
        ├─ Load culture expectations CSV (scale)
        ├─ Extract levels
        ├─ Get user level culture data
        ├─ Load organization focus areas
        └─ Assemble prompts (framework + user context)
        │
        ▼
Return JSON response:
{
  "inputs": {...},
  "framework": "System prompt with culture context...",
  "user_context": "User-specific context...",
  "result": null,
  "powered_by": "prompts-only"
}
        │
        ▼
webapp/js/app.js receives response
        │
        ▼
Display prompts in UI
        │
        ▼
User copies to clipboard
        │
        ▼
User pastes into their LLM (ChatGPT, Claude, etc.)
```

---

## Deployment Sequence Timeline

```
Day 2, 8:00 AM: START
    │
    ├─ 8:00-8:30: Azure Setup
    │   ├─ Create Service Principal
    │   ├─ Create ACR
    │   ├─ Create Container Apps Env
    │   └─ Get credentials
    │
    ├─ 8:30-8:40: GitHub Secrets Config
    │   ├─ Add AZURE_CREDENTIALS
    │   ├─ Add AZURE_REGISTRY_*
    │   ├─ Add CONTAINER_APP_*
    │   └─ Verify all 7 secrets
    │
    ├─ 8:40-8:45: Push Code
    │   ├─ git add .
    │   ├─ git commit -m "Deploy: ..."
    │   └─ git push origin main
    │
    ├─ 8:45-8:55: Workflows Run
    │   ├─ 8:45: Test Backend starts (parallel)
    │   ├─ 8:45: Deploy Backend starts (parallel)
    │   ├─ 8:50: Backend deployed to ACA
    │   ├─ 8:50: Deploy Frontend starts
    │   ├─ 8:52: Frontend deployed to SWA
    │   └─ 8:55: All workflows complete ✓
    │
    ├─ 8:55-9:00: Verification
    │   ├─ curl /api/health
    │   ├─ Test rate limiting
    │   ├─ Open browser to SWA URL
    │   └─ Test form submission
    │
    └─ 9:00: READY FOR OPENSPACE! 🚀
       ✓ Backend: Deployed & tested
       ✓ Frontend: Live & responsive
       ✓ Rate limiting: Active
       ✓ URL ready to share
```

---

## Cost Model

```
┌─────────────────────────────────────────────────────┐
│           AZURE CONSUMPTION PLAN PRICING            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  vCPU-seconds: $0.000011 per vCPU-second           │
│  Memory GB-seconds: $0.000006 per GB-second        │
│                                                     │
│  Container App Configuration:                       │
│  • 0.5 vCPU allocated                              │
│  • 1.0 GB RAM allocated                            │
│  • Only billed when running (idle = $0)            │
│                                                     │
│  Example 1 hour demo session:                       │
│  ─────────────────────────────────────             │
│  • 100 requests average                            │
│  • Each request: ~500ms (0.5 vCPU, 1 GB)           │
│  • Compute: 50 vCPU-seconds × $0.000011 = $0.0005  │
│  • Memory: 50 GB-seconds × $0.000006 = $0.0003     │
│  • Total: <$0.001 per demo session                 │
│                                                     │
│  Monthly estimate (if running 24/7):               │
│  ─────────────────────────────────────             │
│  • ACR: $5                                         │
│  • Container Apps: ~$10-15                         │
│  • Static Web Apps: $0 (FREE)                      │
│  • Total: ~$15-20/month                            │
│                                                     │
│  Note: Includes free tier limits:                  │
│  • First 1,000,000 vCPU-seconds: FREE              │
│  • First 512 MB RAM-seconds: FREE                  │
│  • 100 GB bandwidth: FREE                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│           SECURITY LAYERS                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Layer 1: Network                              │
│  • HTTPS only (TLS/SSL enforced)               │
│  • DDoS Protection (Azure basic tier)          │
│  • CORS whitelist                              │
│                                                 │
│  Layer 2: Application                          │
│  • Rate limiting (10 req/min per IP)           │
│  • Input validation (Pydantic models)          │
│  • Error handling (no stack traces to client)  │
│                                                 │
│  Layer 3: Container                            │
│  • Non-root user (appuser UID 1000)            │
│  • Health checks (auto-restart on failure)     │
│  • Multi-stage Docker build (smaller images)   │
│                                                 │
│  Layer 4: Secrets Management                   │
│  • GitHub Secrets (encrypted)                  │
│  • No secrets in code/git history              │
│  • Azure Managed Identity (future)             │
│                                                 │
│  Layer 5: Infrastructure                       │
│  • Resource group isolation                    │
│  • ACR private (registry-only access)          │
│  • Container Apps Env (isolated network)       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Scaling Behavior

```
Load Test: 100 requests in 10 seconds
      │
      ▼
  ┌─────────────┐
  │ 1 replica   │ (minimum)
  │ 0.5 vCPU    │
  │ 1 GB RAM    │
  │ ~10 req/sec │
  │ Healthy ✓   │
  └─────────────┘
      │
      │ (Need more capacity)
      ▼
  ┌─────────────┐
  │ 2 replicas  │
  │ 0.5 vCPU ea │
  │ 1 GB RAM ea │
  │ ~20 req/sec │
  │ Healthy ✓   │
  └─────────────┘
      │
      │ (Still under load)
      ▼
  ┌─────────────┐
  │ 3 replicas  │ (maximum)
  │ 0.5 vCPU ea │
  │ 1 GB RAM ea │
  │ ~30 req/sec │
  │ Healthy ✓   │
  └─────────────┘

Configuration in main.bicep:
scale: {
  minReplicas: 1
  maxReplicas: 3
  rules: [
    {
      name: 'http-requests'
      threshold: '100'
    }
  ]
}
```

---

## Monitoring & Observability

```
┌──────────────────────────────────────┐
│      GitHub Actions Status           │
│  • Real-time workflow logs           │
│  • Test results per matrix           │
│  • Deployment status                 │
│  • Workflow duration                 │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│    Azure Container Apps Portal       │
│  • Health status (Healthy/Unhealthy) │
│  • Replica count (current)           │
│  • Resource utilization              │
│  • Restart history                   │
│  • Container logs (streaming)        │
│  • Ingress configuration             │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   Future: Azure Monitor/App Insights │
│  • Request metrics                   │
│  • Performance analytics             │
│  • Custom metrics                    │
│  • Alerting rules                    │
│  • Dashboards                        │
└──────────────────────────────────────┘
```

---

This architecture is:
✅ **Scalable** - Auto-scales to handle traffic  
✅ **Reliable** - Health checks & auto-restart  
✅ **Secure** - Multi-layer security  
✅ **Cost-Effective** - Consumption-based pricing  
✅ **Observable** - Logs & metrics included  
✅ **Maintainable** - Infrastructure as Code  
✅ **Automated** - GitHub Actions CI/CD  

**Perfect for an OpenSpace demo! 🚀**
