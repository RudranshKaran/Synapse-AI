"""Tests for the provider abstraction layer."""

from app.providers.base import BaseModelProvider, ModelResponse
from app.providers.config import AVAILABLE_MODELS, get_model_config
from app.providers.factory import create_provider
from app.providers.mocks.model_a import ModelAProvider
from app.providers.mocks.model_b import ModelBProvider
from app.providers.mocks.model_c import ModelCProvider
from app.providers.registry import (
    get_provider_class,
    list_providers,
    register_provider,
)


class TestModelResponse:
    """ModelResponse data class tests."""

    def test_creates_with_content_and_confidence(self) -> None:
        response = ModelResponse(content="Test response", confidence=85.0)
        assert response.content == "Test response"
        assert response.confidence == 85.0

    def test_default_confidence(self) -> None:
        response = ModelResponse(content="Test")
        assert response.confidence == 50.0


class TestModelAProvider:
    """Model A mock provider tests."""

    def setup_method(self) -> None:
        self.provider = ModelAProvider()

    def test_is_valid_provider(self) -> None:
        assert isinstance(self.provider, BaseModelProvider)

    def test_generate_response_returns_content(self) -> None:
        result = self.provider.generate_response("Test question?")
        assert result.content is not None
        assert "Model-A" in result.content

    def test_generate_response_returns_confidence(self) -> None:
        result = self.provider.generate_response("Test question?")
        assert result.confidence == 82.0

    def test_critique_response_returns_content(self) -> None:
        result = self.provider.critique_response(
            "Test question?", "Initial response"
        )
        assert result.content is not None
        assert "Model-A" in result.content

    def test_revise_position_returns_content(self) -> None:
        result = self.provider.revise_position(
            "Test question?", "Original", "Critique"
        )
        assert result.content is not None
        assert "Model-A" in result.content


class TestModelBProvider:
    """Model B mock provider tests."""

    def setup_method(self) -> None:
        self.provider = ModelBProvider()

    def test_generate_response_contains_model_b(self) -> None:
        result = self.provider.generate_response("Test?")
        assert "Model-B" in result.content
        assert result.confidence == 76.0


class TestModelCProvider:
    """Model C mock provider tests."""

    def setup_method(self) -> None:
        self.provider = ModelCProvider()

    def test_generate_response_contains_model_c(self) -> None:
        result = self.provider.generate_response("Test?")
        assert "Model-C" in result.content
        assert result.confidence == 79.0


class TestProviderRegistry:
    """Provider registry tests."""

    def test_mock_providers_are_registered(self) -> None:
        providers = list_providers()
        assert "model_a" in providers
        assert "model_b" in providers
        assert "model_c" in providers

    def test_get_provider_class_returns_correct_class(self) -> None:
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


class TestModelConfig:
    """Model configuration tests."""

    def test_available_models_contains_all_mock_models(self) -> None:
        assert "model-a" in AVAILABLE_MODELS
        assert "model-b" in AVAILABLE_MODELS
        assert "model-c" in AVAILABLE_MODELS

    def test_get_model_config_returns_config(self) -> None:
        config = get_model_config("model-a")
        assert config is not None
        assert config.name == "model-a"
        assert config.provider_key == "model_a"

    def test_get_unknown_model_returns_none(self) -> None:
        assert get_model_config("nonexistent") is None


class TestProviderFactory:
    """Provider factory tests."""

    def test_create_model_a_provider(self) -> None:
        provider = create_provider("model-a")
        assert provider is not None
        assert isinstance(provider, ModelAProvider)

    def test_create_model_b_provider(self) -> None:
        provider = create_provider("model-b")
        assert provider is not None
        assert isinstance(provider, ModelBProvider)

    def test_create_model_c_provider(self) -> None:
        provider = create_provider("model-c")
        assert provider is not None
        assert isinstance(provider, ModelCProvider)

    def test_create_unknown_model_returns_none(self) -> None:
        assert create_provider("nonexistent") is None

    def test_all_providers_implement_base_methods(self) -> None:
        for model in ["model-a", "model-b", "model-c"]:
            provider = create_provider(model)
            assert provider is not None
            # All three methods should work
            r1 = provider.generate_response("Question?")
            r2 = provider.critique_response("Question?", "Response")
            r3 = provider.revise_position("Question?", "Original", "Critique")
            assert r1.content and r2.content and r3.content
