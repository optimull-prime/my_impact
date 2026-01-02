"""Tests for myimpact.assembler module."""

import pytest
from pathlib import Path
from myimpact.assembler import (
    load_culture_csv,
    load_org_themes,
    load_system_prompt,
    extract_levels_from_csv,
    extract_culture_for_level,
    discover_scales,
    discover_orgs,
    discover_levels,
    assemble_prompt,
)


class TestResourceLoading:
    """Test resource file loading functions."""

    def test_load_culture_csv_technical(self):
        """Test loading technical culture CSV."""
        culture = load_culture_csv("technical")
        assert isinstance(culture, dict)
        assert len(culture) == 8  # 8 cultural attributes
        assert "Humble" in culture
        assert "Ownership" in culture

    def test_load_culture_csv_leadership(self):
        """Test loading leadership culture CSV."""
        culture = load_culture_csv("leadership")
        assert isinstance(culture, dict)
        assert len(culture) == 8
        assert "Humble" in culture
        assert "Ownership" in culture

    def test_load_culture_csv_invalid_scale(self):
        """Test that loading invalid scale raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_culture_csv("invalid_scale")

    def test_load_org_themes_demo(self):
        """Test loading demo org themes."""
        themes = load_org_themes("demo")
        assert isinstance(themes, str)
        assert len(themes) > 0
        # Demo file may or may not have markdown headers, just check it loads

    def test_load_org_themes_invalid(self):
        """Test that loading invalid org raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_org_themes("nonexistent_org")

    def test_load_system_prompt(self):
        """Test loading system prompt."""
        prompt = load_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "MyImpact" in prompt
        assert "SMART" in prompt


class TestDiscoveryFunctions:
    """Test resource discovery functions."""

    def test_discover_scales(self):
        """Test scale discovery from CSV files."""
        scales = discover_scales()
        assert isinstance(scales, list)
        assert "technical" in scales
        assert "leadership" in scales
        assert len(scales) >= 2

    def test_discover_orgs(self):
        """Test organization discovery from markdown files."""
        orgs = discover_orgs()
        assert isinstance(orgs, list)
        assert "demo" in orgs

    def test_discover_levels_technical(self):
        """Test level discovery for technical scale."""
        levels = discover_levels("technical")
        assert isinstance(levels, list)
        assert len(levels) == 6  # L10–L60
        assert "L30–35 (Career)" in levels

    def test_discover_levels_leadership(self):
        """Test level discovery for leadership scale."""
        levels = discover_levels("leadership")
        assert isinstance(levels, list)
        assert len(levels) == 4  # L70–L100+
        assert "L80–85 (VP)" in levels


class TestLevelExtraction:
    """Test level extraction and culture filtering."""

    def test_extract_levels_from_csv_technical(self):
        """Test extracting levels from technical CSV."""
        levels = extract_levels_from_csv("technical")
        assert isinstance(levels, list)
        assert len(levels) == 6
        assert all("L" in level for level in levels)

    def test_extract_culture_for_level(self):
        """Test extracting culture expectations for specific level."""
        culture = extract_culture_for_level("technical", "L30–35 (Career)")
        assert isinstance(culture, dict)
        assert len(culture) == 8
        assert "Humble" in culture
        assert "Shows self‑awareness" in culture["Humble"]

    def test_extract_culture_for_invalid_level(self):
        """Test that extracting invalid level returns empty dict."""
        culture = extract_culture_for_level("technical", "L99 (Invalid)")
        assert culture == {}


class TestPromptAssembly:
    """Test prompt assembly orchestration."""

    def test_assemble_prompt_basic(self):
        """Test basic prompt assembly."""
        system, user = assemble_prompt(
            scale="technical",
            level="L30–35 (Career)",
            growth_intensity="moderate",
            org_name="demo",
            goal_style="independent",
        )

        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "MyImpact" in system
        assert "L30–35 (Career)" in user
        assert "technical" in user.lower()
        assert "moderate" in user
        assert "independent" in user

    def test_assemble_prompt_with_theme(self):
        """Test prompt assembly with theme."""
        system, user = assemble_prompt(
            scale="leadership",
            level="L80–85 (VP)",
            growth_intensity="aggressive",
            org_name="demo",
            theme="Innovation",
            goal_style="progressive",
        )

        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "L80–85 (VP)" in user
        assert "leadership" in user.lower()
        assert "aggressive" in user
        assert "progressive" in user

    def test_assemble_prompt_invalid_level(self):
        """Test that invalid level raises ValueError."""
        with pytest.raises(ValueError, match="No culture data found"):
            assemble_prompt(scale="technical", level="L99 (Invalid)", growth_intensity="moderate")


class TestDataIntegrity:
    """Test data file integrity and format."""

    def test_csv_no_empty_attributes(self):
        """Test that CSVs don't have empty attribute names."""
        for scale in discover_scales():
            culture = load_culture_csv(scale)
            for attr_name in culture.keys():
                assert attr_name.strip() != ""
                assert attr_name is not None

    def test_csv_all_attributes_have_levels(self):
        """Test that all attributes have data for all levels."""
        culture_tech = load_culture_csv("technical")
        levels_tech = extract_levels_from_csv("technical")

        for attr_name, level_data in culture_tech.items():
            # Filter out None keys from CSV parsing quirks
            valid_levels = {
                k: v for k, v in level_data.items() if k is not None and k.startswith("L")
            }
            assert len(valid_levels) == len(
                levels_tech
            ), f"Attribute '{attr_name}' has {len(valid_levels)} levels, expected {len(levels_tech)}"

    def test_level_names_consistent(self):
        """Test that level names are consistently formatted."""
        for scale in discover_scales():
            levels = extract_levels_from_csv(scale)
            for level in levels:
                # Should have format like "L10–15 (Entry)" or "L100+ (C-Level)"
                assert level.startswith("L"), f"Level '{level}' doesn't start with 'L'"
                assert "(" in level and ")" in level, f"Level '{level}' missing parentheses"
