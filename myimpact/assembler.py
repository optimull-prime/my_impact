"""Prompt assembler: loads culture CSVs, org focus areas, and system prompt to generate LLM context."""

import csv
import os
from pathlib import Path
from typing import Optional


def _get_resource_dir(subdir: str) -> Path:
    """Resolve resource directory relative to package root, supporting both dev and installed modes."""
    package_root = Path(__file__).parent.parent
    resource_path = package_root / subdir
    if resource_path.exists():
        return resource_path
    # Fallback for editable install
    return package_root / subdir


def load_culture_csv(scale: str) -> dict:
    """Load culture expectations CSV by scale (e.g., 'technical', 'leadership')."""
    data_dir = _get_resource_dir("data")
    csv_path = data_dir / f"culture_expectations_{scale}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Culture CSV not found: {csv_path}")

    culture = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            attr_name = row.get("Cultural Attribute", "").strip()
            if not attr_name:  # Skip empty rows
                continue
            culture[attr_name] = {k: v for k, v in row.items() if k != "Cultural Attribute"}
    return culture


def load_org_focus_areas(org_name: str) -> str:
    """Load org focus areas markdown file."""
    prompts_dir = _get_resource_dir("prompts")
    focus_areas_path = prompts_dir / f"org_focus_areas_{org_name}.md"

    if not focus_areas_path.exists():
        raise FileNotFoundError(f"Org focus areas file not found: {focus_areas_path}")

    with open(focus_areas_path, "r", encoding="utf-8") as f:
        return f.read()


def load_system_prompt() -> str:
    """Load goal generation system prompt."""
    prompts_dir = _get_resource_dir("prompts")
    prompt_path = prompts_dir / "goal_generation_system_prompt.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"System prompt not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def discover_scales() -> list[str]:
    """
    Discover available scales based on CSV files in data directory.
    Returns list of scale names (e.g. ['technical', 'leadership']).
    """
    data_dir = Path(__file__).parent.parent / "data"
    scales = []
    for file in data_dir.glob("culture_expectations_*.csv"):
        scale_name = file.stem.replace("culture_expectations_", "")
        scales.append(scale_name)
    return sorted(scales)


def discover_levels() -> dict[str, list[str]]:
    """
    Discover available levels for each scale.
    Returns a dictionary mapping scale names to lists of level strings.
    """
    scales = discover_scales()
    levels = {}
    for scale in scales:
        try:
            levels[scale] = extract_levels_from_csv(scale)
        except FileNotFoundError:
            levels[scale] = []
    return levels


def discover_orgs() -> list:
    """Discover available organizations from org_focus_areas_*.md files."""
    prompts_dir = _get_resource_dir("prompts")
    org_names = []
    for file in prompts_dir.glob("org_focus_areas_*.md"):
        org_name = file.stem.replace("org_focus_areas_", "")
        org_names.append(org_name)
    return sorted(org_names)


def extract_levels_from_csv(scale: str) -> list:
    """Extract available job levels from CSV column headers."""
    culture = load_culture_csv(scale)
    if not culture:
        return []
    # Get first attribute's keys (all should have same levels)
    first_attr = next(iter(culture.values()))
    return sorted(first_attr.keys())


def discover_levels(scale: str) -> list:
    """Discover available levels for a specific scale."""
    return extract_levels_from_csv(scale)


def extract_culture_for_level(scale: str, level: str) -> dict:
    """Extract culture expectations for a specific level."""
    culture = load_culture_csv(scale)
    result = {}
    for attr_name, levels in culture.items():
        if level in levels:
            result[attr_name] = levels[level]
    return result


def _get_growth_guidance(intensity: str) -> str:
    """Return growth intensity guidance for the LLM."""
    guidance = {
        "minimal": "Focus on foundational skill-building and consistency. Emphasize learning over output.",
        "moderate": "Balance learning with measurable contributions. Demonstrate reliability and growth.",
        "aggressive": "Stretch goals that build strategic capabilities. Show leadership and impact.",
    }
    return guidance.get(intensity, guidance["moderate"])


def _get_goal_style_guidance(style: str) -> str:
    """Return goal style guidance for the LLM."""
    guidance = {
        "independent": "Generate 6–9 standalone goals. Each goal is independent and can be pursued in any order.",
        "progressive": "Generate 4 quarterly goals that build upon each other. Each Q builds on prior success, demonstrating commitment and deepening expertise.",
    }
    return guidance.get(style, guidance["independent"])


def assemble_prompt(
    scale: str,
    level: str,
    growth_intensity: str,
    org_name: str = "demo",
    theme: Optional[str] = None,
    goal_style: str = "independent",
) -> tuple[str, str]:
    """
    Assemble system and user prompts from curated data.
    Returns: (system_prompt, user_context_prompt)
    """
    # Load and extract culture
    culture = extract_culture_for_level(scale, level)
    if not culture:
        raise ValueError(f"No culture data found for scale={scale}, level={level}")

    culture_text = "\n".join(
        [f"- **{attr}**: {expectation}" for attr, expectation in culture.items()]
    )

    # Load full org focus areas content (all strategic focus areas)
    try:
        org_focus_areas_full = load_org_focus_areas(org_name)
    except FileNotFoundError:
        org_focus_areas_full = ""

    # User-specified focus (optional emphasis on top of full org context)
    user_focus = theme.strip() if theme else ""

    # Load system prompt
    system_prompt = load_system_prompt()

    # Build user context
    growth_guidance = _get_growth_guidance(growth_intensity)
    goal_style_guidance = _get_goal_style_guidance(goal_style)

    user_context = f"""
## Context for Goal Generation

**Scale/Track**: {scale.capitalize()}
**Job Level**: {level}
**Growth Intensity**: {growth_intensity}
**Goal Style**: {goal_style}
**Organization**: {org_name}

### Cultural Expectations for {level}
{culture_text}

### Growth Intensity Guidance
{growth_guidance}

### Goal Style Guidance
{goal_style_guidance}
"""

    # Always include full organizational context
    if org_focus_areas_full:
        user_context += f"""
### Organizational Strategic Focus Areas
{org_focus_areas_full}
"""

    # Add user-specified focus if provided
    if user_focus:
        user_context += f"""
### Your Focus Areas
The user wants to emphasize the following areas or themes:
{user_focus}
"""

    user_context += """
### Your Task
Generate quarterly career goals that:
1. Demonstrate progress toward the cultural principles above.
2. Meet the job level expectations.
3. Include a rationale connecting each goal to the cultural principles and level expectations.
4. Follow the goal style (independent or progressive).
5. Respect the growth intensity band.
6. Maintain locus of control (goals should not depend on external company decisions).

Generate the goals now.
"""

    return system_prompt, user_context
