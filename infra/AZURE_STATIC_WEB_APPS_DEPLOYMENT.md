# Azure Static Web Apps Deployment Configuration for MyImpact Frontend

This guide covers deploying the MyImpact frontend to Azure Static Web Apps.

## Overview

Azure Static Web Apps is ideal for the MyImpact frontend because:
- Free tier: 100 GB bandwidth/month, automatic HTTPS, custom domains
- Built-in CI/CD from GitHub (automatic deployments on push)
- No build step needed (vanilla HTML/CSS/JS)
- Staging environments for branch previews
- Easy integration with backend API

## Prerequisites

- GitHub account with the MyImpact repository
- Azure subscription
- Azure CLI (`az` command) installed
- A resource group in Azure

## Environment Setup

```bash
# Set variables
export AZURE_SUBSCRIPTION_ID="<your-subscription-id>"
export AZURE_RESOURCE_GROUP="myimpact-demo"
export AZURE_REGION="westus2"
export STATIC_WEB_APP_NAME="myimpact-demo"
export GITHUB_OWNER="<your-github-username>"
export GITHUB_REPO="my_impact"
export GITHUB_BRANCH="main"

# Login to Azure
az login
az account set --subscription $AZURE_SUBSCRIPTION_ID
```

## Option 1: Deploy via Azure CLI

### Step 1: Create Resource Group

```bash
az group create \
  --name $AZURE_RESOURCE_GROUP \
  --location $AZURE_REGION
```

### Step 2: Create Static Web App

```bash
az staticwebapp create \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --source "https://github.com/$GITHUB_OWNER/$GITHUB_REPO" \
  --branch $GITHUB_BRANCH \
  --location $AZURE_REGION \
  --login-with-github
```

This will:
1. Prompt you to authenticate with GitHub
2. Create a GitHub Actions workflow in your repo
3. Automatically deploy on every push to `main` branch

### Step 3: Get the Default URL

```bash
az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query "defaultHostname" -o tsv
```

Your app is now live at: `https://<default-hostname>`

## Option 2: Manual Deployment (Without GitHub CI/CD)

If you prefer to deploy manually without GitHub integration:

```bash
# Install Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Login to Azure
swa login --subscription-id $AZURE_SUBSCRIPTION_ID

# Deploy
swa deploy ./webapp --deployment-token <token>
```

## Step 4: Update Backend API Endpoint

Once your backend (Container Apps) is deployed, update the frontend to point to it:

**File: `webapp/js/api.js`**

Replace:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}`;
```

With:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://<your-container-app-fqdn>';  // Update this
```

Then push the change:
```bash
git add webapp/js/api.js
git commit -m "Update API endpoint to production Container Apps"
git push
```

The frontend will automatically redeploy.

## Step 5: Configure Custom Domain (Optional)

```bash
# Get static web app ID
STATIC_WEB_APP_ID=$(az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query "id" -o tsv)

# Add custom domain
az staticwebapp custom-domain add \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --domain-name "myimpact.example.com"

# Follow the DNS validation steps provided by Azure
```

## Monitoring and Logs

```bash
# View build history
az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP

# Check GitHub Actions workflow
# Go to: https://github.com/$GITHUB_OWNER/$GITHUB_REPO/actions
```

## Environment-Specific Configuration

Create `webapp/staticwebapp.config.json` to handle:
- CORS for backend API
- Routing rules
- Response overrides for 404 handling
- Custom headers

Example is provided in the repo.

## Deployment Strategy

### Development/Staging
1. Create a feature branch: `git checkout -b feature/my-feature`
2. GitHub Actions automatically creates a staging environment
3. Access preview at: `https://<random-id>.azurestaticapps.net`
4. Test, then merge to `main` for production

### Production
1. Merge to `main` branch
2. GitHub Actions automatically deploys to production
3. Live at: `https://myimpact-demo.azurestaticapps.net`

## GitHub Actions Workflow

Azure Static Web Apps creates a GitHub Actions workflow automatically. It's located in:
```
.github/workflows/azure-static-web-apps-<random-id>.yml
```

Key steps:
1. Checkout code
2. Build (skipped for vanilla HTML/CSS/JS)
3. Deploy to Static Web Apps

## Cost

**Azure Static Web Apps - Free Tier**:
- 100 GB bandwidth/month
- 1 staging environment per custom domain
- Automatic HTTPS and custom domains
- Cost: **$0**

**Paid Tier** (if you exceed free limits):
- $0.20 per GB additional bandwidth

## Troubleshooting

### Build failed in GitHub Actions
- Check the workflow run in GitHub Actions tab
- Look for build errors (usually related to node_modules or missing dependencies)
- Since we're using vanilla JS + CDN, build failures are rare

### Frontend can't reach backend API
- Verify backend Container Apps is running: `curl https://<api-fqdn>/api/health`
- Check `API_BASE_URL` in `webapp/js/api.js` is correct
- Verify CORS is enabled on the backend
- Check browser console for CORS errors

### Custom domain not working
- Ensure DNS records are configured correctly
- Wait up to 15 minutes for DNS propagation
- Verify domain ownership in Azure portal

## Cleanup

```bash
# Delete Static Web App
az staticwebapp delete \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP
```

## Next Steps

1. Deploy the backend to Azure Container Apps (see `AZURE_CONTAINER_APPS_DEPLOYMENT.md`)
2. Update `API_BASE_URL` in `webapp/js/api.js`
3. Push changes to trigger frontend redeploy
4. Test end-to-end flow

## Resources

- Azure Static Web Apps: https://docs.microsoft.com/azure/static-web-apps/
- Pricing: https://azure.microsoft.com/pricing/details/app-service/static/
- GitHub Actions: https://docs.github.com/actions
