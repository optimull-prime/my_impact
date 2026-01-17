---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "infra/**"
description: Operational Excellence (Hints)
---

# Operational Excellence (Hints)

DO:
- Use IaC (Bicep) for all infra; version and reuse modules.
- Automate CI/CD; add approvals for prod; no manual portal changes.
- Use managed identity for service-to-service auth.
- Implement health endpoints and probes; structured logging.
- Version images by commit/SemVer (avoid latest).
- Document env vars; keep runbooks minimal but current.

DO NOT:
- Commit secrets or configs to source control.
- Deploy via portal for prod.
- Skip health checks or rollback paths.