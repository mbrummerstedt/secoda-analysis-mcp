"""Shared fixtures for mock (unit) tests."""

import pytest
import responses as responses_lib

MOCK_API_URL = "https://app.secoda.co/api/v1/"
MOCK_EAPI_BASE_URL = "https://app.secoda.co"
MOCK_TOKEN = "mock-token"


@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    """Pin all URL/token module-level variables to mock values.

    config.py reads env vars at import time, so if API_URL is set in the
    environment (e.g. via a .env file) the wrong host ends up in every module
    that did `from ..core.config import API_URL`.  We patch each binding site
    directly so the responses mocks always match.
    """
    targets = [
        ("secoda_analysis_mcp.core.client", "API_URL", MOCK_API_URL),
        ("secoda_analysis_mcp.core.client", "API_TOKEN", MOCK_TOKEN),
        ("secoda_analysis_mcp.tools.ai_chat", "EAPI_BASE_URL", MOCK_EAPI_BASE_URL),
        ("secoda_analysis_mcp.tools.ai_chat", "API_TOKEN", MOCK_TOKEN),
        ("secoda_analysis_mcp.tools.resources", "API_URL", MOCK_API_URL),
        ("secoda_analysis_mcp.tools.resources", "API_TOKEN", MOCK_TOKEN),
        ("secoda_analysis_mcp.tools.questions", "API_URL", MOCK_API_URL),
        ("secoda_analysis_mcp.tools.questions", "API_TOKEN", MOCK_TOKEN),
        ("secoda_analysis_mcp.tools.collections", "API_URL", MOCK_API_URL),
        ("secoda_analysis_mcp.tools.collections", "API_TOKEN", MOCK_TOKEN),
    ]
    for module, attr, value in targets:
        monkeypatch.setattr(f"{module}.{attr}", value)


@pytest.fixture
def mocked_responses():
    """Activate the responses library for the duration of a test."""
    with responses_lib.RequestsMock() as rsps:
        yield rsps


# ---------------------------------------------------------------------------
# Pre-built response payloads
# ---------------------------------------------------------------------------


@pytest.fixture
def mcp_tool_response():
    """Standard successful Secoda AI MCP tool response."""
    return {
        "isError": False,
        "content": [{"type": "text", "text": '{"results": [{"id": "abc123", "title": "orders"}]}'}],
    }


@pytest.fixture
def resource_list_response():
    """Standard paginated resource list response."""
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": "res-001",
                "title": "orders",
                "native_type": "table",
                "description": "Order lines table",
            }
        ],
    }


@pytest.fixture
def resource_detail_response():
    """Standard single resource response."""
    return {
        "id": "res-001",
        "title": "orders",
        "native_type": "table",
        "description": "Order lines table with full details here",
    }


@pytest.fixture
def collection_list_response():
    """Standard paginated collection list response."""
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [{"id": "col-001", "title": "Finance", "description": "Finance resources"}],
    }


@pytest.fixture
def question_list_response():
    """Standard paginated question list response."""
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": "q-001",
                "title": "How is GMV calculated?",
                "description": "Gross Merchandise Value",
            }
        ],
    }


@pytest.fixture
def ai_chat_submit_response():
    """Response from POST /ai/embedded_prompt/."""
    return {"id": "chat-abc123", "status": "pending"}


@pytest.fixture
def ai_chat_completed_response():
    """Response from GET /ai/embedded_prompt/{id}/ when completed."""
    return {
        "id": "chat-abc123",
        "status": "completed",
        "response": {"content": "GMV is calculated as total order value before deductions."},
    }
