# MyImpact

AI-powered quarterly goal generation aligned to company culture, Radford level expectations, and job-family competencies.

## Vision

**MyImpact** generates context-rich prompts to help employees create quarterly SMART goals aligned to:
- **Company cultural principles** (8 attributes: humble, hardworking, continuous learner, world-class, transparency, improvement, respect, ownership)
- **Level expectations** (technical L10–L65, leadership L30–L100+)
- **Organizational themes** (strategic priorities, focus areas, department level, team level context)

### Prompt-First Approach

The tool's **primary use case** is generating high-quality prompts that users can:
- **Copy into any LLM** (ChatGPT, Claude, Gemini, etc.) to generate personalized goals
- **Customize** with additional personal context before LLM submission
- **Use as templates** for self-reflection and goal planning sessions

**Future Enhancement**: Optional "Quick LLM" buttons if there's demand (currently API can integrate Azure OpenAI, but prompts-only mode is the focus).

## Quick Start

### 1. Set Up the Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate venv (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install package in editable mode with all dependencies
pip install -e ".[dev]"


# Or for Phase 1 API work:
pip install -e ".[dev,api,azure]"
```

### 2. List Available Options

```bash
myimpact list-options
```

### 3. Generate a Prompt

```bash
# Independent goals (default)
myimpact generate technical L30 moderate

# Progressive goals with org theme
myimpact generate leadership L80 aggressive --org demo --theme "Standardize for Speed and Interchangeability" --goal-style progressive
```

## Project Structure

```
myimpact/
  __init__.py          # Package metadata
  assembler.py         # Core prompt assembly logic
  cli.py              # CLI interface
data/
  culture_expectations_technical.csv
  culture_expectations_leadership.csv
prompts/
  goal_generation_system_prompt.txt
  org_themes_demo.md
```

## Admin Guide

### Editing Culture Expectations

1. Open `data/culture_expectations_[technical|leadership].csv` in Excel or Sheets.
2. Rows = cultural attributes; Columns = Radford levels.
3. Edit expectations; save as CSV.
4. Re-run CLI to validate: `myimpact list-options`

### Editing Organization Themes

1. Open `prompts/org_themes_[orgname].md`.
2. Add/edit strategic themes in markdown format.
3. Use theme names in CLI: `myimpact generate ... --theme "Theme Name"`

### Editing System Prompt

1. Open `prompts/goal_generation_system_prompt.txt`.
2. Update LLM behavior, output format, or constraints.
3. Changes apply to next CLI run.

## Phase Roadmap

- **Phase 0**: ✅ MVP prompt assembler, CLI, editable data files
- **Phase 1**: API, persistence (Cosmos DB), Azure OpenAI integration, auth (Entra ID)
- **Phase 2**: RAG (optional), org themes dimension, multi-tenant governance
- **Phase 3**: Production scaling, compliance, cost optimization

## Development

```bash
# Lint
black myimpact/
isort myimpact/

# Type check
mypy myimpact/

# Run tests
pytest

# Security scan
snyk code test myimpact/
```

## License

MIT
