# MyImpact — Minimal API Spec (Phase 0)

## POST /api/goals/generate
Inputs:
- tenantId
- positionId
- levelCode
- growthIntensity (minimal|moderate|aggressive)

Process:
- Resolve expectation profile (culture × level × job-family).
- Assemble prompt (system + user context).
- Call Azure OpenAI chat completions.
- Return 6–9 SMART quarterly goals with metadata.

## POST /api/goals/refine
Inputs:
- goalSetId
- operations: [ tightenMetric | splitGoal | mergeGoals | adjustGrowthIntensity ]

Process:
- Apply deterministic transforms; re-evaluate SMART criteria.
- Optionally call LLM for phrasing improvements.

## GET /api/goals/export
Inputs:
- goalSetId
- format: markdown|csv

Process:
- Render and return download.
