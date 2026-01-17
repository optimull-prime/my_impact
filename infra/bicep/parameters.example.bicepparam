@description('Resource group location')
param location string = 'eastus'

@description('Project name')
param projectName string = 'myimpact'

@description('Environment name')
param environment string = 'demo'

@description('Container image tag')
param containerImageTag string = 'latest'

var resourceNamePrefix = '${projectName}-${environment}'
var commonTags = {
  project: projectName
  environment: environment
  managedBy: 'bicep'
}

// Deploy container infrastructure
module containerInfra './main.bicep' = {
  name: 'container-infrastructure'
  params: {
    location: location
    projectName: projectName
    environment: environment
    containerImageName: 'myimpact-api'
    containerImageTag: containerImageTag
  }
}

// Outputs
output containerRegistryLoginServer string = containerInfra.outputs.containerRegistryLoginServer
output containerRegistryName string = containerInfra.outputs.containerRegistryName
output containerAppUrl string = containerInfra.outputs.containerAppUrl
output containerAppFqdn string = containerInfra.outputs.containerAppFqdn
