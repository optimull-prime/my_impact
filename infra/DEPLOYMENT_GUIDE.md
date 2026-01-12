# MyImpact Deployment Guide




## Quick Start (20 min)

**Prerequisites:**
- Azure subscription (Owner/Contributor access)
- Azure CLI installed: `az --version`
- PowerShell 7.0+ installed
- GitHub repo access

**Run the deployment script:**
This script bootstraps enough infrastructure to enable CI/CD.  After infrastructure is set up, subsequent deployments are automatic on `git push main`

```powershell
# 1. Navigate to the infra directory
cd infra

# 2. Run the idempotent deployment script
.\Deploy-Azure.ps1 -SubscriptionId "<your-subscription-id>"

# Or with custom parameters:
.\Deploy-Azure.ps1 `
  -SubscriptionId "<your-subscription-id>" `
  -ResourceGroupName "myimpact-prod-rg" `
  -AzureRegion "westus"
```

**Safe to run multiple times** — existing resources are preserved.

**Next: Configure GitHub Secrets (5 min)**

The script outputs a `github-secrets.json` file with all values. Go to:
1. GitHub Repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** (not environment-specific)
3. Add the 5 secrets from the script output:
   - `AZURE_CREDENTIALS`
   - `AZURE_RESOURCE_GROUP`
   - `AZURE_REGISTRY_LOGIN_SERVER`
   - `CONTAINER_APP_NAME`
   - `CONTAINER_APPS_ENV`

> **Note:** For demo/dev, use **repository secrets** (no environment required). For production with approval gates, see [Using GitHub Environments](#using-github-environments-optional) below.

**Then: Deploy application (first time: manual, 5 min)**

**Manual deployment (recommended for first deploy)**

Verify your setup works before enabling automatic deployments:

1. Go to GitHub → **Actions** tab
2. Click **Deploy Backend to Azure Container Apps** (left sidebar)
3. Click **Run workflow** dropdown → **Run workflow** (green button)
4. Monitor the deployment progress (~5-10 minutes)

**Finally: Verify deployment**

```powershell
# Get your API URL
$container_app_url = az containerapp show `
  --name myimpact-demo-api `
  --resource-group myimpact-demo-rg `
  --query 'properties.configuration.ingress.fqdn' -o tsv

echo "Your API: https://$container_app_url"

# Test health endpoint
curl "https://$container_app_url/api/health"
# Expected: {"status":"healthy","version":"0.1.0"}
```

**Done!** Your app is live at `https://<container-app-url>`

---

## CI/CD Pipeline Overview

When you push to `main`, GitHub Actions automatically:

1. **Tests & Security Scan**
2. **Build Docker Image**
3. **Push to Azure Container Registry**
4. **Deploy to Container Apps**
5. **Health Check**

**Total time:** ~5-10 minutes from `git push` to live

### Available Workflows

See [`.github/workflows/`](../../.github/workflows/) for complete workflow definitions.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-backend.yml` | Push to `main` (changes in `api/`, `myimpact/`, `Dockerfile`, `pyproject.toml`) OR manual trigger | Build Docker image, push to ACR, deploy to Container Apps |
| `deploy-frontend.yml` | Push to `main` (changes in `webapp/`) OR manual trigger | Build Vue.js app, deploy to Azure Static Web Apps |
| `test-backend.yml` | Push to any branch, PRs | Run Python unit tests with pytest |

**Security scanning options:**

- **GitHub CodeQL** (recommended, free): Analyzes code for vulnerabilities at commit time
- **Dependabot** (built-in): Auto-updates dependencies with security patches

**Manual trigger:** Run workflows manually from GitHub → **Actions** tab → Select workflow → **Run workflow**

**Why start with manual deployment?**
- Validates GitHub Secrets are correct
- Tests deployment process without code changes
- Easier to troubleshoot (no git history confusion)
- You control when first deploy happens

**After first successful manual deploy:** Future commits to `main` automatically deploy (CI/CD enabled). To deploy changes:

```bash
git add .
git commit -m "Update API endpoint"
git push origin main
```

The workflows automatically trigger on changes to their respective paths.

### Monitoring Deployment

**View workflow logs:**
1. Go to GitHub repo → **Actions** tab
2. Click the workflow run
3. Expand each job to see detailed logs

**Check deployment status:**
- **GitHub Actions:** Click workflow run → **Deploy job** → See step-by-step progress
- **Azure Portal:** Container Apps → myimpact-demo-api → **Revisions** tab → See active revision
- **CLI:** `az containerapp show --name myimpact-demo-api --resource-group myimpact-demo-rg --query 'properties.runningStatus'`

---

## Security & Best Practices

**Security Architecture:** See [Security Design Documentation](../docs/architecture/security-design.md) for comprehensive security details aligned with Azure Well-Architected Framework.

**Key Security Controls:**
- Managed Identity for Container App to ACR (no credentials stored)
- Service Principal scoped to resource group only (least privilege)
- ACR admin user disabled (RBAC-based access only)
- HTTPS enforced on all endpoints (TLS 1.2+)
- CORS headers restrict allowed origins
- GitHub Secrets encrypted at rest
- Snyk and CodeQL security scanning on all code changes

**Production Hardening:** For production deployments, implement:
- Federated credentials (OIDC) instead of service principal secrets
- Private endpoints for ACR and Container Apps
- Web Application Firewall (WAF)
- Azure Key Vault for secrets management
- Application Insights for monitoring and alerting

See [Security Design Documentation](../docs/architecture/security-design.md) for production security roadmap.

---

## Using GitHub Environments (Optional)

For **production deployments**, use GitHub Environments to add:
- **Approval gates** (manual approval before deploy)
- **Environment-specific secrets** (prod vs. staging)
- **Deployment protection rules**

**Setup (5 min):**

1. Go to **Settings** → **Environments** → **New environment**
2. Create environment named `production`
3. Add **Required reviewers** (1-6 people who must approve)
4. Add **Wait timer** (e.g., 5 min delay before deploy)
5. Move secrets from repository level to `production` environment

**Update workflow to use environment:**

```yaml
# .github/workflows/deploy-backend.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Add this line
    steps:
      # ...existing steps...
```

**Why this matters for production:**
- Prevents accidental deploys (`main` push requires approval)
- Separates dev/staging/prod credentials
- Creates audit trail of who approved what

**For demo/dev:** Skip this—direct repository secrets are faster and simpler.

---

## Troubleshooting

### Script execution fails with "Azure CLI not found"

**Cause:** Azure CLI not installed or not in PATH

**Fix:**
```powershell
# Verify Azure CLI is installed
az --version

# If not installed, download from:
# https://docs.microsoft.com/cli/azure/install-azure-cli
```

### Script fails at "Authenticating with Azure"

**Cause:** Not logged into Azure, or login times out

**Fix:**
```powershell
# Manual login
az login

# Then run the deployment script again
.\Deploy-Azure.ps1 -SubscriptionId "your-subscription-id"
```

### GitHub Actions workflow fails with "Authentication failed"

**Cause:** Invalid or missing GitHub Secrets

**Fix:**
1. Verify all 5 secrets are added to GitHub:
   - **Settings** → **Secrets and variables** → **Actions**
   - Confirm: `AZURE_CREDENTIALS`, `AZURE_RESOURCE_GROUP`, `AZURE_REGISTRY_LOGIN_SERVER`, `CONTAINER_APP_NAME`, `CONTAINER_APPS_ENV`
2. If credentials expired:
   ```powershell
   # Regenerate service principal credentials
   $resourceGroupId = az group show --name myimpact-demo-rg --query id -o tsv
   az ad sp create-for-rbac --name myimpact-ci-cd-demo `
     --role Contributor --scopes $resourceGroupId --json-auth
   ```
   Copy the new JSON to GitHub `AZURE_CREDENTIALS` secret

### Container App won't start or health check fails

**Cause:** Image build failed, dependency issue, or runtime error

**Fix:**
```powershell
# Check container logs
az containerapp logs show `
  --name myimpact-demo-api `
  --resource-group myimpact-demo-rg `
  --follow

# Check app status
az containerapp show `
  --name myimpact-demo-api `
  --resource-group myimpact-demo-rg `
  --query 'properties.provisioningState'

# Check if local build works
docker build -t myimpact:local .
docker run -p 8000:8000 myimpact:local
curl http://localhost:8000/api/health
```

### CORS errors in browser

**Cause:** Frontend URL not in backend CORS allow list

**Fix:** Update [api/main.py](api/main.py):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-static-app.azurestaticapps.net",  # Add your URL
        "https://*.azurestaticapps.net",
        "http://localhost:8000",
    ],
)
```

Commit and push to trigger redeployment.

### Rate limiting appears to not be working

**Cause:** slowapi middleware not installed or not initialized

**Fix:** Verify in [api/main.py](api/main.py):
```python
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.add_middleware(SlowAPIMiddleware)
```

---

## Cost Estimation

| Component | Monthly | Demo Usage |
|-----------|---------|-----------|
| Container Registry (Standard) | $5 | N/A |
| Container Apps (0.5 CPU, 1GB) | $10-15 | <$0.50 |
| Static Web Apps (Free tier) | FREE | FREE |
| **Total** | **$15-20** | **<$0.50** |

**Demo tip:** Scale to 0 replicas when not in use to save costs:
```bash
az containerapp update --name myimpact-demo-api \
  --resource-group myimpact-demo-rg --min-replicas 0
```

**Cleanup after demo:**
```bash
az group delete --name myimpact-demo-rg --yes --no-wait
```
