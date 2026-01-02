"""Tests for myimpact.cli module."""

import pytest
from click.testing import CliRunner
from myimpact.cli import main, discover_org_names, discover_scales


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "MyImpact" in result.output
        assert "generate" in result.output
        assert "list-options" in result.output

    def test_list_options_command(self):
        """Test list-options command."""
        result = self.runner.invoke(main, ["list-options"])
        assert result.exit_code == 0
        assert "RADFORD SCALES" in result.output
        assert "TECHNICAL" in result.output
        assert "LEADERSHIP" in result.output
        assert "GROWTH INTENSITIES" in result.output
        assert "minimal" in result.output
        assert "moderate" in result.output
        assert "aggressive" in result.output

    def test_generate_command_basic(self):
        """Test generate command with basic arguments."""
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30–35 (Career)",
            "moderate"
        ])
        assert result.exit_code == 0
        assert "SYSTEM PROMPT" in result.output
        assert "USER CONTEXT" in result.output
        assert "L30–35 (Career)" in result.output
        assert "moderate" in result.output

    def test_generate_command_with_options(self):
        """Test generate command with all options."""
        result = self.runner.invoke(main, [
            "generate",
            "leadership",
            "L80–85 (VP)",
            "aggressive",
            "--org", "demo",
            "--goal-style", "progressive"
        ])
        assert result.exit_code == 0
        assert "L80–85 (VP)" in result.output
        assert "aggressive" in result.output
        assert "progressive" in result.output
        assert "demo" in result.output

    def test_generate_command_invalid_intensity(self):
        """Test generate command with invalid growth intensity."""
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30–35 (Career)",
            "invalid_intensity"
        ])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_generate_command_invalid_goal_style(self):
        """Test generate command with invalid goal style."""
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30–35 (Career)",
            "moderate",
            "--goal-style", "invalid_style"
        ])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_generate_command_missing_args(self):
        """Test generate command with missing required arguments."""
        result = self.runner.invoke(main, ["generate", "technical"])
        assert result.exit_code != 0


class TestCLIDiscoveryFunctions:
    """Test CLI discovery helper functions."""

    def test_discover_org_names(self):
        """Test org name discovery function."""
        orgs = discover_org_names()
        assert isinstance(orgs, list)
        assert "demo" in orgs

    def test_discover_scales(self):
        """Test scales discovery function."""
        scales = discover_scales()
        assert isinstance(scales, list)
        assert "technical" in scales
        assert "leadership" in scales


class TestCLIOutput:
    """Test CLI output formatting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_list_options_formatting(self):
        """Test that list-options output is well-formatted."""
        result = self.runner.invoke(main, ["list-options"])
        lines = result.output.split("\n")
        
        # Should have section headers with separator lines
        separator_count = sum(1 for line in lines if "====" in line)
        assert separator_count >= 4  # At least 4 sections with separators

    def test_generate_output_sections(self):
        """Test that generate output has required sections."""
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30–35 (Career)",
            "moderate"
        ])
        
        # Should have both prompt sections
        assert "SYSTEM PROMPT" in result.output
        assert "USER CONTEXT" in result.output
        
        # Should have proper separators
        assert "====" in result.output

    def test_generate_output_includes_cultural_attributes(self):
        """Test that generated output includes cultural attributes."""
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30–35 (Career)",
            "moderate"
        ])
        
        # Should include at least some cultural attributes
        assert "Humble" in result.output or "humble" in result.output.lower()
        assert "Cultural Expectations" in result.output
