<!-- filepath: z:\Shared\Code\my_impact\infra\CI_CD_DEPLOYMENT_GUIDE.md -->
# Complete CI/CD Deployment Guide for MyImpact

This guide provides step-by-step instructions to deploy MyImpact to Azure with automated CI/CD pipelines using GitHub Actions.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Azure Setup](#initial-azure-setup)
3. [GitHub Secrets Configuration](#github-secrets-configuration)
4. [Deployment](#deployment)
5. [Troubleshooting](#troubleshooting)
6. [Post-Deployment Verification](#post-deployment-verification)

---

## Prerequisites

Before starting, ensure you have:

- **Azure Subscription** with appropriate permissions (Owner or Contributor)
- **GitHub Repository** (your forked/cloned copy of my_impact)
- **Azure CLI** installed locally ([download](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **GitHub Account** with ability to configure repository settings
- **Docker** installed (for local testing)

### Verify Tools

```bash
az --version
gh --version
docker --version
git --version
```

---

## Initial Azure Setup

### Step 1: Create Resource Group First

```bash
# Set variables
SUBSCRIPTION_ID="<your-azure-subscription-id>"
RESOURCE_GROUP_NAME="myimpact-demo-rg"
AZURE_REGION="eastus"

# Login to Azure
az login
az account set --subscription "$SUBSCRIPTION_ID"

# Create resource group
az group create \
  --name "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"
```

### Step 2: Create Service Principal with Least-Privilege Scope

**Security Best Practice**: Scope the service principal to **only the resource group**, not the entire subscription.

```bash
# Get resource group ID for scoping
RESOURCE_GROUP_ID=$(az group show \
  --name "$RESOURCE_GROUP_NAME" \
  --query id -o tsv)

# Create service principal scoped to resource group only
az ad sp create-for-rbac \
  --name "myimpact-ci-cd-demo" \
  --role "Contributor" \
  --scopes "$RESOURCE_GROUP_ID" \
  --json-auth > azure-credentials.json

echo "✅ Service principal created with resource group scope"
echo "📁 Credentials saved to: azure-credentials.json"
```

**🔒 Security Improvement**: If the `AZURE_CREDENTIALS` secret is compromised, the attacker can only affect resources in `myimpact-demo-rg`, not the entire subscription.

**⚠️ Important**: 
- Save the output from `azure-credentials.json` - you'll need it for GitHub Secrets
- **Delete this file after adding to GitHub Secrets**: `rm azure-credentials.json`
- The service principal uses a long-lived client secret; for production, use [Federated Credentials](#optional-use-federated-credentials-for-production) instead

### Step 3: Create Azure Container Registry

**Security Note**: Admin user is **disabled** by default (following managed identity best practices).

```bash
REGISTRY_NAME="myimpactdemo$(date +%s)"

# Create Container Registry (admin user disabled)
az acr create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$REGISTRY_NAME" \
  --sku Standard \
  --location "$AZURE_REGION" \
  --admin-enabled false

echo "✅ Container Registry created: $REGISTRY_NAME.azurecr.io"
```

**Note**: We use the service principal credentials for **CI/CD image push only**. The Container App uses **Managed Identity** to pull images (no admin credentials needed).

### Step 4: Grant Service Principal AcrPush Role

```bash
# Get ACR resource ID
ACR_ID=$(az acr show \
  --name "$REGISTRY_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query id -o tsv)

# Get service principal app ID
SP_APP_ID=$(cat azure-credentials.json | jq -r '.clientId')

# Grant AcrPush role for CI/CD (least privilege for pushing images)
az role assignment create \
  --assignee "$SP_APP_ID" \
  --role "AcrPush" \
  --scope "$ACR_ID"

echo "✅ Service principal granted AcrPush role (push images only)"
```

### Step 5: Create Container Apps Environment

```bash
ENV_NAME="myimpact-demo-env"

az containerapp env create \
  --name "$ENV_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"

echo "✅ Container Apps Environment created: $ENV_NAME"
```

### Step 6: Create Azure Static Web Apps Resource (Optional)

If you want automated Static Web Apps deployment:

```bash
STATIC_APP_NAME="myimpact-demo"

# Create the Static Web App resource
az staticwebapp create \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --location "$AZURE_REGION"

# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query 'properties.apiKey' -o tsv)

echo "✅ Static Web App created: $STATIC_APP_NAME"
echo "📝 Deployment token: $DEPLOYMENT_TOKEN"
```

Save the deployment token for GitHub Secrets.

---

## GitHub Secrets Configuration

GitHub Actions workflows use secrets to authenticate with Azure. Configure these in your GitHub repository:

### How to Add Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret below:

### Required Secrets for Backend (Container Apps)

| Secret Name | Value | Source |
|---|---|---|
| `AZURE_CREDENTIALS` | Full JSON output from `azure-credentials.json` | Step 2 above |
| `AZURE_RESOURCE_GROUP` | `myimpact-demo-rg` | Created in Step 1 |
| `AZURE_REGISTRY_LOGIN_SERVER` | e.g., `myimpactdemo12345.azurecr.io` | Step 3 output |
| `CONTAINER_APP_NAME` | `myimpact-demo-api` | Created by workflow |
| `CONTAINER_APPS_ENV` | `myimpact-demo-env` | Step 5 above |

**Security Note**: `AZURE_REGISTRY_USERNAME` and `AZURE_REGISTRY_PASSWORD` are **not needed** because:
- CI/CD uses service principal credentials from `AZURE_CREDENTIALS`
- Container App uses Managed Identity to pull images

### Required Secrets for Frontend (Static Web Apps)

| Secret Name | Value | Source |
|---|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token from Step 6 | Step 6 above |
| `AZURE_CREDENTIALS` | Full JSON output from `azure-credentials.json` | Step 2 above |
| `AZURE_RESOURCE_GROUP` | `myimpact-demo-rg` | Created in Step 1 |

### Example Azure Credentials Secret

Your `AZURE_CREDENTIALS` secret should look like:

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxx~xxx-xxx.xxx_xxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**🔒 Security Reminder**: After adding to GitHub Secrets, delete the local file:
```bash
rm azure-credentials.json
```

---

## Optional: Use Federated Credentials for Production

For **production environments**, use OpenID Connect (OIDC) federated credentials instead of long-lived client secrets:

```bash
# Create app registration (no secret)
APP_ID=$(az ad app create \
  --display-name "myimpact-prod-github-actions" \
  --query appId -o tsv)

# Create service principal
SP_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)

# Create federated credential for GitHub Actions
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-federated",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_GITHUB_ORG/my_impact:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Grant contributor role to resource group
az role assignment create \
  --assignee "$SP_ID" \
  --role Contributor \
  --scope "$RESOURCE_GROUP_ID"

echo "✅ Federated credentials setup complete"
```

---

## Deployment

### Method 1: Automatic Deployment (Recommended)

Once secrets are configured, deployments happen automatically:

1. **Backend deploys** when you push changes to:
   - `api/**`
   - `myimpact/**`
   - `Dockerfile`
   - `pyproject.toml`

2. **Frontend deploys** when you push changes to:
   - `webapp/**`

Just push to `main` branch:

```bash
git add .
git commit -m "Deploy: Add rate limiting and CI/CD"
git push origin main
```

Monitor deployment progress in: **Actions** tab on GitHub

### Method 2: Manual Infrastructure Setup (Using Bicep)

If you prefer to deploy infrastructure first:

```bash
# Deploy using Bicep template
az deployment group create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --template-file infra/bicep/main.bicep \
  --parameters \
    projectName=myimpact \
    environment=demo \
    location="$AZURE_REGION"
```

---

## Post-Deployment Verification

### Check Backend Deployment

```bash
# Get Container App URL
CONTAINER_APP_URL=$(az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.configuration.ingress.fqdn' \
  -o tsv)

echo "Container App URL: https://$CONTAINER_APP_URL"

# Test health endpoint
curl "https://$CONTAINER_APP_URL/api/health"

# Expected response:
# {"status":"healthy","version":"0.1.0"}

# Test metadata endpoint
curl "https://$CONTAINER_APP_URL/api/metadata" | jq .

# Test rate limiting (run multiple times rapidly)
for i in {1..15}; do
  curl -X POST "https://$CONTAINER_APP_URL/api/goals/generate" \
    -H "Content-Type: application/json" \
    -d '{"scale":"technical","level":"L30–35 (Career)","growth_intensity":"moderate","org":"demo"}'
done
# After 10 requests, you should get 429 (Too Many Requests)
```

### Check Frontend Deployment

```bash
# Get Static Web App URL
STATIC_APP_URL=$(az staticwebapp show \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'defaultHostname' \
  -o tsv)

echo "Static Web App URL: https://$STATIC_APP_URL"

# Visit in browser: https://$STATIC_APP_URL
```

### Update Frontend API Endpoint

Once backend is deployed, update the frontend to use the production API:

**File: `webapp/js/api.js`**

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://<YOUR-CONTAINER-APP-URL>'; // Replace with actual Container App FQDN
```

---

## Troubleshooting

### Workflow Fails with Authentication Error

**Problem**: `ERROR: Unable to authenticate to Azure`

**Solution**:
1. Verify `AZURE_CREDENTIALS` secret is valid JSON (no extra spaces)
2. Ensure service principal still exists: `az ad sp show --id <client-id>`
3. Re-create credentials if needed: `az ad sp create-for-rbac --name myimpact-ci-cd --role Contributor`

### Container App Won't Start

**Problem**: Container crashes or won't become healthy

**Solution**:
```bash
# View container logs
az containerapp logs show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --container myimpact-api \
  --follow

# Check container app status
az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.provisioningState'
```

### Static Web App Won't Deploy

**Problem**: Frontend deployment fails

**Solution**:
1. Check GitHub Actions logs in the repo
2. Verify Static Web App resource exists
3. Ensure deployment token is correct and not expired
4. Check that `webapp/` directory contains `index.html`

### CORS Errors in Browser

**Problem**: Frontend can't reach backend API

**Solution**: Update `api/main.py` with correct Static Web Apps URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myimpact-demo.azurestaticapps.net",  # Update this
        "https://*.azurestaticapps.net",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    ...
)
```

Then commit and push to trigger backend redeploy.

---

## Cost Estimation

For a demo environment:

- **Azure Container Registry**: ~$5/month
- **Container Apps (0.5 CPU, 1GB RAM)**: ~$10-15/month (billed per second only when running)
- **Azure Static Web Apps**: FREE (up to 100 GB bandwidth)
- **Total Monthly Cost**: ~$15-20

**Demo Usage**: Cost will be minimal (~$0.10-0.50) if only running during the openspace session.

---

## Useful Commands Reference

```bash
# View deployment logs
az containerapp logs show --name myimpact-demo-api --resource-group myimpact-demo-rg --follow

# Update container image
az containerapp update --name myimpact-demo-api --resource-group myimpact-demo-rg \
  --image myimpactdemo12345.azurecr.io/myimpact-api:latest

# Scale replicas
az containerapp update --name myimpact-demo-api --resource-group myimpact-demo-rg \
  --min-replicas 1 --max-replicas 5

# Delete all resources
az group delete --name myimpact-demo-rg --yes --no-wait
```

---

## Next Steps

1. ✅ Configure GitHub Secrets
2. ✅ Push code to trigger automatic deployment
3. ✅ Monitor GitHub Actions → Actions tab
4. ✅ Verify endpoints are working
5. ✅ Update frontend API endpoint
6. ✅ Test end-to-end in browser
7. ✅ Share URL at openspace session!

---

For questions or issues, check:
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
