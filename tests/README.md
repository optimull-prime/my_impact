# Test Setup and Execution Guide

## Install Test Dependencies

```powershell
# Install test dependencies
pip install -e ".[test]"

# Or install all dependencies including dev tools
pip install -e ".[test,dev]"
```

## Running Tests

### Run All Tests
```powershell
pytest
```

### Run by Test Type
```powershell
# Fast unit tests only (recommended for development)
pytest -m unit

# Integration tests (require running services)
pytest -m integration

# All except slow tests
pytest -m "not slow"
```

### Run Specific Test Files
```powershell
# API tests
pytest tests/test_api.py -v

# Input sanitization tests
pytest tests/test_input_sanitization.py -v

# Assembler tests
pytest tests/test_assembler.py -v
```

### Run with Coverage
```powershell
# Generate coverage report
pytest --cov=api --cov=myimpact --cov-report=html

# View coverage report
start htmlcov/index.html  # Windows
```

### Run Specific Tests
```powershell
# Run single test
pytest tests/test_api.py::TestRateLimiting::test_generate_prompts_rate_limit_enforced -v

# Run all tests in a class
pytest tests/test_api.py::TestRateLimiting -v

# Run tests matching pattern
pytest -k "rate_limit" -v
```

## Test Structure

```
tests/
├── test_api.py              # API endpoints, rate limiting, cache headers
├── test_assembler.py        # Core business logic
├── test_cli.py              # CLI interface
└── test_input_sanitization.py  # Security & input validation
```

## Test Markers

| Marker | Description | Run Command |
|--------|-------------|-------------|
| `@pytest.mark.unit` | Fast tests, no external deps | `pytest -m unit` |
| `@pytest.mark.integration` | Requires running services | `pytest -m integration` |
| `@pytest.mark.slow` | Takes >1 second | `pytest -m "not slow"` |

## Pre-Commit Workflow

```powershell
# Before committing code
pytest -m unit  # Fast feedback

# Before pushing to remote
pytest -m "not slow"  # All tests except slow ones

# Before deployment
pytest  # All tests
```

## Troubleshooting

### Rate Limiting Test Failures
Rate limiting tests may fail if:
- Another test session is running simultaneously
- Rate limit state hasn't reset (wait 60 seconds)

To isolate:
```powershell
pytest tests/test_api.py::TestRateLimiting -v --no-cov
```

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pip install -e ".[test]"

- name: Run unit tests
  run: pytest -m unit --cov=api --cov=myimpact

- name: Run integration tests
  run: pytest -m integration
```
