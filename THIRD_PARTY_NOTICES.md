# Third-Party Licenses

This project uses open-source software with the following licenses. All are compatible with Apache-2.0.

## Python Dependencies

### Core

| Package | License | Purpose |
|---------|---------|---------|
| FastAPI | MIT | Web framework for REST API |
| Uvicorn | BSD-3-Clause | ASGI server |
| Pydantic | MIT | Data validation and settings |
| click | BSD-3-Clause | CLI framework |
| python-dotenv | BSD-3-Clause | Environment variables |

### Rate Limiting

| Package | License | Purpose |
|---------|---------|---------|
| slowapi | Apache-2.0 | Rate limiting for FastAPI |

### Testing

| Package | License | Purpose |
|---------|---------|---------|
| pytest | MIT | Testing framework |
| pytest-cov | MIT | Coverage reporting |
| httpx | BSD-3-Clause | HTTP client for tests |

### Code Quality

| Package | License | Purpose |
|---------|---------|---------|
| black | MIT | Code formatter |
| isort | MIT | Import sorting |
| flake8 | MIT | Linting |
| mypy | MIT | Type checking |

## Infrastructure & Deployment

| Service | License | Purpose |
|---------|---------|---------|
| Azure Container Apps | Proprietary (Microsoft) | Hosting backend API |
| Azure Static Web Apps | Proprietary (Microsoft) | Hosting frontend |
| Azure Container Registry | Proprietary (Microsoft) | Docker image storage |
| GitHub Actions | Proprietary (GitHub) | CI/CD automation |

## JavaScript Libraries

| Package | License | Purpose |
|---------|---------|---------|
| (Frontend has minimal dependencies; vanilla JS used where possible) | — | —

## License Compatibility

All open-source dependencies are compatible with Apache-2.0 (code) and CC BY 4.0 (documentation). No GPL or AGPL dependencies are included, so there are no copyleft obligations beyond the Apache-2.0 license itself.

## How to Update This List

When adding new dependencies:

```bash
# Show all dependencies with licenses
pip-licenses --format=markdown

# Or for dev dependencies
pip-licenses --format=markdown --with-system
```

Then update this file accordingly.

## Questions About Licensing?

- Code licensing: See [LICENSE.txt](../LICENSE.txt) (Apache-2.0)
- Documentation licensing: See [docs/LICENSE-DOCS.md](LICENSE-DOCS.md) (CC BY 4.0)
- Attribution: See [NOTICE](../NOTICE)
- Citation: See [CITATION.cff](../CITATION.cff)
