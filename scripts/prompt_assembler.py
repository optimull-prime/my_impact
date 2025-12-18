"""MyImpact — Prompt Assembler

Loads CSV data (culture expectations by scale) and markdown prompt files (org themes).
Assembles context for LLM goal generation.

Supports:
- Multiple Radford scales (technical, leadership, etc.), each with its own CSV
- Multiple organizations, each with its own org_themes_{orgname}.md file
- Goal styles: independent or progressive
"""

import argparse
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROMPTS = BASE / "prompts"
DATA = BASE / "data"


def load_markdown_file(filename: str) -> str:
    """Load a markdown file from prompts/."""
    path = PROMPTS / filename
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def load_culture_csv(scale: str, level_code: str) -> str:
    """Load culture expectations for a given scale and level from CSV.

    Looks for culture_expectations_{scale}.csv in data/.
    Extracts the column matching the level code and returns a formatted markdown section.
    """
    csv_path = DATA / f"culture_expectations_{scale}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Culture CSV not found: {csv_path}")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No culture expectations found in {csv_path}")

    # Find the column header that matches this level code
    # Columns are like "L10–15 (Entry)" or "L20–25 (Developing)"
    target_column = None
    for col in rows[0].keys():
        if level_code.upper() in col.upper() or col.startswith(level_code):
            target_column = col
            break

    if not target_column:
        raise ValueError(
            f"Level {level_code} not found in {csv_path}. Available levels: {', '.join(rows[0].keys())}"
        )

    # Extract level label from column header (e.g., "L10–15 (Entry)" -> "L10–15 Entry")
    level_label = target_column.replace("(", "").replace(")", "").strip()

    # Build markdown section
    markdown = f"## Cultural Expectations for {scale.title()} Track — {level_label}\n\n"
    for row in rows:
        attribute = row["Cultural Attribute"]
        expectation = row[target_column]
        markdown += f"### {attribute}\n{expectation}\n\n"

    return markdown.strip()


def load_org_themes(org: str) -> str:
    """Load org themes markdown file for a specific organization.

    Looks for org_themes_{org}.md in prompts/.
    """
    path = PROMPTS / f"org_themes_{org}.md"
    if not path.exists():
        raise FileNotFoundError(f"Org themes file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def discover_scales() -> list:
    """Discover all available Radford scales from CSV files in data/."""
    scales = []
    for csv_file in DATA.glob("culture_expectations_*.csv"):
        scale_name = csv_file.stem.replace("culture_expectations_", "")
        scales.append(scale_name)
    return sorted(scales)


def discover_levels(scale: str) -> list:
    """Discover all available levels for a given scale from CSV column headers."""
    csv_path = DATA / f"culture_expectations_{scale}.csv"
    if not csv_path.exists():
        return []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        # Skip "Cultural Attribute" column, extract level columns
        levels = [col for col in reader.fieldnames if col != "Cultural Attribute"]

    return levels


def discover_orgs() -> list:
    """Discover all available organizations from org_themes_*.md files."""
    orgs = []
    for md_file in PROMPTS.glob("org_themes_*.md"):
        org_name = md_file.stem.replace("org_themes_", "")
        orgs.append(org_name)
    return sorted(orgs)


def _get_goal_style_guidance(goal_style: str) -> str:
    """Return guidance text based on goal style."""
    if goal_style == "progressive":
        return """**Progressive (4-Goal Progression):**
Generate exactly 4 goals that build upon one another across a year-long journey (Q1 → Q4).
Each goal should:
- Demonstrate deepening expertise, leadership, or influence
- Build on the previous quarter's outcomes
- Show determination and commitment to seeing a multi-quarter initiative through
- Together, tell a cohesive narrative of growth and impact
- Example: Q1 (learn), Q2 (deepen), Q3 (lead), Q4 (mentor/scale)

This style demonstrates sustained focus and leadership maturity."""
    else:  # independent
        return """**Independent (6–9 Standalone Goals):**
Generate 6–9 goals that are independent and can be pursued in any order or concurrently.
Each goal is self-contained:
- No dependencies between goals
- Can start, pause, or complete any goal without affecting others
- Provides flexibility and autonomy
- Covers diverse skill areas and growth domains"""


def print_options():
    """Print all available configuration options."""
    print("=" * 70)
    print("MYIMPACT CONFIGURATION OPTIONS")
    print("=" * 70)

    # Scales and Levels
    print("\n## RADFORD SCALES & LEVELS\n")
    for scale in discover_scales():
        levels = discover_levels(scale)
        print(f"Scale: {scale}")
        for level in levels:
            print(f"  - {level}")

    # Growth Intensities
    print("\n## GROWTH INTENSITIES\n")
    intensities = ["minimal", "moderate", "aggressive"]
    for intensity in intensities:
        print(f"  - {intensity}")

    # Goal Styles
    print("\n## GOAL STYLES\n")
    print("  - independent (6–9 standalone goals)")
    print("  - progressive (4 quarterly goals that build upon each other)")

    # Organizations
    print("\n## ORGANIZATIONS\n")
    for org in discover_orgs():
        print(f"  - {org}")

    print("\n" + "=" * 70)


def assemble_prompt(
    scale: str,
    level: str,
    growth_intensity: str,
    org: str = "demo",
    theme: str | None = None,
    goal_style: str = "independent",
):
    """
    Assemble a complete system + user prompt from modular CSV and markdown files.

    Args:
        scale: e.g., "technical" or "leadership"
        level: e.g., "L3" or "L5" (can be any level code)
        growth_intensity: "minimal", "moderate", or "aggressive"
        org: organization name for org_themes_{org}.md (default: "demo")
        theme: optional strategic theme to include
        goal_style: "independent" or "progressive" (default: "independent")
    """

    # Load base system prompt from external file
    try:
        system = load_markdown_file("goal_generation_system_prompt.txt")
    except FileNotFoundError:
        # Fallback system prompt if file not found
        system = """You are MyImpact, an AI assistant that generates quarterly, SMART, locus-of-control career goals for employees.

Generate SMART quarterly goals with rationale explaining how each aligns to cultural principles, level expectations, and org themes."""

    # Load culture expectations from scale-specific CSV
    try:
        culture_section = load_culture_csv(scale, level)
    except (FileNotFoundError, ValueError) as e:
        return {"system": system, "user": f"Error: {e}"}

    # Load org themes (optional)
    theme_section = ""
    if theme:
        try:
            org_themes = load_org_themes(org)
            # Look for the theme in the markdown (flexible format support)
            if theme in org_themes:
                start = org_themes.find(theme)
                # Find where this theme starts (might be after whitespace/newlines)
                start = org_themes.rfind("\n", 0, start) + 1 if start > 0 else 0
                # Find the next theme-level line (no leading dash) or end of file
                lines_after = org_themes[start:].split("\n")
                theme_lines = [lines_after[0]]
                for line in lines_after[1:]:
                    # Stop at next non-indented line (next theme)
                    if line and not line[0].isspace() and not line.startswith("-"):
                        break
                    if line.strip():
                        theme_lines.append(line)
                theme_section = "\n".join(theme_lines).strip()
        except FileNotFoundError:
            pass  # Org theme file missing; continue without it

    # Build user context
    user_context = f"""## Your Context

**Organization:** {org.title()}
**Radford Scale:** {scale.title()}
**Level:** {level}
**Growth Intensity:** {growth_intensity}
**Goal Style:** {goal_style.title()}
{f"**Strategic Theme Bias:** {theme}" if theme else ""}

---

## Goal Style Definition

{_get_goal_style_guidance(goal_style)}

---

## Cultural Expectations and Level Context

{culture_section}

---

## Goal Generation Principles

1. **Locus of Control:** Goals must be within your control. Avoid depending on external OKRs, company strategy, or actions by teams you don't influence.
2. **Quarterly Cadence:** Think in quarters, not annual cycles. Smaller, focused goals are more motivating and measurable.
3. **Growth Intensity:** Consider {growth_intensity} growth for each goal (minimal = foundational, moderate = ambitious but achievable, aggressive = stretch).
4. **SMART Criteria:** Specific, Measurable, Achievable, Relevant, Time-bound.
5. **Career Growth:** Goals should advance your skills, influence, or impact in a way that translates across roles or companies.
6. **Variety:** Vary goal topics and metrics across runs. Each generation should explore new areas and creative approaches.

{f"## Organization Theme{chr(10)}{chr(10)}{theme_section}" if theme_section else ""}
"""

    return {"system": system, "user": user_context}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Assemble MyImpact goal generation prompt from CSV and text files"
    )
    parser.add_argument(
        "--list-options",
        action="store_true",
        help="List all available scales, levels, growth intensities, and goal styles",
    )
    parser.add_argument(
        "scale", nargs="?", help="Radford scale (e.g., technical, leadership)"
    )
    parser.add_argument("level", nargs="?", help="Radford level (e.g., L3, L5, L70)")
    parser.add_argument(
        "growth_intensity",
        nargs="?",
        help="Growth intensity (minimal, moderate, aggressive)",
    )
    parser.add_argument(
        "--org", default="demo", help="Organization name (default: demo)"
    )
    parser.add_argument(
        "--theme",
        help="Optional strategic theme to bias (e.g., 'Standardize for Speed and Interchangeability')",
    )
    parser.add_argument(
        "--goal-style",
        default="independent",
        choices=["independent", "progressive"],
        help="Goal generation style: independent (6–9 standalone) or progressive (4 quarterly progression) (default: independent)",
    )

    args = parser.parse_args()

    # Handle --list-options flag
    if args.list_options:
        print_options()
        exit(0)

    # Validate required arguments if not listing options
    if not args.scale or not args.level or not args.growth_intensity:
        parser.error(
            "scale, level, and growth_intensity are required (unless using --list-options)"
        )

    try:
        prompt = assemble_prompt(
            args.scale,
            args.level,
            args.growth_intensity,
            args.org,
            args.theme,
            args.goal_style,
        )

        print("=" * 70)
        print("MYIMPACT SYSTEM PROMPT")
        print("=" * 70)
        print(prompt["system"])

        print("\n" + "=" * 70)
        print("USER CONTEXT")
        print("=" * 70)
        print(prompt["user"])

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
