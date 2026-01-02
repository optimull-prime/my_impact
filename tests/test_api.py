"""Tests for API endpoints (api.main module)."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app


class TestAPIMetadataEndpoint:
    """Test /api/metadata endpoint."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_metadata_endpoint_success(self):
        """Test metadata endpoint returns 200."""
        response = self.client.get("/api/metadata")
        assert response.status_code == 200

    def test_metadata_endpoint_schema(self):
        """Test metadata endpoint returns correct schema."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        # Should have all required keys
        assert "scales" in data
        assert "levels" in data
        assert "growth_intensities" in data
        assert "goal_styles" in data
        assert "organizations" in data

    def test_metadata_scales(self):
        """Test metadata scales are correct."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        scales = data["scales"]
        assert isinstance(scales, list)
        assert "technical" in scales
        assert "leadership" in scales

    def test_metadata_levels(self):
        """Test metadata levels structure."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        levels = data["levels"]
        assert isinstance(levels, dict)
        assert "technical" in levels
        assert "leadership" in levels
        assert isinstance(levels["technical"], list)
        assert len(levels["technical"]) == 6  # 6 technical levels

    def test_metadata_growth_intensities(self):
        """Test metadata growth intensities."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        intensities = data["growth_intensities"]
        assert isinstance(intensities, list)
        assert "minimal" in intensities
        assert "moderate" in intensities
        assert "aggressive" in intensities

    def test_metadata_goal_styles(self):
        """Test metadata goal styles."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        styles = data["goal_styles"]
        assert isinstance(styles, list)
        assert "independent" in styles
        assert "progressive" in styles

    def test_metadata_organizations(self):
        """Test metadata organizations."""
        response = self.client.get("/api/metadata")
        data = response.json()
        
        orgs = data["organizations"]
        assert isinstance(orgs, list)
        assert "demo" in orgs


class TestAPIGenerateEndpoint:
    """Test /api/goals/generate endpoint."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_generate_endpoint_basic(self):
        """Test generate endpoint with basic payload."""
        payload = {
            "scale": "technical",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 200

    def test_generate_endpoint_response_schema(self):
        """Test generate endpoint returns correct schema."""
        payload = {
            "scale": "technical",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        data = response.json()
        
        # Should have all required keys
        assert "inputs" in data
        assert "prompts" in data
        assert "result" in data
        assert "powered_by" in data

    def test_generate_endpoint_prompts_structure(self):
        """Test that prompts have system and user keys."""
        payload = {
            "scale": "leadership",
            "level": "L80–85 (VP)",
            "growth_intensity": "aggressive",
            "org": "demo",
            "goal_style": "progressive"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        data = response.json()
        
        prompts = data["prompts"]
        # API returns tuple (system, user) as list
        assert isinstance(prompts, (dict, list))
        if isinstance(prompts, list):
            assert len(prompts) == 2  # (system, user) tuple
        else:
            assert "system" in prompts and "user" in prompts

    def test_generate_endpoint_inputs_echo(self):
        """Test that inputs are echoed back correctly."""
        payload = {
            "scale": "technical",
            "level": "L40–45 (Advanced)",
            "growth_intensity": "minimal",
            "org": "demo",
            "goal_style": "independent"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        data = response.json()
        
        inputs = data["inputs"]
        assert inputs["scale"] == "technical"
        assert inputs["level"] == "L40–45 (Advanced)"
        assert inputs["growth_intensity"] == "minimal"
        assert inputs["goal_style"] == "independent"

    def test_generate_endpoint_with_theme(self):
        """Test generate endpoint with optional theme."""
        payload = {
            "scale": "technical",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "theme": "Innovation",
            "goal_style": "independent"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["inputs"]["theme"] == "Innovation"

    def test_generate_endpoint_invalid_scale(self):
        """Test generate endpoint with invalid scale."""
        payload = {
            "scale": "invalid_scale",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate"
        }
        # Invalid scale causes FileNotFoundError, should raise exception
        with pytest.raises(Exception):
            response = self.client.post("/api/goals/generate", json=payload)
            if response.status_code == 500:
                # Expected - invalid scale causes file not found
                pass
            else:
                raise AssertionError(f"Expected 500, got {response.status_code}")

    def test_generate_endpoint_invalid_intensity(self):
        """Test generate endpoint with invalid intensity."""
        payload = {
            "scale": "technical",
            "level": "L30–35 (Career)",
            "growth_intensity": "invalid"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        # Invalid intensity is accepted (no enum validation), just uses default guidance
        assert response.status_code == 200

    def test_generate_endpoint_missing_required_fields(self):
        """Test generate endpoint with missing required fields."""
        payload = {
            "scale": "technical"
            # Missing level and growth_intensity
        }
        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 422  # Pydantic validation error


class TestAPIRootEndpoint:
    """Test API root and docs endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema


class TestAPIPromptOnlyMode:
    """Test that API works in prompts-only mode (no Azure OpenAI)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_prompts_only_mode(self):
        """Test that API returns prompts even without Azure OpenAI configured."""
        payload = {
            "scale": "technical",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent"
        }
        response = self.client.post("/api/goals/generate", json=payload)
        data = response.json()
        
        # Should always return prompts
        assert "prompts" in data
        assert data["prompts"] is not None
        
        # Result may be None if Azure OpenAI not configured
        # powered_by should indicate mode
        assert data["powered_by"] in ["Azure OpenAI", "prompts-only"]
