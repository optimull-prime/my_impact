# MyImpact

**MyImpact** helps employees generate quarterly, SMART, career goals aligned to company culture, job-family expectations, and personal growth. Built on LLM technology with structured grounding (no RAG in early phases).

Assumption: curated knowledge (culture × Radford level × job-family + optional org themes) fits within a ~256K context window. We use structured grounding (no RAG in early phases) to assemble concise prompts for LLM goal generation and a chat-based refinement experience.

## Phase 0 (POC)
- Persist cultural principles mapped to Radford levels (higher level → higher expectations).
- Compute expectation profile: culture × level × job-family.
- Generate 6–9 SMART quarterly goals across growth bands (minimal, moderate, aggressive); enforce locus of control.
- Chat refinement (tighten metrics, split/merge, adjust growth band); export to Markdown/CSV.
- Dev-only auth: Entra ID single-tenant or demo-mode bias prompt.

## Curated Knowledge
Admins can freely edit CSV files under `data/`:
- `culture_expectations_technical.csv` — Cultural attributes + manifestations across technical Radford levels (L10–15 through L60–65).
- `culture_expectations_leadership.csv` — Cultural attributes + manifestations across leadership Radford levels (L70–75 through L100+).
- Add more scales as needed (e.g., `culture_expectations_product.csv`).

Markdown files under `prompts/`:
- `org_themes_{orgname}.md` — Strategic themes and organizational context per organization (e.g., `org_themes_demo.md`, `org_themes_acme.md`).
- Admins can easily edit these in any text editor.

## Prompt Assembly
See `scripts/prompt_assembler.py` for assembling a complete system+user prompt. It:
1. Loads the culture CSV for the selected scale and level.
2. Extracts the cultural attributes and expectations.
3. Loads org themes for the specified organization (optional theme bias).
4. Outputs system + user prompt ready for Azure OpenAI.

## Multi-Tenant & Multi-Org Support
The system supports multiple organizations, each with independent strategic themes:
- Each organization has its own `org_themes_{orgname}.md` file.
- Sensitive org data can be access-controlled later via Entra ID roles and groups (no individual users).
- Currently, all data is accessible; role-based access to follow in Phase 2+.

## Dev→Prod Portability (Azure)
- App: Azure App Service or Static Web Apps + Functions (API).
- LLM: Azure OpenAI for chat completions.
- Data: Cosmos DB (tenant-partitioned). Key Vault for secrets. Managed Identities.
- IaC: Bicep modules with per-env parameters.

## Next
- Finalize curated datasets and expectation profile assembly.
- Implement minimal API and chat UI.
