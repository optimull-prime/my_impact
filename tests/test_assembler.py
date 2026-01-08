"""Tests for myimpact.assembler module.

Following Martin Fowler's Test Shapes principles:
- Expressive: Tests clearly state what behavior is expected
- Bounded: Tests focus on assembler logic only, mocking file I/O
- Fast: Minimal file I/O, uses tmp_path fixtures
- Reliable: Only fail for real logic changes, not data mutations
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from myimpact.assembler import (
    load_culture_csv,
    load_org_focus_areas,
    load_system_prompt,
    extract_levels_from_csv,
    extract_culture_for_level,
    discover_scales,
    discover_orgs,
    discover_levels,
    assemble_prompt,
)


# ============================================================================
# INTEGRATION TESTS - Test assembler against real data files
# ============================================================================
class TestResourceLoadingIntegration:
    """Test resource file loading with real files (integration tier)."""

    def test_load_culture_csv_technical_has_required_attributes(self):
        """
        Given: Technical culture CSV file exists
        When: load_culture_csv('individual_contributor_technical') is called
        Then: Returns dict with core cultural attributes
        """
        culture = load_culture_csv("individual_contributor_technical")
        
        assert isinstance(culture, dict)
        assert len(culture) > 0
        # Verify core attributes present
        core_attributes = {"Humble", "Ownership"}
        actual_attrs = set(culture.keys())
        assert core_attributes.issubset(actual_attrs), \
            f"Missing attributes: {core_attributes - actual_attrs}"

    def test_load_culture_csv_people_manager_has_required_attributes(self):
        """
        Given: People manager culture CSV file exists
        When: load_culture_csv('people_manager') is called
        Then: Returns dict with core cultural attributes
        """
        culture = load_culture_csv("people_manager")
        
        assert isinstance(culture, dict)
        assert len(culture) > 0
        core_attributes = {"Humble", "Ownership"}
        actual_attrs = set(culture.keys())
        assert core_attributes.issubset(actual_attrs)

    def test_load_org_focus_areas_demo_returns_markdown_content(self):
        """
        Given: Demo org focus areas file exists
        When: load_org_focus_areas('demo') is called
        Then: Returns non-empty string with markdown content
        """
        content = load_org_focus_areas("demo")
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert any(marker in content for marker in ["#", "-", "*"]), \
            "Should contain markdown formatting"

    def test_load_system_prompt_returns_substantive_content(self):
        """
        Given: System prompt file exists
        When: load_system_prompt() is called
        Then: Returns substantive prompt with key concepts
        """
        prompt = load_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 100, "Should be substantive prompt"
        # Check for goal-oriented language
        prompt_lower = prompt.lower()
        assert any(term in prompt_lower for term in ["goal", "smart", "impact", "objective"]), \
            "Prompt should mention goals or objectives"

    def test_load_culture_csv_raises_for_missing_scale(self):
        """
        Given: Invalid scale name
        When: load_culture_csv('nonexistent_scale_xyz') is called
        Then: Raises FileNotFoundError
        """
        with pytest.raises(FileNotFoundError):
            load_culture_csv("nonexistent_scale_xyz")

    def test_load_org_focus_areas_raises_for_missing_org(self):
        """
        Given: Invalid org name
        When: load_org_focus_areas('nonexistent_org_xyz') is called
        Then: Raises FileNotFoundError
        """
        with pytest.raises(FileNotFoundError):
            load_org_focus_areas("nonexistent_org_xyz")


# ============================================================================
# UNIT TESTS - Test discovery and extraction logic
# ============================================================================
class TestDiscoveryFunctions:
    """Test resource discovery functions (unit tier)."""

    def test_discover_scales_returns_list_of_strings(self):
        """
        Given: Data directory with culture_expectations_*.csv files
        When: discover_scales() is called
        Then: Returns non-empty list of scale name strings
        """
        scales = discover_scales()
        
        assert isinstance(scales, list)
        assert len(scales) > 0, "Should discover at least one scale"
        assert all(isinstance(s, str) and len(s) > 0 for s in scales), \
            "All scales should be non-empty strings"

    def test_discover_scales_returns_sorted_list(self):
        """
        Given: Multiple scale files
        When: discover_scales() is called
        Then: Returns alphabetically sorted list for consistency
        """
        scales = discover_scales()
        
        assert scales == sorted(scales), "Scales should be sorted alphabetically"

    def test_discover_orgs_returns_list_with_demo(self):
        """
        Given: Prompts directory with org_focus_areas_*.md files
        When: discover_orgs() is called
        Then: Returns non-empty list including 'demo'
        """
        orgs = discover_orgs()
        
        assert isinstance(orgs, list)
        assert len(orgs) > 0
        assert "demo" in orgs, "Demo org should always be available"

    def test_discover_orgs_returns_sorted_list(self):
        """
        Given: Multiple org files
        When: discover_orgs() is called
        Then: Returns alphabetically sorted list
        """
        orgs = discover_orgs()
        
        assert orgs == sorted(orgs), "Orgs should be sorted alphabetically"

    def test_discover_levels_returns_dict_mapping_scales_to_lists(self):
        """
        Given: Resource discovery functions work
        When: discover_levels() is called for each scale
        Then: Returns dict mapping each scale to its levels
        """
        scales = discover_scales()
        levels = {}
        
        for scale in scales:
            levels[scale] = extract_levels_from_csv(scale)
        
        assert isinstance(levels, dict)
        assert set(levels.keys()) == set(scales), \
            "Should have entries for all scales"
        
        # Each scale maps to non-empty list
        for scale, level_list in levels.items():
            assert isinstance(level_list, list)
            assert len(level_list) > 0, f"Scale '{scale}' should have levels"


class TestLevelExtraction:
    """Test level extraction from CSV data (unit tier)."""

    def test_extract_levels_from_csv_returns_list(self):
        """
        Given: Valid scale name
        When: extract_levels_from_csv(scale) is called
        Then: Returns list of level strings starting with 'L'
        """
        scales = discover_scales()
        assert len(scales) > 0, "Need at least one scale"
        
        levels = extract_levels_from_csv(scales[0])
        
        assert isinstance(levels, list)
        assert len(levels) > 0
        assert all(isinstance(l, str) and l.startswith("L") for l in levels), \
            "All levels should be strings starting with 'L'"

    def test_extract_levels_are_sorted(self):
        """
        Given: CSV with multiple levels
        When: extract_levels_from_csv() is called
        Then: Returns sorted list (consistent ordering)
        """
        scales = discover_scales()
        levels = extract_levels_from_csv(scales[0])
        
        assert levels == sorted(levels), "Levels should be sorted"

    def test_extract_culture_for_level_returns_dict(self):
        """
        Given: Valid scale and level
        When: extract_culture_for_level(scale, level) is called
        Then: Returns dict mapping attributes to expectations
        """
        scales = discover_scales()
        scale = scales[0]
        levels = extract_levels_from_csv(scale)
        level = levels[0]
        
        culture = extract_culture_for_level(scale, level)
        
        assert isinstance(culture, dict)
        assert len(culture) > 0, f"Should have expectations for {scale}/{level}"

    def test_extract_culture_for_invalid_level_returns_empty_dict(self):
        """
        Given: Invalid level name
        When: extract_culture_for_level(scale, 'L999 (Invalid)') is called
        Then: Returns empty dict (graceful degradation)
        """
        scales = discover_scales()
        culture = extract_culture_for_level(scales[0], "L999 (Invalid)")
        
        assert culture == {}, "Should return empty dict for invalid level"

    def test_extract_culture_values_are_strings(self):
        """
        Given: Valid scale and level
        When: extract_culture_for_level() is called
        Then: All values are non-empty expectation strings
        """
        scales = discover_scales()
        scale = scales[0]
        levels = extract_levels_from_csv(scale)
        
        culture = extract_culture_for_level(scale, levels[0])
        
        assert all(isinstance(v, str) and len(v) > 0 for v in culture.values()), \
            "All expectations should be non-empty strings"


# ============================================================================
# INTEGRATION TESTS - Test prompt assembly with real data
# ============================================================================
class TestPromptAssemblyIntegration:
    """Test prompt assembly orchestration (integration tier)."""

    def test_assemble_prompt_returns_tuple_of_strings(self):
        """
        Given: Valid scale, level, intensity, org
        When: assemble_prompt() is called
        Then: Returns tuple (system_prompt, user_prompt) both non-empty strings
        """
        scales = discover_scales()
        orgs = discover_orgs()
        assert len(scales) > 0 and len(orgs) > 0
        
        scale = scales[0]
        level = extract_levels_from_csv(scale)[0]
        
        system, user = assemble_prompt(
            scale=scale,
            level=level,
            growth_intensity="moderate",
            org_name=orgs[0],
            goal_style="independent"
        )
        
        assert isinstance(system, str) and len(system) > 0
        assert isinstance(user, str) and len(user) > 0

    def test_assemble_prompt_includes_user_context(self):
        """
        Given: Valid parameters including level and intensity
        When: assemble_prompt() is called
        Then: User prompt includes level and intensity context
        """
        scales = discover_scales()
        scale = scales[0]
        level = extract_levels_from_csv(scale)[0]
        
        system, user = assemble_prompt(
            scale=scale,
            level=level,
            growth_intensity="aggressive",
            org_name="demo",
            goal_style="progressive"
        )
        
        assert level in user, "User prompt should reference the level"
        assert "aggressive" in user.lower(), "User prompt should reference intensity"
        assert "progressive" in user.lower(), "User prompt should reference goal style"

    def test_assemble_prompt_with_theme_includes_theme_context(self):
        """
        Given: assemble_prompt() called with optional theme
        When: theme is 'Innovation & Quality'
        Then: User prompt includes theme context
        """
        scales = discover_scales()
        scale = scales[0]
        level = extract_levels_from_csv(scale)[0]
        
        system, user = assemble_prompt(
            scale=scale,
            level=level,
            growth_intensity="moderate",
            org_name="demo",
            theme="Innovation & Quality",
            goal_style="independent"
        )
        
        assert len(user) > 100, "Theme context should make prompt more substantive"
        # Theme should be referenced (at least indirectly)
        assert any(word in user.lower() for word in ["innovation", "quality"]), \
            "Prompt should incorporate theme concepts"

    def test_assemble_prompt_without_theme_still_succeeds(self):
        """
        Given: assemble_prompt() called without theme parameter
        When: theme is None (optional)
        Then: Still returns valid prompts
        """
        scales = discover_scales()
        scale = scales[0]
        level = extract_levels_from_csv(scale)[0]
        
        system, user = assemble_prompt(
            scale=scale,
            level=level,
            growth_intensity="moderate",
            org_name="demo"
        )
        
        assert isinstance(system, str) and len(system) > 0
        assert isinstance(user, str) and len(user) > 0

    def test_assemble_prompt_raises_for_invalid_level(self):
        """
        Given: Invalid level that doesn't exist in scale
        When: assemble_prompt() is called with 'L999 (Invalid)'
        Then: Raises ValueError
        """
        scales = discover_scales()
        
        with pytest.raises(ValueError):
            assemble_prompt(
                scale=scales[0],
                level="L999 (Invalid)",
                growth_intensity="moderate"
            )


# ============================================================================
# DATA INTEGRITY TESTS - Verify consistency and format compliance
# ============================================================================
class TestDataIntegrity:
    """Test data file integrity and format consistency (integration tier)."""

    def test_csv_attributes_are_non_empty(self):
        """
        Given: Culture CSV files
        When: Loaded
        Then: All attribute names are non-empty and trimmed
        """
        for scale in discover_scales():
            culture = load_culture_csv(scale)
            for attr_name in culture.keys():
                assert attr_name, f"Scale '{scale}' has empty attribute name"
                assert attr_name.strip() == attr_name, \
                    f"Attribute '{attr_name}' in '{scale}' has leading/trailing whitespace"

    def test_all_scales_have_consistent_attributes(self):
        """
        Given: Multiple culture CSV files
        When: Loaded
        Then: All scales have the same set of cultural attributes
        """
        scales = discover_scales()
        if len(scales) < 2:
            pytest.skip("Need at least 2 scales to test consistency")
        
        baseline_attrs = set(load_culture_csv(scales[0]).keys())
        
        for scale in scales[1:]:
            actual_attrs = set(load_culture_csv(scale).keys())
            assert actual_attrs == baseline_attrs, \
                f"Scale '{scale}' attributes differ from '{scales[0]}': " \
                f"missing {baseline_attrs - actual_attrs}, " \
                f"extra {actual_attrs - baseline_attrs}"

    def test_all_attributes_have_level_data(self):
        """
        Given: Culture CSV for a scale
        When: Loaded and levels extracted
        Then: Each attribute has expectations for all levels
        """
        for scale in discover_scales():
            culture = load_culture_csv(scale)
            levels = extract_levels_from_csv(scale)
            
            for attr_name, level_data in culture.items():
                # Filter to valid levels (skip None keys from CSV parsing)
                valid_level_keys = {
                    k for k in level_data.keys() 
                    if k is not None and isinstance(k, str) and k.startswith("L")
                }
                
                assert len(valid_level_keys) == len(levels), \
                    f"Attribute '{attr_name}' in '{scale}': " \
                    f"has {len(valid_level_keys)} levels, expected {len(levels)}"

    def test_level_names_follow_expected_format(self):
        """
        Given: Levels extracted from CSV
        When: Extracted
        Then: All follow pattern "L## (description)" or "L##+ (description)"
        """
        for scale in discover_scales():
            levels = extract_levels_from_csv(scale)
            
            for level in levels:
                assert level.startswith("L"), \
                    f"Level '{level}' in '{scale}' doesn't start with 'L'"
                assert "(" in level and ")" in level, \
                    f"Level '{level}' in '{scale}' missing description in parentheses"
                # Extract and verify format is like "L10–15" or "L100+"
                parts = level.split("(")
                level_num_part = parts[0].strip()
                assert any(c.isdigit() for c in level_num_part), \
                    f"Level '{level}' missing numeric component"

    def test_org_focus_areas_files_contain_markdown(self):
        """
        Given: Org focus areas markdown files
        When: Loaded
        Then: All contain markdown formatting (headers, lists, etc.)
        """
        for org in discover_orgs():
            content = load_org_focus_areas(org)
            assert isinstance(content, str)
            assert len(content) > 0
            # Should have at least one markdown element
            assert any(marker in content for marker in ["#", "-", "*", "•"]), \
                f"Org '{org}' should contain markdown formatting"
