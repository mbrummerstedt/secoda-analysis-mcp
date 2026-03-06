"""Configuration for integration tests.

Integration tests hit the real Secoda API and require:
  - API_TOKEN environment variable to be set
  - (Optional) API_URL if using a self-hosted Secoda instance

All tests in this directory are automatically skipped when API_TOKEN is not set.
Run them with:

    pytest tests/integration/ -v

Or with inline credentials:

    API_TOKEN=your-token pytest tests/integration/ -v
"""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all integration tests when API_TOKEN is not set."""
    if not os.getenv("API_TOKEN"):
        skip_marker = pytest.mark.skip(
            reason="API_TOKEN env var not set — skipping integration tests"
        )
        for item in items:
            if "integration" in str(item.fspath):
                item.add_marker(skip_marker)


pytestmark = pytest.mark.integration
