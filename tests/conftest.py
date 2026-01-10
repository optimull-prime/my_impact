import pytest

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests - fast, isolated, use mocks/fixtures")
    config.addinivalue_line("markers", "integration: Integration tests - use real data or controlled temp fixtures")
    config.addinivalue_line("markers", "smoke: Smoke tests - validate shipped demo data works")
    config.addinivalue_line("markers", "slow: Tests that may take longer to run")