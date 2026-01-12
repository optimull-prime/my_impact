---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "**/*.md"
description: Documentation Standards (Hints)
---

# Documentation Standards (Hints)

DO:
- Use Mermaid diagrams (code-based, version-controllable, rendered by GitHub).
- Use ASCII art diagrams as fallback (if Mermaid insufficient).
- Keep docs up-to-date with code changes; link to relevant files.
- Use clear headings, tables, and code blocks for readability.
- Document "why" not just "what" (decisions, trade-offs, rationale).
- Use consistent terminology throughout the docs.
- Review docs as part of code reviews; ensure accuracy and clarity.  

DO NOT:
- Use external image files (PNG, JPG) for diagrams—hard to version control and maintain.
- Leave outdated docs in repo; delete or update them.
- Assume readers know the codebase; provide context and examples.
- Overcomplicate docs; keep them concise and focused.