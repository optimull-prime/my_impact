# OpenSpace Day 2: Deployment Checklist & Quick Commands

## ⏱️ Timeline: ~1 hour total

---

## Phase 1: Azure Setup (30 minutes)

### Before Starting
- [ ] Have Azure subscription ready
- [ ] Have Azure CLI installed
- [ ] Save this file locally for reference

### Commands to Run

```bash
# 1. Set variables (customize these)
SUBSCRIPTION_ID="<your-subscription-id>"
RESOURCE_GROUP_NAME="myimpact-demo-rg"
AZURE_REGION="eastus"
REGISTRY_NAME="myimpactdemo$(date +%s)"
ENV_NAME="myimpact-demo-env"

# 2. Login to Azure
az login
az account set --subscription "$SUBSCRIPTION_ID"

# 3. Create resource group
az group create \
  --name "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"

# 4. Create Container Registry
az acr create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$REGISTRY_NAME" \
  --sku Standard \
  --location "$AZURE_REGION"

# 5. Create Container Apps Environment
az containerapp env create \
  --name "$ENV_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"

# 6. Create Service Principal for CI/CD
az ad sp create-for-rbac \
  --name "myimpact-ci-cd" \
  --role "Contributor" \
  --scopes "/subscriptions/$SUBSCRIPTION_ID" \
  --json-auth > azure-credentials.json

# 7. Get Container Registry credentials
az acr credential show \
  --name "$REGISTRY_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

### Save These Values
From the output above, copy and save:
- `loginServer` → `AZURE_REGISTRY_LOGIN_SERVER`
- `username` → `AZURE_REGISTRY_USERNAME`
- `password` → `AZURE_REGISTRY_PASSWORD`
- Full JSON from `azure-credentials.json` → `AZURE_CREDENTIALS`

---

## Phase 2: GitHub Secrets (10 minutes)

### Go to Your Repository
1. GitHub → Settings → Secrets and variables → Actions
2. Click "New repository secret"

### Add These 7 Secrets

| Secret Name | Value |
|---|---|
| `AZURE_CREDENTIALS` | Full JSON from azure-credentials.json |
| `AZURE_RESOURCE_GROUP` | myimpact-demo-rg |
| `AZURE_REGISTRY_LOGIN_SERVER` | From Step 7 above |
| `AZURE_REGISTRY_USERNAME` | From Step 7 above |
| `AZURE_REGISTRY_PASSWORD` | From Step 7 above |
| `CONTAINER_APP_NAME` | myimpact-demo-api |
| `CONTAINER_APPS_ENV` | myimpact-demo-env |

---

## Phase 3: Automatic Deployment (5-10 minutes)

### Deploy Everything
```bash
git add .
git commit -m "Deploy: Add rate limiting and CI/CD"
git push origin main
```

### Monitor Deployment
1. Go to GitHub → Actions tab
2. Watch workflows run:
   - `Deploy Backend to Azure Container Apps` (~5 min)
   - `Deploy Frontend to Azure Static Web Apps` (~2 min)

### Get Your URLs
Once deployed:

```bash
# Backend URL
az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.configuration.ingress.fqdn' \
  -o tsv

# Frontend URL  
az staticwebapp show \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'defaultHostname' \
  -o tsv
```

---

## Phase 4: Verification (5 minutes)

### Test Backend Health
```bash
curl https://<YOUR_API_URL>/api/health
# Expected: {"status":"healthy","version":"0.1.0"}
```

### Test Rate Limiting (10 requests/min)
```bash
# Run this multiple times in a terminal loop
for i in {1..15}; do
  curl -X POST https://<YOUR_API_URL>/api/goals/generate \
    -H "Content-Type: application/json" \
    -d '{"scale":"technical","level":"L30–35 (Career)","growth_intensity":"moderate","org":"demo"}'
  sleep 0.5
done
# After 10 requests, should see: 429 Too Many Requests
```

### Test Frontend
```bash
# Open in browser
https://<YOUR_STATIC_APP_URL>

# Should see the form load
```

### Update Frontend API Endpoint
Before showing at openspace, update [webapp/js/api.js](webapp/js/api.js):

```javascript
// Find this line:
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://myimpact-demo.azurestaticapps.net';

// Replace with your actual Container App URL
// Then push to trigger frontend redeploy
```

---

## Troubleshooting Quick Fixes

### "Resource already exists"
```bash
# Delete and recreate
az group delete --name myimpact-demo-rg --yes --no-wait
# Then re-run the setup commands above
```

### Workflow fails with "Unable to authenticate"
- Check `AZURE_CREDENTIALS` secret - must be valid JSON
- Try recreating service principal: `az ad sp create-for-rbac...`

### Container App won't start
```bash
# View logs
az containerapp logs show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --container myimpact-api \
  --follow
```

### CORS errors in browser
- Backend URLs in [api/main.py](api/main.py) CORS config
- Static Web Apps URL must be in allow_origins list
- Push to main to redeploy backend

---

## 🎯 Show Time at OpenSpace

Share this URL:
```
https://<YOUR_STATIC_APP_URL>
```

Demo includes:
✅ Live form (no local CLI needed!)  
✅ Real backend API calls  
✅ Copy-to-clipboard functionality  
✅ Rate limiting protection  
✅ Mobile-friendly responsive design  

---

## 📞 Help & Reference

- Full guide: [infra/CI_CD_DEPLOYMENT_GUIDE.md](infra/CI_CD_DEPLOYMENT_GUIDE.md)
- Cost calculator: ~$15-20/month (~$0.50 for demo)
- Tests: All 77 passing ✅

**You've got this! 🚀**
