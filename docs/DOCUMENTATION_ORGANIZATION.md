# Documentation Organization

This document explains how MyImpact documentation is organized and which files are public (version-controlled) vs private (event/development-specific).

## File Organization Strategy

### Public Documentation (Version-Controlled)

These files explain how to use and deploy MyImpact. They're useful for anyone who clones the repository.

**Location**: `/docs/` and root directory

| File | Purpose | Audience |
|---|---|---|
| [README.md](../README.md) | Project overview, quick links | Everyone |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | How to contribute | Contributors |
| [docs/guides/01-quick-start.md](guides/01-quick-start.md) | 5-minute local setup | Developers |
| [docs/guides/02-local-development.md](guides/02-local-development.md) | Full development guide | Developers |
| [docs/guides/03-deployment.md](guides/03-deployment.md) | Deploy to Azure | DevOps/Teams deploying |
| [docs/guides/04-demo-script.md](guides/04-demo-script.md) | Demo script (org-agnostic) | Anyone giving demos |
| [docs/api/README.md](api/README.md) | API reference | API consumers |
| [docs/api/spec.md](api/spec.md) | OpenAPI spec | Integrators |
| [docs/architecture/overview.md](architecture/overview.md) | High-level system design | Architects, contributors |
| [docs/architecture/system-overview.md](architecture/system-overview.md) | Components, deployment, scaling | Architects, DevOps |
| [docs/architecture/data-flow.md](architecture/data-flow.md) | Request/response lifecycle | Developers, integrators |
| [docs/architecture/security-design.md](architecture/security-design.md) | Security architecture (Well-Architected) | Security teams, architects |
| [docs/planning/](planning/) | Design decisions, phase docs | Historians, context seekers |
