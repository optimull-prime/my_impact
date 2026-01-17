# Deployment Guide

Deploy MyImpact to Azure with CI/CD pipelines in about 1 hour.

## Quick Overview

MyImpact deploys to two Azure services:
- **Backend API**: Azure Container Apps (auto-scales, consumption pricing)
- **Frontend**: Azure Static Web Apps (free tier, CDN included)

Total estimated cost: **$15-20/month** (or ~$0.10-0.50 for a demo)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Setup (30 min)](#azure-setup)
3. [GitHub Secrets (10 min)](#github-secrets)
4. [Deploy (5 min)](#deploy)
5. [Verify (5 min)](#verify)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## Prerequisites

Before starting, you need:

- **Azure Subscription** with Owner or Contributor permissions
- **GitHub Repository** (your fork of my_impact)
- **Azure CLI** ([install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **GitHub Account** with repository settings access
- **jq** (JSON parser) - optional but recommended

Verify tools:
```bash
az --version
gh --version
jq --version  # optional
```

---

## Azure Setup

### Step 1: Set Variables

```bash
# Customize these for your environment
SUBSCRIPTION_ID="<your-azure-subscription-id>"
RESOURCE_GROUP_NAME="myimpact-demo-rg"
AZURE_REGION="eastus"
REGISTRY_NAME="myimpactdemo$(date +%s)"
ENV_NAME="myimpact-demo-env"
STATIC_APP_NAME="myimpact-demo"
```

### Step 2: Login and Create Resource Group

```bash
# Login to Azure
az login
az account set --subscription "$SUBSCRIPTION_ID"

# Create resource group
az group create \
  --name "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"

# Get resource group ID (needed for scoped service principal)
RESOURCE_GROUP_ID=$(az group show \
  --name "$RESOURCE_GROUP_NAME" \
  --query id -o tsv)

echo "Resource group created: $RESOURCE_GROUP_NAME"
echo "Region: $AZURE_REGION"
```

### Step 3: Create Container Registry

```bash
# Create ACR with admin user disabled (security best practice)
az acr create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$REGISTRY_NAME" \
  --sku Standard \
  --location "$AZURE_REGION" \
  --admin-enabled false

echo "Container Registry created: $REGISTRY_NAME.azurecr.io"
```

### Step 4: Create Container Apps Environment

```bash
# Build image
docker build -t $ACR_NAME.azurecr.io/myimpact-api:latest .

# Login to Azure Container Registry
az acr login --name $ACR_NAME

# Push image
docker push $ACR_NAME.azurecr.io/myimpact-api:latest

# Verify it's there
az acr repository list --name $ACR_NAME
```

### Step 6: Create Service Principal for CI/CD

**Security**: Service principal is scoped to **resource group only** (not entire subscription). If credentials leak, damage is limited to this resource group.

```bash
# Create service principal scoped to resource group only
az ad sp create-for-rbac \
  --name "myimpact-ci-cd-demo" \
  --role "Contributor" \
  --scopes "$RESOURCE_GROUP_ID" \
  --json-auth > azure-credentials.json

echo "✅ Service principal created with resource group scope"
echo "📁 Credentials saved to: azure-credentials.json"
```

Save this JSON - you'll need it for GitHub Secrets in the next step.

### Step 7: Grant Service Principal AcrPush Role

The service principal only needs to push images, not manage ACR:

```bash
# Get ACR resource ID
ACR_ID=$(az acr show \
  --name "$REGISTRY_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query id -o tsv)

# Get service principal app ID
SP_APP_ID=$(cat azure-credentials.json | jq -r '.clientId')

# Grant AcrPush role (least privilege)
az role assignment create \
  --assignee "$SP_APP_ID" \
  --role "AcrPush" \
  --scope "$ACR_ID"

echo "✅ Service principal granted AcrPush role"
```

### Step 8: Optional - Use Federated Credentials for Production

For production, use OpenID Connect instead of long-lived secrets:

```bash
# Create app registration without secret
APP_ID=$(az ad app create \
  --display-name "myimpact-github-actions-federated" \
  --query appId -o tsv)

# Create service principal
SP_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)

# Create federated credential for GitHub Actions
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_ORG/my_impact:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Grant Contributor role
az role assignment create \
  --assignee "$SP_ID" \
  --role Contributor \
  --scope "$RESOURCE_GROUP_ID"

echo "✅ Federated credentials configured"
```

Then in GitHub Secrets, use `AZURE_TENANT_ID` and `AZURE_CLIENT_ID` instead of `AZURE_CREDENTIALS`.

---

## GitHub Secrets

### Add Repository Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below:

### Required Secrets

| Secret | Value | From |
|---|---|---|
| `AZURE_CREDENTIALS` | Full JSON from `azure-credentials.json` | Step 6 above |
| `AZURE_RESOURCE_GROUP` | `myimpact-demo-rg` | Created in Step 2 |
| `AZURE_REGISTRY_LOGIN_SERVER` | e.g., `myimpactdemo12345.azurecr.io` | Step 3 output |
| `CONTAINER_APP_NAME` | `myimpact-demo-api` | Workflow will create this |
| `CONTAINER_APPS_ENV` | `myimpact-demo-env` | Step 4 above |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token from Step 5 | Step 5 output (optional) |

### Example Azure Credentials Secret

Your `AZURE_CREDENTIALS` should look like:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxx~xxx-xxx.xxx_xxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### Security Reminder

**After adding secrets to GitHub**:
```bash
# Delete the local credentials file
rm azure-credentials.json
```

Never commit this file to version control.

---

## Deploy

### Automatic Deployment

Once secrets are configured, deployments happen automatically when you push:

```bash
# Commit your changes
git add .
git commit -m "Deploy: MyImpact to Azure"
git push origin main
```

GitHub Actions will:
1. Run tests (if any fail, deployment stops)
2. Build Docker image
3. Push to Azure Container Registry
4. Deploy to Azure Container Apps
5. Deploy frontend to Static Web Apps

### Monitor Deployment

Watch progress in GitHub:
1. Go to your repository
2. Click **Actions** tab
3. Watch the active workflows

Expected timeline:
- Test Backend: 2-3 minutes
- Build & Deploy Backend: 5-7 minutes
- Deploy Frontend: 2-3 minutes
- **Total**: ~10-15 minutes

---

## Verify

### Get Your URLs

Once deployment completes:

```bash
# Backend API URL
API_URL=$(az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.configuration.ingress.fqdn' \
  -o tsv)

echo "Backend API: https://$API_URL"

# Frontend URL
FRONTEND_URL=$(az staticwebapp show \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'defaultHostname' \
  -o tsv)

echo "Frontend: https://$FRONTEND_URL"
```

### Test Backend Health

```bash
curl https://$API_URL/api/health
# Expected: {"status":"healthy","version":"0.1.0"}
```

### Test Rate Limiting

Rate limiting is set to 10 requests/minute on the `/api/goals/generate` endpoint:

```bash
# Run this several times
for i in {1..15}; do
  response=$(curl -s -w "\n%{http_code}" -X POST https://$API_URL/api/goals/generate \
    -H "Content-Type: application/json" \
    -d '{
      "scale": "technical",
      "level": "L30-35",
      "growth_intensity": "moderate",
      "org": "demo",
      "goal_style": "independent"
    }')
  http_code=$(echo "$response" | tail -n1)
  echo "Request $i: HTTP $http_code"
  sleep 0.5
done
# After 10 requests, you should see: 429 Too Many Requests
```

### Test Frontend

Open your browser and visit: `https://$FRONTEND_URL`

You should see:
- ✅ MyImpact form loads
- ✅ All dropdowns work
- ✅ Submit button works (connects to backend)
- ✅ Generated prompt displays correctly

### Update Frontend API Endpoint

If the frontend is showing errors when calling the API, update the API endpoint:

Edit [webapp/js/api.js](../../webapp/js/api.js):

```javascript
// Find this section:
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://myimpact-demo.azurestaticapps.net';

// Replace with your actual Container App URL:
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://<YOUR_CONTAINER_APP_URL>';
```

Then push to trigger a frontend redeploy:
```bash
git add webapp/js/api.js
git commit -m "Update API endpoint to production"
git push origin main
```

### Verify Security Controls

```bash
# ✅ ACR admin user should be disabled
az acr show --name "$REGISTRY_NAME" --query adminUserEnabled
# Expected: false

# ✅ Container App should use Managed Identity
az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'identity.type'
# Expected: "SystemAssigned"

# ✅ Service principal should be resource-group scoped
az role assignment list --assignee "$SP_APP_ID" --all
# Should only show myimpact-demo-rg in scope
```

---

## Troubleshooting

### Workflow Fails: "Unable to authenticate to Azure"

**Cause**: Invalid or expired credentials

**Fix**:
```bash
# Check service principal still exists
az ad sp show --id <client-id>

# If not found, recreate:
az ad sp create-for-rbac \
  --name "myimpact-ci-cd-demo" \
  --role "Contributor" \
  --scopes "$RESOURCE_GROUP_ID" \
  --json-auth > azure-credentials.json

# Update AZURE_CREDENTIALS in GitHub Secrets with new JSON
```

### Container App Won't Start

**Cause**: Image failed to pull or application crashed

**Fix**:
```bash
# View detailed logs
az containerapp logs show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --container myimpact-api \
  --follow

# Check provisioning state
az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.provisioningState'

# Redeploy infrastructure (Managed Identity, health checks)
az deployment group create \
  --resource-group myimpact-demo-rg \
  --template-file infra/bicep/main.bicep \
  --parameters projectName=myimpact environment=demo
```

### Static Web App Won't Deploy

**Cause**: Deployment token expired or invalid

**Fix**:
```bash
# Get fresh deployment token
az staticwebapp secrets list \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'properties.apiKey' -o tsv

# Update AZURE_STATIC_WEB_APPS_API_TOKEN in GitHub Secrets
```

### CORS Errors in Browser

**Cause**: Frontend URL not in backend CORS allow-list

**Fix**:
```bash
# Find your Static Web App URL
az staticwebapp show \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'defaultHostname'

# Edit api/main.py - update allow_origins list:
# allow_origins=[
#     "https://myimpact-demo.azurestaticapps.net",  # Add your URL here
#     ...
# ]

# Commit and push to trigger backend redeploy
git add api/main.py
git commit -m "Fix: Update CORS allow_origins"
git push origin main
```

### "Resource already exists" Error

**Cause**: Resource name collision (registry names must be globally unique)

**Fix**:
```bash
# Delete resource group and try again with new names
az group delete --name myimpact-demo-rg --yes --no-wait

# After deletion completes (~5 min), recreate with new registry name
REGISTRY_NAME="myimpactdemo$(date +%s)"
# Then re-run Steps 2-7 above
```

### Test Failures Block Deployment

**Cause**: Tests fail in GitHub Actions

**Fix**:
```bash
# Run tests locally first
python -m pytest tests/ -v

# Fix any failing tests locally
# Commit and push when tests pass locally
git push origin main
```

---

## Architecture Overview

### Components

```
┌──────────────────────────────────────────────────────┐
│                    Users (Browser)                   │
│                 myimpact-demo.azureSWA               │
└────────────────────┬─────────────────────────────────┘
                     │ HTTPS
         ┌───────────▼──────────────┐
         │  Azure Static Web Apps    │
         │  (Frontend - FREE Tier)   │
         │                           │
         │  webapp/                  │
         │  ├── index.html           │
         │  ├── js/api.js            │
         │  └── js/app.js            │
         └───────────┬──────────────┘
                     │ HTTP /api/*
         ┌───────────▼──────────────────────┐
         │  Azure Container Apps            │
         │  (Backend API)                   │
         │                                  │
         │  FastAPI + slowapi               │
         │  • 0.5 vCPU, 1 GB RAM            │
         │  • Auto-scale: 1-3 replicas      │
         │  • Health checks every 30s       │
         │  • Rate limit: 10 req/min        │
         │  • CORS configured               │
         └───────────┬──────────────────────┘
                     │ Pull Image
         ┌───────────▼──────────────┐
         │  Azure Container Registry │
         │                           │
         │  Docker Images:           │
         │  • myimpact-api:latest    │
         │  • Managed Identity auth  │
         └───────────────────────────┘
```

### CI/CD Pipeline

```
Developer → git push → GitHub → GitHub Actions
                           │
              ┌────────────┼────────────┐
              │            │            │
           Test         Build      Deploy
           Unit        Docker     → ACR
          Tests        Build      → ACA
          Lint                    → SWA
           ✓
```

### Security

- ✅ **Managed Identity**: Container App uses Managed Identity to pull from ACR (no credentials)
- ✅ **Scoped Service Principal**: CI/CD service principal limited to resource group (not subscription)
- ✅ **Least Privilege RBAC**: Service principal has AcrPush role only (can't manage ACR settings)
- ✅ **Admin User Disabled**: ACR admin user is disabled (further reduces credential surface)
- ✅ **Health Checks**: Automatic restart if container unhealthy
- ✅ **Rate Limiting**: 10 requests/minute on expensive endpoints

---

## Costs

| Resource | SKU | Monthly Cost |
|---|---|---|
| Container Apps | Consumption (0.5 CPU, 1 GB) | $10-15 |
| Container Registry | Standard | $5 |
| Static Web Apps | Free | $0 |
| **Total** | | **$15-20/month** |

For a demo event (1-2 hours): ~$0.10-0.50

---

## Clean Up

To delete all resources and stop incurring costs:

```bash
# Delete entire resource group (all resources within)
az group delete --name myimpact-demo-rg --yes --no-wait

# Verify deletion (takes ~5-10 minutes)
az group exists --name myimpact-demo-rg
# Should return: false
```

---

## Next Steps

1. ✅ Complete Azure setup (Steps 1-7)
2. ✅ Configure GitHub Secrets
3. ✅ Push code to trigger deployment
4. ✅ Verify endpoints are working
5. ✅ Update frontend API endpoint
6. ✅ Test end-to-end
7. ✅ Share URL with others!

---

## References

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Static Web Apps Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
