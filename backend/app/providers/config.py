"""Model configuration system.

Defines available models and their provider mappings.
New models can be registered here without changing business logic.
"""

from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider_key: str
    display_name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    metadata: dict = field(default_factory=dict)


# Registry of all available models
AVAILABLE_MODELS: dict[str, ModelConfig] = {
    "model-a": ModelConfig(
        name="model-a",
        provider_key="model_a",
        display_name="Model A",
    ),
    "model-b": ModelConfig(
        name="model-b",
        provider_key="model_b",
        display_name="Model B",
    ),
    "model-c": ModelConfig(
        name="model-c",
        provider_key="model_c",
        display_name="Model C",
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider_key="openai",
        display_name="GPT-4o Mini",
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider_key="openai",
        display_name="GPT-4o",
    ),
}


def get_model_config(model_name: str) -> ModelConfig | None:
    """Retrieve configuration for a named model.

    Args:
        model_name: The model identifier (e.g. "model-a").

    Returns:
        ModelConfig if found, otherwise None.
    """
    return AVAILABLE_MODELS.get(model_name)
