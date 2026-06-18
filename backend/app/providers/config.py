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


# Default Synapse AI agent configuration
# Agent A: Balanced Analyst → Gemini 2.5 Flash
# Agent B: Critical Reviewer → Llama 3.1 8B Instant (Groq)
# Agent C: Devil's Advocate → DeepSeek R1 (OpenRouter)
# Consensus Agent: Synthesis → Gemini 2.5 Flash
AVAILABLE_MODELS: dict[str, ModelConfig] = {
    # Production agents
    "agent-a": ModelConfig(
        name="agent-a",
        provider_key="gemini",
        display_name="Agent A (Gemini 2.5 Flash)",
        metadata={"role": "balanced_analyst"},
    ),
    "agent-b": ModelConfig(
        name="agent-b",
        provider_key="groq",
        display_name="Agent B (Llama 3.1 Groq)",
        metadata={"role": "critical_reviewer"},
    ),
    "agent-c": ModelConfig(
        name="agent-c",
        provider_key="openrouter",
        display_name="Agent C (DeepSeek R1)",
        metadata={"role": "devils_advocate"},
    ),
    # Legacy mock model aliases (for backward compatibility)
    "model-a": ModelConfig(
        name="model-a",
        provider_key="model_a",
        display_name="Model A (Mock)",
    ),
    "model-b": ModelConfig(
        name="model-b",
        provider_key="model_b",
        display_name="Model B (Mock)",
    ),
    "model-c": ModelConfig(
        name="model-c",
        provider_key="model_c",
        display_name="Model C (Mock)",
    ),
    # Direct model access
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
        model_name: The model identifier (e.g. "agent-a").

    Returns:
        ModelConfig if found, otherwise None.
    """
    return AVAILABLE_MODELS.get(model_name)


def get_default_agent_models() -> list[str]:
    """Return the default set of agent models for a Synapse AI debate.

    Returns:
        ["agent-a", "agent-b", "agent-c"]
    """
    return ["agent-a", "agent-b", "agent-c"]
