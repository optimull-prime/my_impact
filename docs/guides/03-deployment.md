# 🚀 Deployment Guide

Complete guide for deploying MyImpact to Azure.

## Overview

MyImpact deploys to two Azure services:

- **Frontend**: Azure Static Web Apps (free tier: 100 GB bandwidth)
- **Backend API**: Azure Container Apps (~$15/month)

**Total Cost**: ~$15/month

---

## Prerequisites

- Azure subscription
- Azure CLI (`az` command) installed
- Docker installed (for building container images)
- GitHub account (with your MyImpact repository)

## Environment Setup

```bash
# Set your Azure variables
export AZURE_SUBSCRIPTION_ID="<your-subscription-id>"
export AZURE_RESOURCE_GROUP="myimpact-demo"
export AZURE_REGION="eastus"
export GITHUB_OWNER="<your-github-username>"
export GITHUB_REPO="my_impact"

# Login to Azure
az login
az account set --subscription $AZURE_SUBSCRIPTION_ID

# Create resource group
az group create \
  --name $AZURE_RESOURCE_GROUP \
  --location $AZURE_REGION
```

---

## Part 1: Deploy Backend API (Container Apps)

### Step 1: Create Container Registry

```bash
export ACR_NAME="myimpactacr"

az acr create \
  --resource-group $AZURE_RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard
```

### Step 2: Build and Push Docker Image

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

### Step 3: Create Container Apps Environment

```bash
export CONTAINER_ENV="myimpact-env"

az containerapp env create \
  --name $CONTAINER_ENV \
  --resource-group $AZURE_RESOURCE_GROUP \
  --location $AZURE_REGION
```

### Step 4: Create Container App

```bash
export CONTAINER_APP="myimpact-api"

az containerapp create \
  --name $CONTAINER_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image $ACR_NAME.azurecr.io/myimpact-api:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv) \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 3
```

### Step 5: Get API Endpoint

```bash
# Get the fully qualified domain name
API_FQDN=$(az containerapp show \
  --name $CONTAINER_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo "API URL: https://$API_FQDN"

# Test it
curl https://$API_FQDN/api/health
```

Expected response:
```json
{"status":"healthy","version":"0.1.0"}
```

**Save this URL** – you'll need it for the frontend.

---

## Part 2: Deploy Frontend (Static Web Apps)

### Step 1: Create Static Web App

```bash
export STATIC_APP="myimpact-demo"

az staticwebapp create \
  --name $STATIC_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --source "https://github.com/$GITHUB_OWNER/$GITHUB_REPO" \
  --branch main \
  --location $AZURE_REGION \
  --login-with-github
```

This will:
1. Prompt you to authenticate with GitHub
2. Create a GitHub Actions workflow in your repo
3. Auto-deploy on every push to `main`

### Step 2: Get Frontend URL

```bash
# Get the default hostname
FRONTEND_URL=$(az staticwebapp show \
  --name $STATIC_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query defaultHostname \
  -o tsv)

echo "Frontend URL: https://$FRONTEND_URL"
```

### Step 3: Update Frontend API Endpoint

Edit `webapp/js/api.js` and update the API URL:

**File**: `webapp/js/api.js`

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://<your-container-app-fqdn>';  // ← Update with your API URL
```

Replace `<your-container-app-fqdn>` with the API FQDN from Step 5 above (e.g., `myimpact-api.gentleriver-xyz.eastus.azurecontainerapps.io`)

### Step 4: Commit and Push

```bash
git add webapp/js/api.js
git commit -m "Update API endpoint to production Container Apps"
git push origin main
```

The frontend will automatically redeploy via GitHub Actions. Check GitHub Actions to see the build progress.

---

## Part 3: Verify Everything Works

### Test the Backend

```bash
curl https://$API_FQDN/api/health
curl https://$API_FQDN/api/metadata | python -m json.tool
```

### Test the Frontend

1. Visit: `https://$FRONTEND_URL`
2. Fill out the form
3. Click "Generate Prompt"
4. Verify results appear and copy buttons work

---

## Optional: Add Custom Domain

### For Static Web App (Frontend)

```bash
az staticwebapp custom-domain add \
  --name $STATIC_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --domain-name "myimpact.example.com"
```

Then update your DNS provider with the validation record Azure provides.

### For Container App (Backend)

Container Apps FQDN is already public. Consider using API Management for custom domains (advanced).

---

## Monitoring & Troubleshooting

### View Logs

**Backend logs**:
```bash
az containerapp logs show \
  --name $CONTAINER_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --follow
```

**Frontend build logs**:
Go to: `https://github.com/$GITHUB_OWNER/$GITHUB_REPO/actions`

### Common Issues

**Frontend can't reach backend API**:
- Check that API endpoint in `webapp/js/api.js` is correct
- Check that Container App is running: `az containerapp show --name $CONTAINER_APP ...`
- Test API directly: `curl https://$API_FQDN/api/health`

**Frontend builds fail**:
- Check GitHub Actions logs
- Ensure `webapp/` directory exists and has `index.html`

**API returns 502 Bad Gateway**:
- Check logs: `az containerapp logs show ...`
- Ensure Docker image builds: `docker build -t test . && docker run -it test`

---

## Scaling & Cost Optimization

### Increase Replicas (for higher traffic)

```bash
az containerapp update \
  --name $CONTAINER_APP \
  --resource-group $AZURE_RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 5
```

### Cost Estimates

| Service | Free Tier | Estimated Cost |
|---------|-----------|-----------------|
| Static Web Apps | ✅ 100 GB bandwidth | $0/month |
| Container Apps | 0.5 CPU, 1 GB RAM, 1-3 replicas | ~$15/month |
| Container Registry | | ~$5/month |
| **Total** | | ~**$20/month** |

To reduce costs:
- Set `--min-replicas 0` for auto-scale to zero (cold-starts ~5 seconds)
- Use Standard tier ACR instead of Premium

---

## CI/CD Pipeline (Automatic Deployments)

### Frontend (GitHub Actions)

Static Web Apps automatically creates a GitHub Actions workflow. Every push to `main`:
1. Builds and deploys the `webapp/` directory
2. Deploys to `https://$FRONTEND_URL`

### Backend (Manual)

To automate backend deployments, set up a GitHub Actions workflow:

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Container Apps

on:
  push:
    branches:
      - main
    paths:
      - 'api/**'
      - 'myimpact/**'
      - 'Dockerfile'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker image
        run: |
          docker build -t ${{ secrets.ACR_NAME }}.azurecr.io/myimpact-api:latest .
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/myimpact-api:latest
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name myimpact-api \
            --resource-group myimpact-demo \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/myimpact-api:latest
```

---

## Cleanup (Delete Everything)

```bash
# Delete the entire resource group and all resources
az group delete --name $AZURE_RESOURCE_GROUP --yes
```

---

## Troubleshooting Checklist

- [ ] Resource group created in correct region
- [ ] Container image builds successfully locally
- [ ] Container image pushed to Azure Container Registry
- [ ] Container App is running (check status in Portal)
- [ ] API endpoint responds to health check
- [ ] Frontend API URL in `webapp/js/api.js` is correct
- [ ] Frontend deployed and accessible
- [ ] Frontend can reach backend (check browser console)
- [ ] Copy-to-clipboard buttons work

---

## Next Steps

→ Everything deployed? Go show people! 🚀

→ Want to set up CI/CD? Create `.github/workflows/deploy-backend.yml` (see CI/CD section above)

→ Want to add monitoring? See Azure Application Insights docs
