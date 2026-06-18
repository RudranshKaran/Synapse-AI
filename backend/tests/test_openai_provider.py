"""Tests for the OpenAI provider implementation."""

from unittest.mock import MagicMock, patch

import pytest

from app.providers.openai_provider import OpenAIProvider


class TestOpenAIProviderInitialization:
    """Tests for OpenAI provider setup."""

    def test_provider_creates_without_error(self) -> None:
        """Provider can be instantiated without an API key (fails at runtime)."""
        provider = OpenAIProvider()
        assert provider.api_key is not None  # Will be empty string from settings

    def test_provider_requires_api_key(self) -> None:
        """Calling the provider without an API key should raise."""
        provider = OpenAIProvider()
        provider.api_key = ""
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            provider.generate_response("Test?")


class TestOpenAIProviderConfidenceExtraction:
    """Tests for confidence score extraction from responses."""

    def test_extract_confidence_from_end(self) -> None:
        text = "My position is clear.\nConfidence: 85"
        assert OpenAIProvider._extract_confidence(text) == 85.0

    def test_extract_confidence_with_percent(self) -> None:
        text = "Confidence: 92%"
        assert OpenAIProvider._extract_confidence(text) == 92.0

    def test_extract_confidence_lowercase(self) -> None:
        text = "confidence: 78"
        assert OpenAIProvider._extract_confidence(text) == 78.0

    def test_extract_confidence_missing_returns_default(self) -> None:
        text = "No confidence score here."
        assert OpenAIProvider._extract_confidence(text) == 50.0

    def test_extract_confidence_clamps_above_100(self) -> None:
        text = "Confidence: 150"
        assert OpenAIProvider._extract_confidence(text) == 100.0

    def test_extract_confidence_non_numeric_returns_default(self) -> None:
        text = "Confidence: not-a-number"
        assert OpenAIProvider._extract_confidence(text) == 50.0


class TestOpenAIProviderMockedCall:
    """Tests with mocked OpenAI API calls."""

    @patch("openai.OpenAI")
    def test_generate_response_returns_content(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="This is my opinion.\nConfidence: 82"))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider()
        provider.api_key = "test-key"
        result = provider.generate_response("Test question?")

        assert result.content == "This is my opinion.\nConfidence: 82"
        assert result.confidence == 82.0

    @patch("openai.OpenAI")
    def test_critique_response_returns_content(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Strong critique.\nConfidence: 74"))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider()
        provider.api_key = "test-key"
        result = provider.critique_response("Question?", "Some response")
        assert "critique" in result.content.lower()

    @patch("openai.OpenAI")
    def test_revise_position_returns_content(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Revised position.\nConfidence: 88"))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider()
        provider.api_key = "test-key"
        result = provider.revise_position("Q?", "Original", "Critique")
        assert result.content is not None

    @patch("openai.OpenAI")
    def test_uses_configured_model(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="OK"))]
        )

        provider = OpenAIProvider()
        provider.api_key = "test-key"
        provider.model = "gpt-4"
        provider.generate_response("Test?")

        _, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4"

    @patch("openai.OpenAI")
    def test_sends_system_prompt(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="OK"))]
        )

        provider = OpenAIProvider()
        provider.api_key = "test-key"
        provider.generate_response("Test?")

        _, kwargs = mock_client.chat.completions.create.call_args
        messages = kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
