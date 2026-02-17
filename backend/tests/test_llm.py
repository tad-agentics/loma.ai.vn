"""Tests for loma.llm — Claude API integration, retry, timeout."""
from unittest.mock import patch, MagicMock
import os

from loma.llm import call_claude, MAX_RETRIES, RETRY_DELAY_S, REQUEST_TIMEOUT_S


class TestRetryConfig:
    def test_max_retries_is_3(self):
        assert MAX_RETRIES == 3

    def test_request_timeout_is_20(self):
        assert REQUEST_TIMEOUT_S == 20.0

    def test_retry_delay_is_1(self):
        assert RETRY_DELAY_S == 1.0


class TestCallClaudeNoApiKey:
    def test_placeholder_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            result = call_claude("system", "input text")
            assert "[LLM placeholder" in result
            assert "input text" not in result or "chars" in result

    def test_placeholder_mentions_model(self):
        with patch.dict(os.environ, {}, clear=True):
            result = call_claude("system", "input", model="claude-sonnet-4-20250514")
            assert "claude-sonnet-4-20250514" in result


class TestCallClaudeWithApiKey:
    def _make_mock_anthropic_module(self):
        """Create a mock anthropic module with exception types."""
        mock_module = MagicMock()
        mock_module.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_module.APIConnectionError = type("APIConnectionError", (Exception,), {})
        mock_module.RateLimitError = type("RateLimitError", (Exception,), {})
        return mock_module

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_successful_call(self):
        mock_client = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "  Rewritten text  "
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response

        mock_module = self._make_mock_anthropic_module()
        mock_module.Anthropic = MagicMock(return_value=mock_client)

        with patch.dict("sys.modules", {"anthropic": mock_module}):
            result = call_claude("system prompt", "hello")
            assert result == "Rewritten text"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_empty_content_returns_empty(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response

        mock_module = self._make_mock_anthropic_module()
        mock_module.Anthropic = MagicMock(return_value=mock_client)

        with patch.dict("sys.modules", {"anthropic": mock_module}):
            result = call_claude("system", "input")
            assert result == ""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_raises_on_all_retries_exhausted(self):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")

        mock_module = self._make_mock_anthropic_module()
        mock_module.Anthropic = MagicMock(return_value=mock_client)

        with patch.dict("sys.modules", {"anthropic": mock_module}):
            try:
                call_claude("system", "input")
                assert False, "Should have raised"
            except RuntimeError as e:
                assert "LLM call failed" in str(e)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_retries_on_rate_limit(self):
        mock_module = self._make_mock_anthropic_module()
        RateLimitError = mock_module.RateLimitError

        mock_client = MagicMock()
        # First 2 calls rate limited, third succeeds
        mock_content = MagicMock()
        mock_content.text = "success"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_client.messages.create.side_effect = [
            RateLimitError("rate limited"),
            RateLimitError("rate limited"),
            mock_response,
        ]

        mock_module.Anthropic = MagicMock(return_value=mock_client)

        with patch.dict("sys.modules", {"anthropic": mock_module}), \
             patch("loma.llm.time"):
            result = call_claude("system", "input")
            assert result == "success"
            assert mock_client.messages.create.call_count == 3


class TestUserMessageTemplate:
    def test_template_contains_placeholder(self):
        from loma.llm import USER_MESSAGE_TEMPLATE
        assert "{input_text}" in USER_MESSAGE_TEMPLATE

    def test_template_format(self):
        from loma.llm import USER_MESSAGE_TEMPLATE
        formatted = USER_MESSAGE_TEMPLATE.format(input_text="test input")
        assert "test input" in formatted
        assert "Rewrite" in formatted
