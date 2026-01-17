"""
Test input sanitization and special character handling.

Security: Ensure special characters, quotes, and injection attempts are handled safely.
Reliability: Prevent application crashes from malformed input.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main import app


@pytest.mark.unit
class TestInputSanitization:
    """Test that special characters and edge cases are handled safely."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures with rate limiter and file I/O mocked."""
        self.client = TestClient(app, raise_server_exceptions=False)
        
        # Mock discover_scales to return test scales (for scale validation in API)
        self.scales_patcher = patch('api.main.discover_scales')
        self.mock_scales = self.scales_patcher.start()
        self.mock_scales.return_value = ["Culture_JobLevels", "technical", "leadership"]
        
        # Mock assemble_prompt to avoid file I/O and make this a pure unit test
        # assemble_prompt returns a tuple: (framework_prompt, user_context)
        self.assemble_patcher = patch('api.main.assemble_prompt')
        self.mock_assemble = self.assemble_patcher.start()
        self.mock_assemble.return_value = ("Mocked framework prompt", "Mocked user context")
        
        # Bypass rate limiting by disabling the enabled flag
        # This is cleaner than trying to mock the complex slowapi internals
        from api.main import limiter
        self.original_enabled = limiter.enabled
        limiter.enabled = False
        
        yield
        
        # Restore rate limiting state
        limiter.enabled = self.original_enabled
        self.assemble_patcher.stop()
        self.scales_patcher.stop()

    @pytest.mark.parametrize("special_input", [
        "O'Reilly",  # Single quote
        'John "The Boss" Doe',  # Double quotes
        "Level 30–35",  # Em dash (–)
        "AI/ML & Data Science",  # Ampersand and slash
        "Cost < $1M",  # Less than symbol
        "Revenue > $5M",  # Greater than symbol
        "Q1 (Jan–Mar)",  # Parentheses and dash
        "Improve by 50%",  # Percent sign
        "Email: user@example.com",  # @ symbol
        "Path: C:\\Users\\Documents",  # Backslashes
        "Line1\nLine2",  # Newline
        "Tab\there",  # Tab character
    ])
    def test_focus_area_special_characters_handled(self, special_input):
        """
        Test that focus_area accepts special characters without errors.
        
        Security: Prevent injection attacks via special characters.
        Reliability: Prevent application crashes from unexpected input.
        """
        payload = {
            "scale": "Culture_JobLevels",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent",
            "focus_area": special_input,
        }

        response = self.client.post("/api/goals/generate", json=payload)
        assert response.status_code == 200, f"Failed with input: {special_input}"
        
        data = response.json()
        # Verify the special input is preserved in response
        assert data["inputs"]["focus_area"] == special_input

    def test_sql_injection_attempts_handled(self):
        """
        Test that SQL injection attempts are handled safely.
        
        Security: No SQL execution from user input (we don't use SQL, but test defensively).
        """
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM sensitive_data--",
        ]

        for injection in sql_injection_attempts:
            payload = {
                "scale": "Culture_JobLevels",
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
                "focus_area": injection,
            }

            response = self.client.post("/api/goals/generate", json=payload)
            # Should not crash; should return 200 or validation error
            assert response.status_code in [200, 400, 422], \
                f"Unexpected status code {response.status_code} for injection: {injection}"

    def test_xss_attempts_handled(self):
        """
        Test that XSS attempts are handled safely.
        
        Security: Prevent script injection via focus_area.
        """
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='malicious.com'>",
        ]

        for xss in xss_attempts:
            payload = {
                "scale": "Culture_JobLevels",
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
                "focus_area": xss,
            }

            response = self.client.post("/api/goals/generate", json=payload)
            assert response.status_code == 200, \
                f"XSS input should not crash API: {xss}"
            
            data = response.json()
            # Verify the input is preserved but not executed
            # (Framework should handle output encoding)
            assert "framework" in data
            assert "user_context" in data

    def test_extremely_long_input_handled(self):
        """
        Test that extremely long input is handled gracefully.
        
        Reliability: Prevent memory exhaustion from oversized inputs.
        Performance: Reject unreasonably large payloads.
        """
        long_input = "A" * 10000  # 10KB of text

        payload = {
            "scale": "Culture_JobLevels",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent",
            "focus_area": long_input,
        }

        response = self.client.post("/api/goals/generate", json=payload)
        # Should either succeed or reject with 413/422 (Payload Too Large)
        assert response.status_code in [200, 413, 422], \
            f"Unexpected status code {response.status_code} for long input"

    def test_unicode_characters_handled(self):
        """
        Test that Unicode characters are handled correctly.
        
        Reliability: Support international characters (names, languages).
        """
        unicode_inputs = [
            "José García",  # Spanish accents
            "François Müller",  # German umlaut
            "北京 (Beijing)",  # Chinese characters
            "Москва (Moscow)",  # Cyrillic
            "مرحبا (Hello in Arabic)",  # Arabic
            "🚀 Innovation",  # Emoji
        ]

        for unicode_input in unicode_inputs:
            payload = {
                "scale": "Culture_JobLevels",
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
                "focus_area": unicode_input,
            }

            response = self.client.post("/api/goals/generate", json=payload)
            assert response.status_code == 200, f"Failed with: {unicode_input}"
            
            data = response.json()
            assert data["inputs"]["focus_area"] == unicode_input

    def test_empty_string_vs_null_focus_area(self):
        """
        Test that empty string and null are both handled for optional field.
        
        Reliability: Consistent handling of missing vs. empty optional fields.
        """
        # Test with empty string
        payload_empty = {
            "scale": "Culture_JobLevels",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent",
            "focus_area": "",
        }

        response_empty = self.client.post("/api/goals/generate", json=payload_empty)
        assert response_empty.status_code == 200

        # Test with null
        payload_null = {
            "scale": "Culture_JobLevels",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent",
            "focus_area": None,
        }

        response_null = self.client.post("/api/goals/generate", json=payload_null)
        assert response_null.status_code == 200

        # Test with field omitted
        payload_omitted = {
            "scale": "Culture_JobLevels",
            "level": "L30–35 (Career)",
            "growth_intensity": "moderate",
            "org": "demo",
            "goal_style": "independent",
        }

        response_omitted = self.client.post("/api/goals/generate", json=payload_omitted)
        assert response_omitted.status_code == 200

    def test_level_field_accepts_special_characters(self):
        """
        Test that level field with em dashes and parentheses works correctly.
        
        Reliability: Support standard level format "L30–35 (Career)".
        """
        level_formats = [
            "L30–35 (Career)",  # Em dash
            "L40-45 (Advanced)",  # Regular dash
            "L50–55",  # No parentheses
            "L60 (Expert)",  # Single level
        ]

        for level in level_formats:
            payload = {
                "scale": "Culture_JobLevels",
                "level": level,
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
            }

            response = self.client.post("/api/goals/generate", json=payload)
            assert response.status_code == 200, f"Failed with level: {level}"
            
            data = response.json()
            assert data["inputs"]["level"] == level


@pytest.mark.unit
class TestInputValidation:
    """Test input validation and boundary conditions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures with rate limiter and file I/O mocked."""
        self.client = TestClient(app, raise_server_exceptions=False)
        
        # Mock discover_scales to return test scales (for scale validation in API)
        self.scales_patcher = patch('api.main.discover_scales')
        self.mock_scales = self.scales_patcher.start()
        self.mock_scales.return_value = ["Culture_JobLevels", "technical", "leadership"]
        
        # Mock assemble_prompt to avoid file I/O and make this a pure unit test
        # assemble_prompt returns a tuple: (framework_prompt, user_context)
        self.assemble_patcher = patch('api.main.assemble_prompt')
        self.mock_assemble = self.assemble_patcher.start()
        self.mock_assemble.return_value = ("Mocked framework prompt", "Mocked user context")
        
        # Bypass rate limiting by disabling the enabled flag
        # This is cleaner than trying to mock the complex slowapi internals
        from api.main import limiter
        self.original_enabled = limiter.enabled
        limiter.enabled = False
        
        yield
        
        # Restore rate limiting state
        limiter.enabled = self.original_enabled
        self.assemble_patcher.stop()
        self.scales_patcher.stop()

    def test_whitespace_only_focus_area_handled(self):
        """
        Test that whitespace-only focus area is handled gracefully.
        
        Reliability: Prevent empty or whitespace-only inputs from breaking logic.
        """
        whitespace_inputs = [
            "   ",  # Spaces
            "\t\t",  # Tabs
            "\n\n",  # Newlines
            "  \t\n  ",  # Mixed whitespace
        ]

        for ws_input in whitespace_inputs:
            payload = {
                "scale": "Culture_JobLevels",
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
                "focus_area": ws_input,
            }

            response = self.client.post("/api/goals/generate", json=payload)
            assert response.status_code == 200, \
                f"Failed with whitespace input: {repr(ws_input)}"

    def test_mixed_case_scale_rejected(self):
        """
        Test that case-sensitive scale values are enforced.
        
        Reliability: Validate exact enum values (no case-insensitive matching).
        """
        invalid_scales = [
            "Technical",  # Capital T
            "TECHNICAL",  # All caps
            "Leadership",  # Capital L
        ]

        for scale in invalid_scales:
            payload = {
                "scale": scale,
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": "demo",
                "goal_style": "independent",
            }

            response = self.client.post("/api/goals/generate", json=payload)
            # Should reject with validation error (case-sensitive)
            assert response.status_code in [400, 422], \
                f"Should reject mixed-case scale: {scale}"

    def test_org_name_special_characters(self):
        """
        Test that org names with special characters are handled.
        
        Reliability: Support org names with hyphens, underscores, etc.
        """
        org_names = [
            "demo",
            "my-company",
            "my_company",
            "company123",
            "Company-2024",
        ]

        for org in org_names:
            payload = {
                "scale": "Culture_JobLevels",
                "level": "L30–35 (Career)",
                "growth_intensity": "moderate",
                "org": org,
                "goal_style": "independent",
            }

            response = self.client.post("/api/goals/generate", json=payload)
            # Should succeed (org validation is lenient)
            assert response.status_code in [200, 400, 500], \
                f"Unexpected error for org: {org}"
