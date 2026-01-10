// Main Bicep template for MyImpact deployment to Azure
// Deploys: Container Registry, Container Apps, Static Web Apps

param location string = resourceGroup().location
param projectName string = 'myimpact'
param environment string = 'demo'
param containerImageName string = 'myimpact-api'
param containerImageTag string = 'latest'

// Derived names
var resourceNamePrefix = '${projectName}-${environment}'
var containerRegistryName = replace('${resourceNamePrefix}acr', '-', '')
var containerAppName = '${resourceNamePrefix}-api'
var containerAppsEnvName = '${resourceNamePrefix}-env'
var staticWebAppName = '${resourceNamePrefix}'

// Tags for all resources
var commonTags = {
  project: projectName
  environment: environment
  managedBy: 'bicep'
  createdDate: utcNow('u')
}

// ============================================================================
// Azure Container Registry
// ============================================================================
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: containerRegistryName
  location: location
  tags: commonTags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// Container Apps Environment
// ============================================================================
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: containerAppsEnvName
  location: location
  tags: commonTags
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
  }
}

// ============================================================================
// Container App (MyImpact API)
// ============================================================================
resource containerApp 'Microsoft.App/containerApps@2023-11-02-preview' = {
  name: containerAppName
  location: location
  tags: commonTags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'Auto'
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: [
        {
          name: 'registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerImageName
          image: '${containerRegistry.properties.loginServer}/${containerImageName}:${containerImageTag}'
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-requests'
            custom: {
              query: 'http_requests_per_second'
              threshold: '100'
            }
          }
        ]
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output containerRegistryName string = containerRegistry.name
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerAppsEnvironmentId string = containerAppsEnvironment.id
