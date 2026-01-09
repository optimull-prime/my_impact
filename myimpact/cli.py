"""Command-line interface for MyImpact goal generator."""

import click
from pathlib import Path
from myimpact.assembler import (
    load_culture_csv,
    extract_levels_from_csv,
    assemble_prompt,
    _get_resource_dir,
)

GROWTH_INTENSITIES = ["minimal", "moderate", "aggressive"]
GOAL_STYLES = ["independent", "progressive"]


def discover_org_names() -> list:
    """Discover available organizations from org_focus_areas_*.md files."""
    prompts_dir = _get_resource_dir("prompts")
    org_names = []
    for file in prompts_dir.glob("org_focus_areas_*.md"):
        org_name = file.stem.replace("org_focus_areas_", "")
        org_names.append(org_name)
    return sorted(org_names)


def discover_scales() -> list:
    """Discover available scales from culture_expectations_*.csv files."""
    data_dir = _get_resource_dir("data")
    scales = []
    for file in data_dir.glob("culture_expectations_*.csv"):
        scale = file.stem.replace("culture_expectations_", "")
        scales.append(scale)
    return sorted(scales)


@click.group()
def main():
    """MyImpact: AI-powered quarterly goal generation."""
    pass


@main.command()
@click.argument("scale", type=str)
@click.argument("level", type=str)
@click.argument("growth_intensity", type=click.Choice(GROWTH_INTENSITIES))
@click.option("--org", default="demo", help="Organization name (default: demo)")
@click.option("--focus_area", default=None, help="Strategic focus area to bias goal generation")
@click.option(
    "--goal-style",
    type=click.Choice(GOAL_STYLES),
    default="independent",
    help="Goal generation style",
)
def generate(scale, level, growth_intensity, org, focus_area, goal_style):
    """Generate a prompt for goal creation."""
    try:
        framework_prompt, user_prompt = assemble_prompt(
            scale=scale,
            level=level,
            growth_intensity=growth_intensity,
            org_name=org,
            focus_area=focus_area,
            goal_style=goal_style,
        )
        click.echo("=" * 80)
        click.echo("GOAL FRAMEWORK")
        click.echo("=" * 80)
        click.echo(framework_prompt)
        click.echo("\n" + "=" * 80)
        click.echo("USER CONTEXT")
        click.echo("=" * 80)
        click.echo(user_prompt)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.exceptions.Exit(1)


@main.command()
def list_options():
    """List all available configuration options."""
    scales = discover_scales()
    org_names = discover_org_names()

    click.echo("\n" + "=" * 80)
    click.echo("AVAILABLE JOB LEVEL SCALES")
    click.echo("=" * 80)
    for scale in scales:
        click.echo(f"\n{scale.upper()}")
        levels = extract_levels_from_csv(scale)
        for level in levels:
            click.echo(f"  - {level}")

    click.echo("\n" + "=" * 80)
    click.echo("GROWTH INTENSITIES")
    click.echo("=" * 80)
    for intensity in GROWTH_INTENSITIES:
        click.echo(f"  - {intensity}")

    click.echo("\n" + "=" * 80)
    click.echo("GOAL STYLES")
    click.echo("=" * 80)
    for style in GOAL_STYLES:
        click.echo(f"  - {style}")

    click.echo("\n" + "=" * 80)
    click.echo("ORGANIZATIONS")
    click.echo("=" * 80)
    for org in org_names:
        click.echo(f"  - {org}")

    click.echo()


if __name__ == "__main__":
    main()
