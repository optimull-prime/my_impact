---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "**"
description: Performance Efficiency (Hints)
---

# Performance Efficiency (Hints)

Targets (demo/low volume):
- Prompt generation: P95 ≤ 3s.
- Dropdown/metadata: P95 ≤ 1s.

DO:
- Cache metadata responses (e.g., 1h); use HTTP cache headers.
- Use async I/O; set timeouts (5–10s external calls).
- Paginate lists; filter fields to reduce payload.
- Rate limit expensive endpoints (e.g., 10/min).
- Tune scaling on real metrics (concurrentRequests, CPU).

DO NOT:
- Block event loop with sync I/O.
- Return unbounded arrays; avoid N+1 queries.
- Skip cache/headers for static and metadata content.