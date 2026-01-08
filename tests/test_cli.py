"""Tests for myimpact.cli module.

Following Martin Fowler's Test Shapes principles:
- Expressive: Tests clearly state behavior and output contracts
- Bounded: Tests focus on CLI command logic, mocking assembler
- Fast: Mocks heavy computation (assembler calls)
- Reliable: Only fail for real CLI contract changes
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from myimpact.cli import main, discover_org_names, discover_scales
from myimpact.assembler import extract_levels_from_csv


# ============================================================================
# UNIT TESTS - Test CLI commands with mocked assembler
# ============================================================================
class TestCLIGenerateCommand:
    """Test 'generate' command with mocked assembler (unit tier)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('myimpact.cli.assemble_prompt')
    def test_generate_accepts_required_arguments(self, mock_assemble):
        """
        Given: generate command with scale, level, intensity
        When: Invoked with valid arguments
        Then: Succeeds and calls assembler with correct parameters
        """
        mock_assemble.return_value = ("system prompt", "user prompt")
        
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "moderate"
        ])
        
        assert result.exit_code == 0
        assert mock_assemble.called

    @patch('myimpact.cli.assemble_prompt')
    def test_generate_command_outputs_system_and_user_prompts(self, mock_assemble):
        """
        Given: Valid generate arguments
        When: Command executes
        Then: Output includes both SYSTEM PROMPT and USER CONTEXT sections
        """
        mock_assemble.return_value = ("system content", "user content")
        
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "moderate"
        ])
        
        assert result.exit_code == 0
        assert "SYSTEM PROMPT" in result.output
        assert "USER CONTEXT" in result.output
        assert "system content" in result.output
        assert "user content" in result.output

    @patch('myimpact.cli.assemble_prompt')
    def test_generate_passes_all_parameters_to_assembler(self, mock_assemble):
        """
        Given: generate command with all optional parameters
        When: Invoked
        Then: Assembler receives exact parameter values
        """
        mock_assemble.return_value = ("sys", "user")
        
        self.runner.invoke(main, [
            "generate",
            "technical",
            "L50",
            "aggressive",
            "--org", "acme",
            "--theme", "Quality First",
            "--goal-style", "progressive"
        ])
        
        # Verify exact call signature
        mock_assemble.assert_called_once_with(
            scale="technical",
            level="L50",
            growth_intensity="aggressive",
            org_name="acme",
            theme="Quality First",
            goal_style="progressive"
        )

    def test_generate_rejects_invalid_intensity(self):
        """
        Given: generate command with invalid growth_intensity
        When: Invoked with 'invalid_xyz'
        Then: Returns non-zero exit code and shows error
        """
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "invalid_xyz"
        ])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid" in result.output.lower()

    def test_generate_rejects_invalid_goal_style(self):
        """
        Given: generate command with invalid goal_style
        When: Invoked with '--goal-style invalid_xyz'
        Then: Returns non-zero exit code with error
        """
        result = self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "moderate",
            "--goal-style", "invalid_xyz"
        ])
        
        assert result.exit_code != 0

    def test_generate_requires_scale_argument(self):
        """
        Given: generate command without scale
        When: Invoked with missing argument
        Then: Returns non-zero exit code
        """
        result = self.runner.invoke(main, ["generate"])
        
        assert result.exit_code != 0

    def test_generate_requires_level_argument(self):
        """
        Given: generate command without level
        When: Invoked with missing argument
        Then: Returns non-zero exit code
        """
        result = self.runner.invoke(main, ["generate", "technical"])
        
        assert result.exit_code != 0

    def test_generate_requires_intensity_argument(self):
        """
        Given: generate command without growth_intensity
        When: Invoked with missing argument
        Then: Returns non-zero exit code
        """
        result = self.runner.invoke(main, ["generate", "technical", "L30"])
        
        assert result.exit_code != 0

    @patch('myimpact.cli.assemble_prompt')
    def test_generate_uses_demo_as_default_org(self, mock_assemble):
        """
        Given: generate command without --org flag
        When: Invoked
        Then: Assembler receives org_name='demo'
        """
        mock_assemble.return_value = ("sys", "user")
        
        self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "moderate"
        ])
        
        call_kwargs = mock_assemble.call_args[1]
        assert call_kwargs["org_name"] == "demo"

    @patch('myimpact.cli.assemble_prompt')
    def test_generate_uses_independent_as_default_goal_style(self, mock_assemble):
        """
        Given: generate command without --goal-style flag
        When: Invoked
        Then: Assembler receives goal_style='independent'
        """
        mock_assemble.return_value = ("sys", "user")
        
        self.runner.invoke(main, [
            "generate",
            "technical",
            "L30",
            "moderate"
        ])
        
        call_kwargs = mock_assemble.call_args[1]
        assert call_kwargs["goal_style"] == "independent"


class TestCLIListOptionsCommand:
    """Test 'list-options' command (unit tier)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_list_options_returns_success(self):
        """
        Given: list-options command
        When: Invoked
        Then: Returns exit code 0
        """
        result = self.runner.invoke(main, ["list-options"])
        assert result.exit_code == 0

    def test_list_options_displays_scales_section(self):
        """
        Given: list-options command
        When: Invoked
        Then: Output includes JOB LEVEL SCALES section
        """
        result = self.runner.invoke(main, ["list-options"])
        
        assert "JOB LEVEL SCALES" in result.output or "SCALES" in result.output
        assert len(result.output) > 100, "Should display options"

    def test_list_options_displays_intensities_section(self):
        """
        Given: list-options command
        When: Invoked
        Then: Output includes GROWTH INTENSITIES with all options
        """
        result = self.runner.invoke(main, ["list-options"])
        
        assert "GROWTH INTENSITIES" in result.output or "INTENSITIES" in result.output
        assert "minimal" in result.output.lower()
        assert "moderate" in result.output.lower()
        assert "aggressive" in result.output.lower()

    def test_list_options_displays_goal_styles_section(self):
        """
        Given: list-options command
        When: Invoked
        Then: Output includes GOAL STYLES with options
        """
        result = self.runner.invoke(main, ["list-options"])
        
        assert "independent" in result.output.lower()
        assert "progressive" in result.output.lower()


# ============================================================================
# INTEGRATION TESTS - Test CLI with real data
# ============================================================================
class TestCLIGenerateIntegration:
    """Test 'generate' command with real assembler (integration tier)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.scales = discover_scales()
        self.orgs = discover_org_names()

    def test_generate_with_real_data_succeeds(self):
        """
        Given: Valid scale and level from discovery
        When: generate command invoked
        Then: Succeeds and produces output
        """
        if not self.scales:
            pytest.skip("No scales discovered")
        
        scale = self.scales[0]
        levels = extract_levels_from_csv(scale)
        if not levels:
            pytest.skip(f"Scale '{scale}' has no levels")
        
        result = self.runner.invoke(main, [
            "generate",
            scale,
            levels[0],
            "moderate"
        ])
        
        assert result.exit_code == 0

    def test_generate_output_includes_prompts(self):
        """
        Given: Valid generate arguments with real data
        When: Command executes
        Then: Output includes both SYSTEM PROMPT and USER CONTEXT
        """
        if not self.scales:
            pytest.skip("No scales discovered")
        
        scale = self.scales[0]
        levels = extract_levels_from_csv(scale)
        if not levels:
            pytest.skip(f"Scale '{scale}' has no levels")
        
        result = self.runner.invoke(main, [
            "generate",
            scale,
            levels[0],
            "moderate"
        ])
        
        assert "SYSTEM PROMPT" in result.output
        assert "USER CONTEXT" in result.output

    def test_generate_output_references_level_and_intensity(self):
        """
        Given: generate command with specific level and intensity
        When: Executed
        Then: Output references both
        """
        if not self.scales:
            pytest.skip("No scales discovered")
        
        scale = self.scales[0]
        levels = extract_levels_from_csv(scale)
        if len(levels) < 1:
            pytest.skip(f"Scale '{scale}' has no levels")
        
        level = levels[0]
        result = self.runner.invoke(main, [
            "generate",
            scale,
            level,
            "aggressive"
        ])
        
        assert level in result.output
        assert "aggressive" in result.output.lower()

    def test_generate_output_well_formatted(self):
        """
        Given: generate command output
        When: Produced
        Then: Contains clear section separators
        """
        if not self.scales:
            pytest.skip("No scales discovered")
        
        scale = self.scales[0]
        levels = extract_levels_from_csv(scale)
        if not levels:
            pytest.skip(f"Scale '{scale}' has no levels")
        
        result = self.runner.invoke(main, [
            "generate",
            scale,
            levels[0],
            "moderate"
        ])
        
        # Should have visual separators
        assert "====" in result.output or "----" in result.output


# ============================================================================
# DISCOVERY FUNCTION TESTS
# ============================================================================
class TestCLIDiscoveryFunctions:
    """Test CLI discovery helper functions (unit tier)."""

    def test_discover_org_names_returns_list(self):
        """
        Given: discover_org_names() function
        When: Called
        Then: Returns list of org name strings
        """
        orgs = discover_org_names()
        
        assert isinstance(orgs, list)
        assert all(isinstance(o, str) for o in orgs)

    def test_discover_org_names_includes_demo(self):
        """
        Given: discover_org_names() function
        When: Called
        Then: Returns list including 'demo'
        """
        orgs = discover_org_names()
        
        assert "demo" in orgs, "Demo org should always be discoverable"

    def test_discover_org_names_sorted(self):
        """
        Given: discover_org_names() with multiple orgs
        When: Called
        Then: Returns sorted list
        """
        orgs = discover_org_names()
        
        assert orgs == sorted(orgs), "Org names should be sorted"

    def test_discover_scales_returns_list(self):
        """
        Given: discover_scales() function
        When: Called
        Then: Returns list of scale name strings
        """
        scales = discover_scales()
        
        assert isinstance(scales, list)
        assert len(scales) > 0
        assert all(isinstance(s, str) for s in scales)

    def test_discover_scales_sorted(self):
        """
        Given: discover_scales() with multiple scales
        When: Called
        Then: Returns sorted list
        """
        scales = discover_scales()
        
        assert scales == sorted(scales), "Scale names should be sorted"


# ============================================================================
# CLI HELP AND DOCUMENTATION TESTS
# ============================================================================
class TestCLIHelp:
    """Test CLI help output and documentation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_help_displays_successfully(self):
        """
        Given: Main CLI help
        When: --help flag used
        Then: Returns exit code 0 with help text
        """
        result = self.runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "MyImpact" in result.output or "goal" in result.output.lower()

    def test_main_help_lists_commands(self):
        """
        Given: Main CLI help
        When: --help flag used
        Then: Lists available commands (generate, list-options)
        """
        result = self.runner.invoke(main, ["--help"])
        
        assert "generate" in result.output.lower()
        assert "list-options" in result.output.lower() or "list" in result.output.lower()

    def test_generate_help_displays_successfully(self):
        """
        Given: generate command help
        When: --help flag used
        Then: Returns exit code 0 with usage info
        """
        result = self.runner.invoke(main, ["generate", "--help"])
        
        assert result.exit_code == 0
        assert "SCALE" in result.output or "scale" in result.output.lower()
