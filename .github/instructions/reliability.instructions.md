---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "**"
description: Reliability (Hints)
---

# Reliability (Hints)

DO:
- Use liveness/readiness probes; add retries with backoff, circuit breakers, timeouts.
- Keep rollback plan; test in dev before prod.
- Multiple replicas for prod (min 2); single replica acceptable for demo.
- Monitor key metrics (availability, error rate, restart count); alert on thresholds.

DO NOT:
- Run single replica in prod for critical paths.
- Use infinite retries or no timeouts.
- Store state in containers; use external stores.