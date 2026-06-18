"""Provider registry — maps provider keys to provider classes.

Providers register themselves here so the factory can
instantiate them by key. New providers just need to
register themselves.
"""

from app.providers.base import BaseModelProvider
from app.providers.mocks.model_a import ModelAProvider
from app.providers.mocks.model_b import ModelBProvider
from app.providers.mocks.model_c import ModelCProvider
from app.providers.openai_provider import OpenAIProvider

_registry: dict[str, type[BaseModelProvider]] = {}


def register_provider(key: str, provider_class: type[BaseModelProvider]) -> None:
    """Register a provider class under a key.

    Args:
        key: The provider key (e.g. "model_a", "openai", "anthropic").
        provider_class: The provider class to register.
    """
    _registry[key] = provider_class


def get_provider_class(key: str) -> type[BaseModelProvider] | None:
    """Retrieve a registered provider class by key.

    Args:
        key: The provider key.

    Returns:
        The provider class if registered, otherwise None.
    """
    return _registry.get(key)


def list_providers() -> list[str]:
    """List all registered provider keys.

    Returns:
        Sorted list of registered provider keys.
    """
    return sorted(_registry.keys())


# Register mock providers on import
register_provider("model_a", ModelAProvider)
register_provider("model_b", ModelBProvider)
register_provider("model_c", ModelCProvider)
register_provider("openai", OpenAIProvider)
