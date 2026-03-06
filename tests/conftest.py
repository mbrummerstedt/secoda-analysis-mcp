"""Root test configuration shared by all test modules."""

import os

import pytest


@pytest.fixture(autouse=True)
def _set_required_env_vars(monkeypatch):
    """Ensure required env vars have values in all tests unless already set."""
    if not os.getenv("API_TOKEN"):
        monkeypatch.setenv("API_TOKEN", "test-token")
    if not os.getenv("API_URL"):
        monkeypatch.setenv("API_URL", "https://app.secoda.co/api/v1/")
