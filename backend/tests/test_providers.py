"""Tests for the provider abstraction layer.

Covers: base provider (retry, error handling), model config,
registry, factory, and all concrete providers (Gemini, Groq,
OpenRouter, OpenAI, Mock).
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.providers.base import (
    BaseModelProvider,
    ModelResponse,
    ProviderError,
)
from app.providers.config import AVAILABLE_MODELS, get_model_config
from app.providers.factory import create_provider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.mocks.model_a import ModelAProvider
from app.providers.mocks.model_b import ModelBProvider
from app.providers.mocks.model_c import ModelCProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.registry import (
    get_provider_class,
    list_providers,
    register_provider,
)


# ═══════════════════════════════════════════════════════════
# ModelResponse
# ═══════════════════════════════════════════════════════════

class TestModelResponse:
    def test_creates_with_content_and_confidence(self) -> None:
        response = ModelResponse(content="Test", confidence=85.0)
        assert response.content == "Test"
        assert response.confidence == 85.0

    def test_default_confidence(self) -> None:
        response = ModelResponse(content="Test")
        assert response.confidence == 50.0


# ═══════════════════════════════════════════════════════════
# Base provider — retry, error handling, confidence extraction
# ═══════════════════════════════════════════════════════════

class TestBaseProvider:
    """Tests for the base provider's retry and helper methods."""

    def test_extract_confidence_present(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "Some text\nConfidence: 85", default=50.0
        ) == 85.0

    def test_extract_confidence_with_percent(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "Analysis complete.\nConfidence: 92%", default=50.0
        ) == 92.0

    def test_extract_confidence_missing(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "No score here", default=50.0
        ) == 50.0

    def test_extract_confidence_clamps_above_100(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "Confidence: 150", default=50.0
        ) == 100.0

    def test_extract_confidence_clamps_below_0(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "Confidence: -10", default=50.0
        ) == 0.0

    def test_extract_confidence_case_insensitive(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "confidence: 77", default=50.0
        ) == 77.0

    def test_extract_confidence_from_last_line_only(self) -> None:
        assert BaseModelProvider.extract_confidence(
            "Confidence: 50\nConfidence: 88", default=50.0
        ) == 88.0

    def test_call_with_retry_succeeds_first_attempt(self) -> None:
        provider = _ConcreteProvider()
        response = MagicMock(spec=requests.Response)
        response.status_code = 200
        fn = MagicMock(return_value=response)
        result = provider.call_with_retry(fn, "arg1", key="val")
        assert result == response
        fn.assert_called_once_with("arg1", timeout=60, key="val")

    def test_call_with_retry_retries_on_500(self) -> None:
        provider = _ConcreteProvider()
        provider.MAX_RETRIES = 3
        provider.RETRY_DELAY = 0.01

        error_resp = MagicMock(spec=requests.Response)
        error_resp.status_code = 500
        error_resp.text = "Server error"
        success_resp = MagicMock(spec=requests.Response)
        success_resp.status_code = 200

        fn = MagicMock(side_effect=[error_resp, error_resp, success_resp])
        result = provider.call_with_retry(fn)
        assert result == success_resp
        assert fn.call_count == 3

    def test_call_with_retry_retries_on_429(self) -> None:
        provider = _ConcreteProvider()
        provider.MAX_RETRIES = 3
        provider.RETRY_DELAY = 0.01

        rate_resp = MagicMock(spec=requests.Response)
        rate_resp.status_code = 429
        rate_resp.text = "Rate limited"
        success_resp = MagicMock(spec=requests.Response)
        success_resp.status_code = 200

        fn = MagicMock(side_effect=[rate_resp, success_resp])
        result = provider.call_with_retry(fn)
        assert result == success_resp

    def test_call_with_retry_raises_on_timeout(self) -> None:
        provider = _ConcreteProvider()
        provider.MAX_RETRIES = 1
        provider.RETRY_DELAY = 0.01

        fn = MagicMock(side_effect=requests.Timeout("timed out"))
        with pytest.raises(ProviderError, match="timed out"):
            provider.call_with_retry(fn)

    def test_call_with_retry_raises_on_connection_error(self) -> None:
        provider = _ConcreteProvider()
        provider.MAX_RETRIES = 1
        provider.RETRY_DELAY = 0.01

        fn = MagicMock(side_effect=requests.ConnectionError("refused"))
        with pytest.raises(ProviderError, match="Connection error"):
            provider.call_with_retry(fn)

    def test_call_with_retry_exhausts_retries(self) -> None:
        provider = _ConcreteProvider()
        provider.MAX_RETRIES = 3
        provider.RETRY_DELAY = 0.01

        error_resp = MagicMock(spec=requests.Response)
        error_resp.status_code = 503
        error_resp.text = "Service unavailable"

        fn = MagicMock(return_value=error_resp)
        with pytest.raises(ProviderError) as excinfo:
            provider.call_with_retry(fn)
        assert "Max retries exceeded" in str(excinfo.value)
        assert fn.call_count == 3

    def test_call_with_retry_non_retryable_error(self) -> None:
        provider = _ConcreteProvider()
        fn = MagicMock(side_effect=requests.RequestException("broken"))
        with pytest.raises(ProviderError, match="broken"):
            provider.call_with_retry(fn)


class _ConcreteProvider(BaseModelProvider):
    """Minimal concrete provider for testing base class methods."""

    def generate_response(self, question, context=None):
        return ModelResponse("test")

    def critique_response(self, question, response, context=None):
        return ModelResponse("test")

    def revise_position(self, question, original_response, critique, context=None):
        return ModelResponse("test")


# ═══════════════════════════════════════════════════════════
# Gemini provider (mocked HTTP)
# ═══════════════════════════════════════════════════════════

class TestGeminiProvider:
    def setup_method(self) -> None:
        self.provider = GeminiProvider()
        self.provider.api_key = "test-key"

    def test_generate_response_parses_content(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock(spec=requests.Response)
            mock_resp.json.return_value = {
                "candidates": [
                    {"content": {"parts": [{"text": "Balanced analysis of the topic.\nConfidence: 88"}]}}
                ]
            }
            mock_call.return_value = mock_resp

            result = self.provider.generate_response("Test question?")
            assert "Balanced analysis" in result.content
            assert result.confidence == 88.0

    def test_critique_response(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "candidates": [
                    {"content": {"parts": [{"text": "Strengths and weaknesses.\nConfidence: 80"}]}}
                ]
            }
            mock_call.return_value = mock_resp
            result = self.provider.critique_response("Q?", "Response")
            assert "Strengths" in result.content

    def test_revise_position(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "candidates": [
                    {"content": {"parts": [{"text": "Revised analysis.\nConfidence: 90"}]}}
                ]
            }
            mock_call.return_value = mock_resp
            result = self.provider.revise_position("Q?", "Original", "Critique")
            assert "Revised" in result.content

    def test_raises_on_empty_candidates(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"candidates": []}
            mock_call.return_value = mock_resp
            with pytest.raises(ProviderError, match="Empty response"):
                self.provider.generate_response("Q?")

    def test_raises_if_no_api_key(self) -> None:
        self.provider.api_key = ""
        with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
            self.provider.generate_response("Q?")


# ═══════════════════════════════════════════════════════════
# Groq provider (mocked HTTP)
# ═══════════════════════════════════════════════════════════

class TestGroqProvider:
    def setup_method(self) -> None:
        self.provider = GroqProvider()
        self.provider.api_key = "test-key"

    def test_generate_response(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Critical analysis.\nConfidence: 75"}}]
            }
            mock_call.return_value = mock_resp
            result = self.provider.generate_response("Test question?")
            assert "Critical" in result.content
            assert result.confidence == 75.0

    def test_raises_if_no_api_key(self) -> None:
        self.provider.api_key = ""
        with pytest.raises(ProviderError, match="GROQ_API_KEY"):
            self.provider.generate_response("Q?")


# ═══════════════════════════════════════════════════════════
# OpenRouter provider (mocked HTTP)
# ═══════════════════════════════════════════════════════════

class TestOpenRouterProvider:
    def setup_method(self) -> None:
        self.provider = OpenRouterProvider()
        self.provider.api_key = "test-key"

    def test_generate_response(self) -> None:
        with patch.object(self.provider, "call_with_retry") as mock_call:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Devil's advocate perspective.\nConfidence: 82"}}]
            }
            mock_call.return_value = mock_resp
            result = self.provider.generate_response("Test question?")
            assert "Devil" in result.content or "perspective" in result.content
            assert result.confidence == 82.0

    def test_raises_if_no_api_key(self) -> None:
        self.provider.api_key = ""
        with pytest.raises(ProviderError, match="OPENROUTER_API_KEY"):
            self.provider.generate_response("Q?")

    def test_timeout_is_120(self) -> None:
        assert self.provider.TIMEOUT == 120


# ═══════════════════════════════════════════════════════════
# Mock providers
# ═══════════════════════════════════════════════════════════

class TestMockProviders:
    def test_model_a_generates_content(self) -> None:
        p = ModelAProvider()
        r = p.generate_response("Test?")
        assert "Model-A" in r.content
        assert r.confidence == 82.0

    def test_model_b_generates_content(self) -> None:
        p = ModelBProvider()
        r = p.generate_response("Test?")
        assert "Model-B" in r.content
        assert r.confidence == 76.0

    def test_model_c_generates_content(self) -> None:
        p = ModelCProvider()
        r = p.generate_response("Test?")
        assert "Model-C" in r.content
        assert r.confidence == 79.0

    def test_all_mock_methods_work(self) -> None:
        for p in [ModelAProvider(), ModelBProvider(), ModelCProvider()]:
            assert p.generate_response("Q?").content
            assert p.critique_response("Q?", "R").content
            assert p.revise_position("Q?", "O", "C").content


# ═══════════════════════════════════════════════════════════
# Provider registry
# ═══════════════════════════════════════════════════════════

class TestProviderRegistry:
    def test_all_providers_are_registered(self) -> None:
        providers = list_providers()
        assert "gemini" in providers
        assert "groq" in providers
        assert "openrouter" in providers
        assert "openai" in providers
        assert "model_a" in providers
        assert "model_b" in providers
        assert "model_c" in providers

    def test_get_provider_class_returns_correct_class(self) -> None:
        assert get_provider_class("gemini") == GeminiProvider
        assert get_provider_class("groq") == GroqProvider
        assert get_provider_class("openrouter") == OpenRouterProvider
        assert get_provider_class("openai") == OpenAIProvider
        assert get_provider_class("model_a") == ModelAProvider
        assert get_provider_class("model_b") == ModelBProvider
        assert get_provider_class("model_c") == ModelCProvider

    def test_get_unknown_provider_returns_none(self) -> None:
        assert get_provider_class("nonexistent") is None

    def test_register_new_provider(self) -> None:
        class DummyProvider(BaseModelProvider):
            def generate_response(self, question, context=None):
                return ModelResponse("dummy")
            def critique_response(self, question, response, context=None):
                return ModelResponse("dummy")
            def revise_position(self, question, original_response, critique, context=None):
                return ModelResponse("dummy")

        register_provider("dummy", DummyProvider)
        assert get_provider_class("dummy") == DummyProvider


# ═══════════════════════════════════════════════════════════
# Model config
# ═══════════════════════════════════════════════════════════

class TestModelConfig:
    def test_production_agents_are_defined(self) -> None:
        assert "agent-a" in AVAILABLE_MODELS
        assert "agent-b" in AVAILABLE_MODELS
        assert "agent-c" in AVAILABLE_MODELS

    def test_agent_provider_keys(self) -> None:
        assert AVAILABLE_MODELS["agent-a"].provider_key == "gemini"
        assert AVAILABLE_MODELS["agent-b"].provider_key == "groq"
        assert AVAILABLE_MODELS["agent-c"].provider_key == "openrouter"

    def test_mock_models_still_available(self) -> None:
        assert "model-a" in AVAILABLE_MODELS
        assert "model-b" in AVAILABLE_MODELS
        assert "model-c" in AVAILABLE_MODELS

    def test_get_model_config_returns_agent(self) -> None:
        config = get_model_config("agent-a")
        assert config is not None
        assert config.name == "agent-a"
        assert config.provider_key == "gemini"
        assert config.metadata.get("role") == "balanced_analyst"

    def test_get_unknown_model_returns_none(self) -> None:
        assert get_model_config("nonexistent") is None


# ═══════════════════════════════════════════════════════════
# Provider factory
# ═══════════════════════════════════════════════════════════

class TestProviderFactory:
    def test_create_agent_a(self) -> None:
        provider = create_provider("agent-a")
        assert provider is not None
        assert isinstance(provider, GeminiProvider)

    def test_create_agent_b(self) -> None:
        provider = create_provider("agent-b")
        assert provider is not None
        assert isinstance(provider, GroqProvider)

    def test_create_agent_c(self) -> None:
        provider = create_provider("agent-c")
        assert provider is not None
        assert isinstance(provider, OpenRouterProvider)

    def test_create_mock_model_a(self) -> None:
        provider = create_provider("model-a")
        assert provider is not None
        assert isinstance(provider, ModelAProvider)

    def test_create_mock_model_b(self) -> None:
        provider = create_provider("model-b")
        assert provider is not None
        assert isinstance(provider, ModelBProvider)

    def test_create_mock_model_c(self) -> None:
        provider = create_provider("model-c")
        assert provider is not None
        assert isinstance(provider, ModelCProvider)

    def test_create_openai_gpt4o_mini(self) -> None:
        provider = create_provider("gpt-4o-mini")
        assert provider is not None
        assert isinstance(provider, OpenAIProvider)

    def test_create_unknown_returns_none(self) -> None:
        assert create_provider("nonexistent") is None

    def test_all_production_agents_implement_base_methods(self) -> None:
        for model in ["agent-a", "agent-b", "agent-c"]:
            # Mock the HTTP calls for production providers
            provider = create_provider(model)
            assert provider is not None

            # Set a dummy API key and mock call_with_retry
            provider.api_key = "test"
            with patch.object(provider, "call_with_retry") as mock_call:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "choices": [{"message": {"content": "Test.\nConfidence: 80"}}]
                }
                if isinstance(provider, GeminiProvider):
                    mock_resp.json.return_value = {
                        "candidates": [{"content": {"parts": [{"text": "Test.\nConfidence: 80"}]}}]
                    }
                mock_call.return_value = mock_resp

                r1 = provider.generate_response("Q?")
                r2 = provider.critique_response("Q?", "R")
                r3 = provider.revise_position("Q?", "O", "C")
                assert r1.content and r2.content and r3.content
