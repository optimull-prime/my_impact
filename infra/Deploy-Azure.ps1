#Requires -Version 7.0
<#
.SYNOPSIS
    Idempotent Azure deployment for MyImpact demo environment.
    
.DESCRIPTION
    Sets up all required Azure resources (Resource Group, ACR, Container Apps Environment, Service Principal)
    and outputs values needed for GitHub Secrets configuration.
    
    Safe to run multiple times - existing resources are preserved and skipped.

.PARAMETER SubscriptionId
    Azure subscription ID.

.PARAMETER ResourceGroupName
    Name for the resource group (default: myimpact-demo-rg).

.PARAMETER AzureRegion
    Azure region for resources (default: eastus).

.PARAMETER OutputSecrets
    Path to output file for GitHub Secrets (default: ./github-secrets.json).

.EXAMPLE
    .\Deploy-Azure.ps1 -SubscriptionId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    
.EXAMPLE
    .\Deploy-Azure.ps1 -SubscriptionId "..." -ResourceGroupName "myimpact-prod-rg" -AzureRegion "westus"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroupName = "myimpact-demo-rg",
    
    [Parameter(Mandatory = $false)]
    [string]$AzureRegion = "eastus",
    
    [Parameter(Mandatory = $false)]
    [string]$OutputSecrets = "./github-secrets.json"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Section {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

function Test-AzureLogin {
    try {
        $account = az account show --query id -o tsv 2>$null
        return $null -ne $account
    }
    catch {
        return $false
    }
}

function Get-RandomSuffix {
    return Get-Date -UFormat "%s"
}

function Test-AzureCliVersion {
    param(
        [string]$MinimumVersion = "2.40.0"
    )
    
    try {
        $versionOutput = (az version --output json | ConvertFrom-Json)."azure-cli"
        $installedVersion = [version]$versionOutput
        $requiredVersion = [version]$MinimumVersion
        
        if ($installedVersion -lt $requiredVersion) {
            Write-Host "Error: Azure CLI version $MinimumVersion or later required." -ForegroundColor Red
            Write-Host "  Installed: $versionOutput"
            Write-Host "  Required:  $MinimumVersion"
            Write-Host "  Update from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
            exit 1
        }
        
        return $true
    }
    catch {
        Write-Host "Error: Could not determine Azure CLI version. Install from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# ENTRY POINT
# ============================================================================

Write-Section "MyImpact Azure Deployment"
Write-Host "Subscription: $SubscriptionId"
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Region: $AzureRegion`n"

# Verify Azure CLI is installed and meets minimum version requirement
Write-Host "Verifying Azure CLI..."
try {
    $versionOutput = (az version --output json | ConvertFrom-Json)."azure-cli"
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI not found or not in PATH"
    }
    Write-Success "Azure CLI found: $versionOutput"
}
catch {
    Write-Host "Error: Azure CLI not found or not accessible." -ForegroundColor Red
    Write-Host "Install from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check minimum version requirement
Test-AzureCliVersion -MinimumVersion "2.40.0"
Write-Success "Azure CLI version requirement met: $versionOutput"

# Login if needed
if (-not (Test-AzureLogin)) {
    Write-Section "Authenticating with Azure"
    az login | Out-Null
}

Write-Section "Setting subscription context"
az account set --subscription $SubscriptionId | Out-Null
Write-Success "Subscription set"

# ============================================================================
# RESOURCE GROUP (idempotent: create only if missing)
# ============================================================================

Write-Section "Resource Group"
$rgExists = az group exists --name $ResourceGroupName | ConvertFrom-Json
if ($rgExists) {
    Write-Success "Resource group already exists: $ResourceGroupName"
}
else {
    Write-Host "Creating resource group: $ResourceGroupName"
    az group create --name $ResourceGroupName --location $AzureRegion | Out-Null
    Write-Success "Resource group created"
}

$resourceGroupId = az group show --name $ResourceGroupName --query id -o tsv

# ============================================================================
# SERVICE PRINCIPAL (idempotent: check if exists, create if missing)
# ============================================================================
# Scoped to resource group only for security: if GitHub secret is compromised,
# attacker can only affect this resource group, not entire subscription.

Write-Section "Service Principal (CI/CD)"
$spName = "myimpact-ci-cd-demo"
$existingSp = az ad sp list --filter "displayName eq '$spName'" --query "[0].id" -o tsv 2>$null

if ($existingSp) {
    Write-Success "Service principal already exists: $spName"
    $spAppId = az ad sp show --id $existingSp --query appId -o tsv
}
else {
    Write-Host "Creating service principal: $spName"
    $spOutput = az ad sp create-for-rbac `
        --name $spName `
        --role "Contributor" `
        --scopes $resourceGroupId `
        --query '{clientId:clientId, clientSecret:clientSecret, tenantId:tenantId, subscriptionId:subscriptionId}' `
        --json-auth -o json | ConvertFrom-Json
    $spAppId = $spOutput.clientId
    Write-Success "Service principal created"
}

# Store SP details for later use
$spDetails = @{
    appId = $spAppId
}

# ============================================================================
# AZURE CONTAINER REGISTRY (idempotent: check if exists, create if missing)
# Disabled admin user per security best practices: CI/CD uses service principal
# (temporary credentials), Container App uses Managed Identity (no credentials).
# ============================================================================

Write-Section "Azure Container Registry"
$registryName = "myimpactdemo" + (Get-RandomSuffix)
$existingRegistry = az acr list --resource-group $ResourceGroupName --query "[0].name" -o tsv 2>$null

if ($existingRegistry) {
    Write-Success "Registry already exists: $existingRegistry"
    $registryName = $existingRegistry
}
else {
    Write-Host "Creating registry: $registryName"
    az acr create `
        --resource-group $ResourceGroupName `
        --name $registryName `
        --sku Standard `
        --admin-enabled false `
        --location $AzureRegion | Out-Null
    Write-Success "Registry created (admin user disabled)"
}

$acrId = az acr show --name $registryName --resource-group $ResourceGroupName --query id -o tsv
$registryLoginServer = az acr show --name $registryName --resource-group $ResourceGroupName --query loginServer -o tsv

# Grant AcrPush role to service principal
# Least privilege: CI/CD can push images but can't delete or modify ACR settings.
Write-Host "Granting AcrPush role to service principal..."
$existingRoleAssignment = az role assignment list `
    --assignee $spAppId `
    --role "AcrPush" `
    --scope $acrId `
    --query "[0].id" -o tsv 2>$null

if ($existingRoleAssignment) {
    Write-Success "AcrPush role already assigned"
}
else {
    az role assignment create `
        --assignee $spAppId `
        --role "AcrPush" `
        --scope $acrId | Out-Null
    Write-Success "AcrPush role assigned"
}

# ============================================================================
# CONTAINER APPS ENVIRONMENT (idempotent: check if exists, create if missing)
# Required infrastructure for logging, scaling, and networking across Container Apps.
# ============================================================================

Write-Section "Container Apps Environment"
$envName = "myimpact-demo-env"
$existingEnv = az containerapp env list --resource-group $ResourceGroupName --query "[0].name" -o tsv 2>$null

if ($existingEnv) {
    Write-Success "Environment already exists: $existingEnv"
}
else {
    Write-Host "Creating Container Apps environment: $envName"
    az containerapp env create `
        --name $envName `
        --resource-group $ResourceGroupName `
        --location $AzureRegion | Out-Null
    Write-Success "Environment created"
}

# ============================================================================
# OUTPUT GITHUB SECRETS
# ============================================================================

Write-Section "GitHub Secrets Configuration"

# Regenerate credentials for GitHub Secrets (safe: just displays app ID for manual setup)
if ($spOutput) {
    # New SP was created, show the full credentials
    Write-Host "⚠️  SAVE THESE CREDENTIALS:" -ForegroundColor Red
    Write-Host "`nAZURE_CREDENTIALS (full JSON):" -ForegroundColor Yellow
    Write-Host ($spOutput | ConvertTo-Json -Depth 10)
    
    $azureCredentials = $spOutput
}
else {
    # SP already existed, cannot retrieve secret again (security best practice in Azure AD)
    Write-Info "Service principal already exists. For new credentials, manually run:"
    Write-Host "  az ad sp create-for-rbac --name $spName --role Contributor --scopes $resourceGroupId --json-auth" -ForegroundColor Gray
    $azureCredentials = $null
}

$secretsOutput = @{
    "AZURE_CREDENTIALS" = if ($azureCredentials) { $azureCredentials | ConvertTo-Json -Depth 10 } else { "MANUALLY RETRIEVE OR REGENERATE (see above)" }
    "AZURE_RESOURCE_GROUP" = $ResourceGroupName
    "AZURE_REGISTRY_LOGIN_SERVER" = $registryLoginServer
    "CONTAINER_APP_NAME" = "myimpact-demo-api"
    "CONTAINER_APPS_ENV" = $envName
}

Write-Host "`nAll Secrets to Add to GitHub:" -ForegroundColor Yellow
Write-Host "  → Go to: GitHub Repo → Settings → Secrets and variables → Actions"
Write-Host "  → Click 'New repository secret' and add each value below:`n"

$secretsOutput.GetEnumerator() | ForEach-Object {
    Write-Host "Key: $($_.Key)" -ForegroundColor Cyan
    if ($_.Key -eq "AZURE_CREDENTIALS" -and $azureCredentials) {
        Write-Host "Value: (full JSON, see above)" -ForegroundColor Green
    }
    elseif ($_.Key -eq "AZURE_CREDENTIALS") {
        Write-Host "Value: (requires manual setup - see message above)" -ForegroundColor Yellow
    }
    else {
        Write-Host "Value: $($_.Value)" -ForegroundColor Green
    }
    Write-Host ""
}

# Save to file for reference
$secretsOutput | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputSecrets -Encoding UTF8
Write-Success "Secrets saved to: $OutputSecrets (reference only, do not commit)"

# ============================================================================
# NEXT STEPS
# ============================================================================

Write-Section "Next Steps"

Write-Host @"
1️⃣  Configure GitHub Secrets (5 min):
    - Go to: GitHub Repo → Settings → Secrets and variables → Actions
    - Add the 5 secrets shown above
    
2️⃣  Deploy application (5-10 min):
    git add .
    git commit -m "Deploy to Azure"
    git push origin main
    
    Then monitor in GitHub → Actions tab

3️⃣  Verify deployment:
    # Wait for workflow to complete, then:
    `$container_app_url = az containerapp show ``
      --name myimpact-demo-api ``
      --resource-group $ResourceGroupName ``
      --query 'properties.configuration.ingress.fqdn' -o tsv
    
    curl "https://`$container_app_url/api/health"
    # Expected: {"status":"healthy","version":"0.1.0"}

🗑️  Cleanup (when done):
    az group delete --name $ResourceGroupName --yes --no-wait
"@

Write-Success "Azure setup complete!"
