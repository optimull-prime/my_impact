# Azure Container Apps Deployment Configuration for MyImpact Backend

This guide covers deploying the MyImpact FastAPI backend to Azure Container Apps.

## Prerequisites

- Azure CLI (`az` command)
- Docker installed locally (for building/testing images)
- An Azure subscription
- A resource group created in Azure

## Environment Setup

```bash
# Set variables
export AZURE_SUBSCRIPTION_ID="<your-subscription-id>"
export AZURE_RESOURCE_GROUP="myimpact-demo"
export AZURE_REGION="eastus"
export CONTAINER_REGISTRY_NAME="myimpactacr"
export CONTAINER_APPS_ENV="myimpact-env"
export CONTAINER_APP_NAME="myimpact-api"
export IMAGE_NAME="myimpact-api:latest"

# Login to Azure
az login
az account set --subscription $AZURE_SUBSCRIPTION_ID
```

## Step 1: Create Resource Group

```bash
az group create \
  --name $AZURE_RESOURCE_GROUP \
  --location $AZURE_REGION
```

## Step 2: Create Container Registry

```bash
az acr create \
  --resource-group $AZURE_RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY_NAME \
  --sku Standard
```

## Step 3: Build and Push Docker Image

```bash
# Build the Docker image
docker build -t $CONTAINER_REGISTRY_NAME.azurecr.io/$IMAGE_NAME .

# Login to Azure Container Registry
az acr login --name $CONTAINER_REGISTRY_NAME

# Push image to registry
docker push $CONTAINER_REGISTRY_NAME.azurecr.io/$IMAGE_NAME
```

## Step 4: Create Container Apps Environment

```bash
az containerapp env create \
  --name $CONTAINER_APPS_ENV \
  --resource-group $AZURE_RESOURCE_GROUP \
  --location $AZURE_REGION
```

## Step 5: Create Container App

```bash
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --environment $CONTAINER_APPS_ENV \
  --image $CONTAINER_REGISTRY_NAME.azurecr.io/$IMAGE_NAME \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server $CONTAINER_REGISTRY_NAME.azurecr.io \
  --registry-username $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query "username" -o tsv) \
  --registry-password $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query "passwords[0].value" -o tsv) \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --query properties.configuration.ingress.fqdn
```

## Step 6: Get API Endpoint

```bash
# Get the fully qualified domain name
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

The API will be available at: `https://<app-fqdn>/api/`

## Step 7: Update Static Web App CORS

In the frontend JavaScript (`webapp/js/api.js`), update the `API_BASE_URL` to point to your Container Apps endpoint:

```javascript
const API_BASE_URL = 'https://<your-container-app-fqdn>';
```

## Environment Variables

If you want to enable Azure OpenAI integration, set these environment variables:

```bash
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    AZURE_OPENAI_DEPLOYMENT=$AZURE_OPENAI_DEPLOYMENT \
    GEN_TEMPERATURE="0.9"
```

## Monitoring and Logs

```bash
# View logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --follow

# Check health
curl https://<your-container-app-fqdn>/api/health
```

## Scaling

```bash
# Update minimum and maximum replicas
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 5
```

## Cost Optimization

- **Min replicas 1, Max replicas 3**: Good for demo/low-traffic scenarios (~$10-15/month)
- **CPU 0.5, Memory 1.0Gi**: Minimum for FastAPI app
- Monitor Container Apps pricing: https://azure.microsoft.com/en-us/pricing/details/container-apps/

## Troubleshooting

### Health check failing
```bash
# Verify the app is running
az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $AZURE_RESOURCE_GROUP
```

### CORS issues
- Verify `staticwebapp.config.json` allows backend origin
- Check that frontend is calling the correct API endpoint

### Image pull errors
- Verify container registry has the image: `az acr repository list --name $CONTAINER_REGISTRY_NAME`
- Check registry credentials

## Cleanup

```bash
# Delete container app
az containerapp delete \
  --name $CONTAINER_APP_NAME \
  --resource-group $AZURE_RESOURCE_GROUP

# Delete container environment
az containerapp env delete \
  --name $CONTAINER_APPS_ENV \
  --resource-group $AZURE_RESOURCE_GROUP

# Delete container registry
az acr delete \
  --name $CONTAINER_REGISTRY_NAME \
  --resource-group $AZURE_RESOURCE_GROUP

# Delete resource group
az group delete --name $AZURE_RESOURCE_GROUP
```
