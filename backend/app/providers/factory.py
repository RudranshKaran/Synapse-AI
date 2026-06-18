"""Provider factory — creates provider instances by model name.

The factory decouples model selection from provider instantiation.
Callers specify a model name and get back a configured provider instance.
"""

from app.providers.base import BaseModelProvider
from app.providers.config import get_model_config
from app.providers.registry import get_provider_class


def create_provider(model_name: str) -> BaseModelProvider | None:
    """Create a provider instance for the given model name.

    Looks up the model configuration to find the provider key,
    then instantiates the corresponding provider class.

    Args:
        model_name: The model identifier (e.g. "model-a").

    Returns:
        An instance of the matching provider, or None if not found.
    """
    config = get_model_config(model_name)
    if config is None:
        return None

    provider_class = get_provider_class(config.provider_key)
    if provider_class is None:
        return None

    return provider_class()
