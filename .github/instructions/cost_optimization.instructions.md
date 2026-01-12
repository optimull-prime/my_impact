---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "infra/**"
description: Cost Optimization (Hints)
---

# Cost Optimization (Hints)

DO:
- Use consumption-based services (Container Apps consumption, Static Web Apps Free).
- Right-size: 0.25–0.5 vCPU, 0.5–1 GiB RAM for demo/dev.
- Set minReplicas 0–1; cap maxReplicas (e.g., 3 for demo).
- Tag resources (project, environment, owner); set cleanup dates.
- Disable ACR admin user; enable image retention and delete unused images.
- Keep all resources in one region; set budgets and alerts.

DO NOT:
- Use Premium SKUs for demo/dev.
- Leave idle services running 24/7.
- Store long-lived credentials in GitHub; prefer managed identity/OIDC.
- Overprovision replicas “just in case.”