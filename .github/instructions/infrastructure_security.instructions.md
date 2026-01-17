---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "infra/**"
description: Infrastructure Security Best Practices
---

# Infrastructure Security Best Practices

## Managed Identity (Always Required)

- **ALWAYS use Azure Managed Identity** when connecting Azure services together
- **NEVER use admin credentials, connection strings, or API keys** when Managed Identity is available
- Common scenarios:
  - Container Apps → Container Registry: Use Managed Identity with AcrPull role
  - Container Apps → Key Vault: Use Managed Identity with Key Vault Secrets User role
  - Container Apps → Storage Account: Use Managed Identity with Storage Blob Data Contributor role
  - Function Apps → Any Azure service: Use Managed Identity first

## Azure Container Registry

- Set `adminUserEnabled: false` (admin user is a security risk)
- Use Managed Identity with `AcrPull` role assignment for pulling images
- Use Azure CLI or Service Principal only for CI/CD pipelines (temporary, scoped credentials)

## Secrets Management

- Store secrets in Azure Key Vault, not in app configuration
- Use Managed Identity to access Key Vault
- Reference Key Vault secrets in Container Apps using `secretStoreComponent`

## Role-Based Access Control (RBAC)

- Always use principle of least privilege
- Assign specific roles (e.g., `AcrPull`) instead of broad roles (e.g., `Contributor`)
- Document why each role assignment is necessary