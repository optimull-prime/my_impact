# MyImpact — Usage (POC Demo)

## Edit Culture Expectations
1. Open `data/culture_expectations_technical.csv` or `data/culture_expectations_leadership.csv` in Excel or Google Sheets.
2. Add or edit cultural attributes and level expectations as needed.
3. Save as CSV.
4. Repeat for other scales if needed.

## Edit Org Themes
5. Open `prompts/org_themes_demo.md` (or create new files like `org_themes_acme.md` for other organizations).
6. Edit strategic themes and their implications for each level.
7. Save as markdown.

## Generate Context
8. Assemble a MyImpact prompt for a specific organization and level:

### List Available Options
View all scales, levels, growth intensities, goal styles, and organizations:
```powershell
python .\scripts\prompt_assembler.py --list-options
```

### Independent Goals (Default)
Generate 6–9 standalone goals with no dependencies:
```powershell
# Default: independent goals, demo org, technical track, L30, moderate growth
python .\scripts\prompt_assembler.py technical L30 moderate

# With theme bias
python .\scripts\prompt_assembler.py technical L30 moderate --theme "Standardize for Speed and Interchangeability"

# Leadership track
python .\scripts\prompt_assembler.py leadership L80 moderate --org demo

# Aggressive growth intensity
python .\scripts\prompt_assembler.py technical L40 aggressive --org demo
```

### Progressive Goals
Generate 4 quarterly goals that build upon each other (Q1 → Q4):
```powershell
# Progressive goals, technical track, L50, aggressive growth
python .\scripts\prompt_assembler.py technical L50 aggressive --goal-style progressive

# Progressive with theme bias
python .\scripts\prompt_assembler.py technical L40 moderate --goal-style progressive --theme "Increase productivity"

# Leadership track, progressive
python .\scripts\prompt_assembler.py leadership L90 aggressive --goal-style progressive --org demo
```

### Goal Style Comparison
- **Independent** (default): Flexibility to pursue goals in any order; ideal for diverse skill development
- **Progressive**: 4-goal narrative arc across quarters; demonstrates leadership maturity and sustained commitment

9. Review system and user context output. Wire to Azure OpenAI in the API when ready.

## Export Flow
10. Export will render goals to Markdown/CSV.
