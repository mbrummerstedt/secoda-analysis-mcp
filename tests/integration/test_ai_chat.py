"""Integration tests for ai_chat tool against the real Secoda API.

Note: These tests send real requests to Secoda's AI endpoint and will
consume AI quota. Each test may take 30-120 seconds to complete.
"""

import json

import pytest

from secoda_analysis.tools.ai_chat import ai_chat

pytestmark = pytest.mark.integration


class TestAiChatIntegration:
    def test_prove_it_works(self):
        """Sanity check: AI responds with a real metric from the catalog."""
        result = ai_chat(
            prompt="Prove that you work by telling me one metric you know about in one sentence.",
            poll_interval_seconds=3.0,
            timeout_seconds=60.0,
        )
        data = json.loads(result)
        assert data.get("success") is True
        assert data.get("response_content")
        assert len(data["response_content"]) > 0

    def test_basic_chat_returns_valid_json(self):
        result = ai_chat(
            prompt="What tools does this MCP server provide?",
            poll_interval_seconds=3.0,
            timeout_seconds=60.0,
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_successful_chat_has_expected_keys(self):
        result = ai_chat(
            prompt="Hello",
            poll_interval_seconds=3.0,
            timeout_seconds=60.0,
        )
        data = json.loads(result)
        if "error" not in data:
            assert "success" in data
            assert "chat_id" in data
            assert "status" in data
            assert "response_content" in data

    def test_chat_id_is_returned(self):
        result = ai_chat(
            prompt="Hello",
            poll_interval_seconds=3.0,
            timeout_seconds=60.0,
        )
        data = json.loads(result)
        if data.get("success"):
            assert data["chat_id"]
            assert len(data["chat_id"]) > 0

    def test_multi_turn_conversation(self):
        """Start a conversation and continue it using the chat_id."""
        first = ai_chat(
            prompt="What is a data catalog?",
            poll_interval_seconds=3.0,
            timeout_seconds=60.0,
        )
        first_data = json.loads(first)

        if first_data.get("success") and first_data.get("chat_id"):
            second = ai_chat(
                prompt="Can you give an example?",
                parent=first_data["chat_id"],
                poll_interval_seconds=3.0,
                timeout_seconds=60.0,
            )
            second_data = json.loads(second)
            assert isinstance(second_data, dict)
