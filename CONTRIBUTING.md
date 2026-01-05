# Contributing to MyImpact

## Admin Guide: Editing Curated Knowledge

### Culture & Job Leveling Expectations

**File**: `data/culture_expectations_[scale].csv`

Each row is a cultural attribute; each column is a job level. Edit cells with expected behaviors at each level.

**Example**:
| Cultural Attribute | L10–15 (Entry) | L20–25 (Developing) | ... |
| --- | --- | --- | --- |
| Humble | Listens first; asks for help readily. | Invites feedback; assumes positive intent. | ... |

**Validation**: After editing, run:
```bash
myimpact list-options
```
Verify that your scale and levels appear correctly.

### Organization Focus Areas

**File**: `prompts/org_focus_areas_[orgname].md`

Add strategic focus areas as markdown bullet points or sections. These bias goal generation toward org priorities.

**Example**:
```markdown
# Strategic Focus Areas for 2024

## Standardize for Speed and Interchangeability
- Consolidate tooling and reduce friction in deployment.
- Enable rapid onboarding and knowledge transfer.
- Measure: time-to-first-commit, deploy frequency.
```

**Validation**: After editing, run:
```bash
myimpact generate technical L30 moderate --org [orgname] --theme "Standardize for Speed and Interchangeability"
```
Verify that the focus area appears in the output.

### System Prompt

**File**: `prompts/goal_generation_system_prompt.txt`

Adjust LLM behavior: emphasis on locus of control, goal style, rationale, etc.

**Warning**: Changes apply globally. Test before pushing.

## Development

### Adding a New Scale

1. Create `data/culture_expectations_[newscale].csv` with cultural attributes and job levels.
2. Run `myimpact list-options` to verify.
3. Use in CLI: `myimpact generate [newscale] [level] [intensity]`

### Adding a New Organization

1. Create `prompts/org_focus_areas_[neworg].md` with strategic focus areas.
2. Run `myimpact list-options` to verify.
3. Use in CLI: `myimpact generate ... --org [neworg] --theme "..."`

## Testing

Run tests after changes:
```bash
pytest -v
```

## Security

- Do not commit `.env` files or secrets.
- Use `.env.example` as a template.
- Run Snyk scans on all new code: `snyk code test`

## Questions?

Reach out to the MyImpact team.