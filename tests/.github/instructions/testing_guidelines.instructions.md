---
alwaysApply: true
trigger: always_on
applyTo: "tests/**/*.py"
---

# Testing Standards

## Markers (Required - Exactly One Per Test)
- `@pytest.mark.unit` - Isolated logic, mocks/fixtures, <10ms
- `@pytest.mark.integration` - Component interaction, controlled test data, <100ms
- `@pytest.mark.smoke` - End-to-end validation with real demo data, <1s
- `@pytest.mark.slow` - Long-running operations, combine with others

## Martin Fowler Test Shapes
1. **Expressive** - Test name + assertions clearly state behavior
2. **Bounded** - Single layer (unit/integration/smoke), isolation via mocks
3. **Fast** - Use mocks/tmp_path, avoid I/O
4. **Reliable** - Fail only for real changes, not data mutations

## Naming Conventions
- Classes: `Test{Component}{Type}` e.g., `TestCLIGenerateCommand`, `TestPromptAssemblyIntegration`
- Methods: Descriptive present tense e.g., `test_assemble_prompt_includes_org_focus_when_provided`


## Anti-Patterns
- ❌ No marker or multiple markers
- ❌ Tests coupled to specific demo data content
- ❌ Real I/O in unit tests
- ❌ Multiple concerns per test
- ❌ Testing implementation details instead of behavior

## Fixtures (In conftest.py)
- `tmp_path` - Isolated filesystem
- `minimal_culture_data` - Valid minimal test data dict
- `test_workspace` - Full test environment with temp files


## References
- [Martin Fowler Test Shapes](https://martinfowler.com/articles/2021-test-shapes.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/how-to/mark.html)