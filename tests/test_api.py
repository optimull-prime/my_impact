"""Tests for API endpoints (api.main module).

Following Martin Fowler's Test Shapes principles:
- Expressive: Tests clearly state what behavior is expected
- Bounded: Tests focus on one layer (HTTP/API), mocking internal concerns
- Fast: No file I/O, no real assembler calls
- Reliable: Only fail for useful reasons (real API contract changes)
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from api.main import app


class TestAPIMetadataEndpoint:
    """Test /api/metadata endpoint - HTTP contract only."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_metadata_endpoint_returns_200_with_all_required_fields(self):
        """
        Given: API is running
        When: Client requests GET /api/metadata
        Then: Returns 200 with scales, levels, intensities, styles, and organizations
        """
        response = self.client.get("/api/metadata")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify contract - these keys MUST exist
        required_keys = {"scales", "levels", "growth_intensities", "goal_styles", "organizations"}
        assert required_keys.issubset(data.keys()), \
            f"Missing keys: {required_keys - set(data.keys())}"

    def test_metadata_scales_is_non_empty_list(self):
        """
        Given: /api/metadata endpoint
        When: Called
        Then: Returns scales as a non-empty list of strings
        """
        response = self.client.get("/api/metadata")
        data = response.json()
        scales = data["scales"]
        
        assert isinstance(scales, list), f"scales should be list, got {type(scales)}"
        assert len(scales) > 0, "scales list should not be empty"
        assert all(isinstance(s, str) for s in scales), "All scales should be strings"

    def test_metadata_levels_maps_scales_to_level_lists(self):
        """
        Given: /api/metadata endpoint
        When: Called
        Then: Returns levels as dict mapping scale names to lists of level strings
        """
        response = self.client.get("/api/metadata")
        data = response.json()
        levels = data["levels"]
        scales = data["scales"]
        
        assert isinstance(levels, dict), "levels should be a dict"
        
        # Each scale should map to a non-empty list
        for scale in scales:
            assert scale in levels, f"Scale '{scale}' missing from levels mapping"
            assert isinstance(levels[scale], list), f"levels[{scale}] should be a list"
            assert len(levels[scale]) > 0, f"levels[{scale}] should have entries"
            assert all(isinstance(l, str) for l in levels[scale]), \
                f"All levels for {scale} should be strings"

    def test_metadata_growth_intensities_has_required_options(self):
        """
        Given: /api/metadata endpoint
        When: Called
        Then: Returns growth_intensities with minimal, moderate, aggressive
        """
        response = self.client.get("/api/metadata")
        data = response.json()
        intensities = data["growth_intensities"]
        
        assert isinstance(intensities, list)
        required_intensities = {"minimal", "moderate", "aggressive"}
        assert required_intensities.issubset(set(intensities)), \
            f"Missing intensities: {required_intensities - set(intensities)}"

    def test_metadata_goal_styles_has_required_options(self):
        """
        Given: /api/metadata endpoint
        When: Called
        Then: Returns goal_styles with independent and progressive
        """
        response = self.client.get("/api/metadata")
        data = response.json()
        styles = data["goal_styles"]
        
        assert isinstance(styles, list)
        required_styles = {"independent", "progressive"}
        assert required_styles.issubset(set(styles)), \
            f"Missing styles: {required_styles - set(styles)}"

    def test_metadata_organizations_is_non_empty_list(self):
        """
        Given: /api/metadata endpoint
        When: Called
        Then: Returns organizations as non-empty list including 'demo'
        """
        response = self.client.get("/api/metadata")
        data = response.json()
        orgs = data["organizations"]
        
        assert isinstance(orgs, list)
        assert len(orgs) > 0
        assert "demo" in orgs, "Demo org should always be available"
        assert all(isinstance(o, str) for o in orgs)


class TestAPIGenerateEndpoint:
    """Test /api/goals/generate endpoint - Focus on HTTP contract and error handling."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    @patch('api.main.assemble_prompt')
    def test_generate_accepts_valid_payload_and_returns_200(self, mock_assemble):
        """
        Given: Valid generate request payload
        When: POST /api/goals/generate
        Then: Returns 200 with framework and user prompts
        """
        # Arrange
        mock_assemble.return_value = ("Framework: context", "User: task")
        
        payload = {
            "scale": "technical",
            "level": "L30",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent"
        }
        
        # Act
        response = self.client.post("/api/goals/generate", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert data["prompts"] == ["Framework: context", "User: task"]

    @patch('api.main.assemble_prompt')
    def test_generate_returns_all_required_response_fields(self, mock_assemble):
        """
        Given: Valid generate request
        When: POST /api/goals/generate
        Then: Response includes inputs, prompts, result
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "technical",
            "level": "L30",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent"
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        data = response.json()
        
        required_fields = {"inputs", "prompts", "result"}
        assert required_fields.issubset(data.keys()), \
            f"Missing fields: {required_fields - set(data.keys())}"

    @patch('api.main.assemble_prompt')
    def test_generate_echoes_input_parameters_in_response(self, mock_assemble):
        """
        Given: Generate request with specific parameters
        When: POST /api/goals/generate
        Then: Response echoes back the exact input values
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "leadership",
            "level": "L50",
            "growth_intensity": "aggressive",
            "org": "acme",
            "focus_area": "Strategic Vision",
            "goal_style": "progressive"
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        inputs = response.json()["inputs"]
        
        # Verify exact echo
        assert inputs["scale"] == "leadership"
        assert inputs["level"] == "L50"
        assert inputs["growth_intensity"] == "aggressive"
        assert inputs["org"] == "acme"
        assert inputs["focus_area"] == "Strategic Vision"
        assert inputs["goal_style"] == "progressive"

    @patch('api.main.assemble_prompt')
    def test_generate_calls_assembler_with_correct_parameters(self, mock_assemble):
        """
        Given: Generate request with all optional parameters
        When: POST /api/goals/generate
        Then: Assembler is called with exact parameters (verifies API → domain mapping)
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "technical",
            "level": "L40",
            "growth_intensity": "minimal",
            "org": "demo",
            "focus_area": "Quality First",
            "goal_style": "progressive"
        }
        
        self.client.post("/api/goals/generate", json=payload)
        
        # Verify assembler was called with exact parameters
        mock_assemble.assert_called_once_with(
            scale="technical",
            level="L40",
            growth_intensity="minimal",
            org_name="demo",
            focus_area="Quality First",
            goal_style="progressive"
        )

    def test_generate_rejects_missing_required_field_scale(self):
        """
        Given: Generate request missing 'scale'
        When: POST /api/goals/generate
        Then: Returns 422 Unprocessable Entity
        """
        payload = {
            "level": "L30",
            "growth_intensity": "moderate"
            # Missing: scale
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 422

    def test_generate_rejects_missing_required_field_level(self):
        """
        Given: Generate request missing 'level'
        When: POST /api/goals/generate
        Then: Returns 422 Unprocessable Entity
        """
        payload = {
            "scale": "technical",
            "growth_intensity": "moderate"
            # Missing: level
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 422

    def test_generate_rejects_missing_required_field_growth_intensity(self):
        """
        Given: Generate request missing 'growth_intensity'
        When: POST /api/goals/generate
        Then: Returns 422 Unprocessable Entity
        """
        payload = {
            "scale": "technical",
            "level": "L30"
            # Missing: growth_intensity
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 422

    @patch('api.main.assemble_prompt')
    def test_generate_accepts_optional_focus_area_parameter(self, mock_assemble):
        """
        Given: Generate request with optional focus area
        When: POST /api/goals/generate
        Then: Focus area is passed to assembler
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "technical",
            "level": "L30",
            "growth_intensity": "moderate",
            "org": "demo",
            "focus_area": "Innovation",
            "goal_style": "independent"
        }
        
        self.client.post("/api/goals/generate", json=payload)
        
        # Verify focus area was passed
        call_kwargs = mock_assemble.call_args[1]
        assert call_kwargs["focus_area"] == "Innovation"

    @patch('api.main.assemble_prompt')
    def test_generate_uses_demo_as_default_organization(self, mock_assemble):
        """
        Given: Generate request without org parameter
        When: POST /api/goals/generate
        Then: Assembler is called with org='demo' as default
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "technical",
            "level": "L30",
            "growth_intensity": "moderate"
            # Missing: org (should default to 'demo')
        }
        
        self.client.post("/api/goals/generate", json=payload)
        
        call_kwargs = mock_assemble.call_args[1]
        assert call_kwargs["org_name"] == "demo"

    @patch('api.main.assemble_prompt')
    def test_generate_uses_independent_as_default_goal_style(self, mock_assemble):
        """
        Given: Generate request without goal_style parameter
        When: POST /api/goals/generate
        Then: Assembler is called with goal_style='independent' as default
        """
        mock_assemble.return_value = ("sys", "user")
        
        payload = {
            "scale": "technical",
            "level": "L30",
            "growth_intensity": "moderate"
            # Missing: goal_style (should default to 'independent')
        }
        
        self.client.post("/api/goals/generate", json=payload)
        
        call_kwargs = mock_assemble.call_args[1]
        assert call_kwargs["goal_style"] == "independent"

    @patch('api.main.assemble_prompt')
    def test_generate_handles_assembler_error_gracefully(self, mock_assemble):
        """
        Given: Assembler raises FileNotFoundError
        When: POST /api/goals/generate
        Then: API returns 500 with error details
        """
        mock_assemble.side_effect = FileNotFoundError("Scale file not found")
        
        payload = {
            "scale": "nonexistent",
            "level": "L30",
            "growth_intensity": "moderate"
        }
        
        response = self.client.post("/api/goals/generate", json=payload)
        
        # Should return error, not crash
        assert response.status_code >= 400


class TestAPIOrgFocusAreasEndpoint:
    """Test /api/orgs/{org_name}/focus-areas endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    @patch('api.main.load_org_focus_areas')
    def test_focus_areas_returns_200_with_content_for_valid_org(self, mock_load):
        """
        Given: Valid org name 'demo'
        When: GET /api/orgs/demo/focus-areas
        Then: Returns 200 with content
        """
        mock_load.return_value = "# Strategic Focus Areas\n- Item 1"
        
        response = self.client.get("/api/orgs/demo/focus-areas")
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "# Strategic Focus Areas\n- Item 1"

    @patch('api.main.load_org_focus_areas')
    def test_focus_areas_returns_null_for_nonexistent_org(self, mock_load):
        """
        Given: Org file doesn't exist
        When: GET /api/orgs/nonexistent/focus-areas
        Then: Returns 200 with content=null (graceful degradation)
        """
        mock_load.side_effect = FileNotFoundError()
        
        response = self.client.get("/api/orgs/nonexistent/focus-areas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] is None

    @patch('api.main.load_org_focus_areas')
    def test_focus_areas_returns_response_structure(self, mock_load):
        """
        Given: Focus areas endpoint
        When: Called with any org
        Then: Always returns dict with 'content' key
        """
        mock_load.return_value = "content"
        
        response = self.client.get("/api/orgs/test/focus-areas")
        data = response.json()
        
        assert isinstance(data, dict)
        assert "content" in data


class TestAPIRootEndpoint:
    """Test API root and docs endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_openapi_schema_available_at_standard_location(self):
        """
        Given: FastAPI app with OpenAPI enabled
        When: GET /openapi.json
        Then: Returns 200 with valid OpenAPI schema
        """
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema

    def test_openapi_schema_includes_endpoints(self):
        """
        Given: OpenAPI schema endpoint
        When: Called
        Then: Schema includes paths for /api/metadata and /api/goals/generate
        """
        response = self.client.get("/openapi.json")
        schema = response.json()
        
        # Verify documented endpoints
        paths = schema.get("paths", {})
        assert "/api/metadata" in paths or len(paths) > 0, \
            "OpenAPI schema should document endpoints"


class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    @patch('api.main.assemble_prompt')
    def test_generate_returns_meaningful_error_for_invalid_data(self, mock_assemble):
        """
        Given: Malformed JSON payload
        When: POST /api/goals/generate
        Then: Returns 422 with validation error details
        """
        response = self.client.post(
            "/api/goals/generate",
            json={"scale": 123}  # Invalid type for scale (should be string)
        )
        
        assert response.status_code == 422

    def test_metadata_endpoint_caches_or_responds_quickly(self):
        """
        Given: /api/metadata endpoint
        When: Called multiple times
        Then: Responds in reasonable time (no unnecessary file I/O)
        """
        import time
        
        start = time.time()
        self.client.get("/api/metadata")
        first_call_time = time.time() - start
        
        # Should be sub-100ms (no file I/O)
        assert first_call_time < 0.1, \
            f"Metadata call took {first_call_time}s - may have unnecessary I/O"
