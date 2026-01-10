param location string = 'eastus'
param projectName string = 'myimpact'
param environment string = 'demo'

@description('Container image tag to deploy')
param containerImageTag string = 'latest'

@description('GitHub repository owner/org')
param githubRepositoryOwner string

@description('GitHub repository name')
param githubRepositoryName string = 'my_impact'

@description('GitHub branch for Static Web Apps')
param githubBranch string = 'main'

@description('GitHub Personal Access Token for Static Web Apps deployment')
@secure()
param githubToken string

// Create resource group if needed (usually already exists)
targetScope = 'subscription'

// Create or use existing resource group
var resourceGroupName = '${projectName}-${environment}-rg'

resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
}

// Deploy main infrastructure
module infrastructure 'main.bicep' = {
  scope: rg
  name: 'infrastructure-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    containerImageTag: containerImageTag
  }
}

// Outputs for GitHub Actions workflow
output resourceGroupName string = rg.name
output containerRegistryLoginServer string = infrastructure.outputs.containerRegistryLoginServer
output containerAppUrl string = infrastructure.outputs.containerAppUrl
output containerAppsEnvironmentId string = infrastructure.outputs.containerAppsEnvironmentId
