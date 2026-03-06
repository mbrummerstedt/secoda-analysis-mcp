"""Unit tests for tools.ai_chat functions."""

import json
from unittest.mock import patch

import pytest
import responses as responses_lib

from secoda_analysis.tools.ai_chat import _poll_for_completion, _submit_prompt, ai_chat

SUBMIT_URL = "https://app.secoda.co/ai/embedded_prompt/"
POLL_URL = "https://app.secoda.co/ai/embedded_prompt/chat-abc123/"


class TestSubmitPrompt:
    @responses_lib.activate
    def test_successful_submit_returns_dict_with_id(self, ai_chat_submit_response):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        result = _submit_prompt(prompt="What is GMV?")
        assert result["id"] == "chat-abc123"

    @responses_lib.activate
    def test_persona_id_included_when_set(self, ai_chat_submit_response):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        _submit_prompt(prompt="Hello", persona_id="persona-xyz")
        body = json.loads(responses_lib.calls[0].request.body)
        assert body["persona_id"] == "persona-xyz"

    @responses_lib.activate
    def test_persona_id_omitted_when_none(self, ai_chat_submit_response):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        _submit_prompt(prompt="Hello", persona_id=None)
        body = json.loads(responses_lib.calls[0].request.body)
        assert "persona_id" not in body

    @responses_lib.activate
    def test_parent_included_when_set(self, ai_chat_submit_response):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        _submit_prompt(prompt="Follow up", parent="prev-chat-id")
        body = json.loads(responses_lib.calls[0].request.body)
        assert body["parent"] == "prev-chat-id"

    @responses_lib.activate
    def test_403_raises_runtime_error(self):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, status=403)
        with pytest.raises(RuntimeError, match="Permission denied"):
            _submit_prompt(prompt="Hello")

    @responses_lib.activate
    def test_no_id_in_response_raises_runtime_error(self):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json={"status": "pending"}, status=200)
        with pytest.raises(RuntimeError, match="No chat ID"):
            _submit_prompt(prompt="Hello")

    @responses_lib.activate
    @patch("secoda_analysis.tools.ai_chat.time.sleep")
    def test_rate_limit_exhausted_raises_runtime_error(self, mock_sleep):
        for _ in range(3):
            responses_lib.add(responses_lib.POST, SUBMIT_URL, status=429)
        with pytest.raises(RuntimeError, match="Rate limit"):
            _submit_prompt(prompt="Hello")


class TestPollForCompletion:
    @responses_lib.activate
    def test_returns_completed_response(self, ai_chat_completed_response):
        responses_lib.add(responses_lib.GET, POLL_URL, json=ai_chat_completed_response, status=200)
        result = _poll_for_completion("chat-abc123", poll_interval=0.01, timeout=5.0)
        assert result["status"] == "completed"

    @responses_lib.activate
    def test_polls_until_completed(self, ai_chat_completed_response):
        responses_lib.add(
            responses_lib.GET, POLL_URL, json={"id": "chat-abc123", "status": "pending"}, status=200
        )
        responses_lib.add(responses_lib.GET, POLL_URL, json=ai_chat_completed_response, status=200)
        result = _poll_for_completion("chat-abc123", poll_interval=0.01, timeout=5.0)
        assert result["status"] == "completed"
        assert len(responses_lib.calls) == 2

    @responses_lib.activate
    def test_failed_status_raises_runtime_error(self):
        responses_lib.add(
            responses_lib.GET, POLL_URL, json={"id": "chat-abc123", "status": "failed"}, status=200
        )
        with pytest.raises(RuntimeError, match="failed"):
            _poll_for_completion("chat-abc123", poll_interval=0.01, timeout=5.0)

    @responses_lib.activate
    def test_404_raises_runtime_error(self):
        responses_lib.add(responses_lib.GET, POLL_URL, status=404)
        with pytest.raises(RuntimeError, match="not found"):
            _poll_for_completion("chat-abc123", poll_interval=0.01, timeout=5.0)

    @responses_lib.activate
    def test_timeout_raises_runtime_error(self):
        responses_lib.add(
            responses_lib.GET,
            POLL_URL,
            json={"id": "chat-abc123", "status": "pending"},
            status=200,
        )
        with pytest.raises(RuntimeError, match="timed out"):
            _poll_for_completion("chat-abc123", poll_interval=0.01, timeout=0.05)


class TestAiChat:
    @responses_lib.activate
    def test_successful_chat_returns_json(
        self, ai_chat_submit_response, ai_chat_completed_response
    ):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        responses_lib.add(responses_lib.GET, POLL_URL, json=ai_chat_completed_response, status=200)
        result = ai_chat(prompt="What is GMV?", poll_interval_seconds=0.01, timeout_seconds=5.0)
        data = json.loads(result)
        assert data["success"] is True
        assert data["chat_id"] == "chat-abc123"
        assert data["status"] == "completed"
        assert "GMV" in data["response_content"]

    @responses_lib.activate
    def test_submit_error_returns_error_json(self):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, status=403)
        result = ai_chat(prompt="Hello", poll_interval_seconds=0.01, timeout_seconds=5.0)
        data = json.loads(result)
        assert "error" in data

    @responses_lib.activate
    def test_poll_error_returns_error_json_with_chat_id(self, ai_chat_submit_response):
        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        responses_lib.add(
            responses_lib.GET,
            POLL_URL,
            json={"id": "chat-abc123", "status": "failed"},
            status=200,
        )
        result = ai_chat(prompt="Hello", poll_interval_seconds=0.01, timeout_seconds=5.0)
        data = json.loads(result)
        assert "error" in data
        assert data["chat_id"] == "chat-abc123"

    @responses_lib.activate
    def test_default_persona_id_from_env(
        self, monkeypatch, ai_chat_submit_response, ai_chat_completed_response
    ):
        monkeypatch.setenv("AI_PERSONA_ID", "env-persona-123")
        # Reimport to pick up new env value
        import importlib

        import secoda_analysis.core.config as cfg
        import secoda_analysis.tools.ai_chat as ai_chat_mod

        importlib.reload(cfg)
        importlib.reload(ai_chat_mod)

        responses_lib.add(responses_lib.POST, SUBMIT_URL, json=ai_chat_submit_response, status=200)
        responses_lib.add(responses_lib.GET, POLL_URL, json=ai_chat_completed_response, status=200)
        ai_chat_mod.ai_chat(prompt="Hello", poll_interval_seconds=0.01, timeout_seconds=5.0)
        body = json.loads(responses_lib.calls[0].request.body)
        assert body.get("persona_id") == "env-persona-123"
