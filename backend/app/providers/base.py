"""Base provider — abstract interface for all LLM providers.

All LLM providers must implement this interface to be
compatible with the Synapse AI orchestration system.
"""

from abc import ABC, abstractmethod


class ModelResponse:
    """Standard response structure from any model provider.

    Attributes:
        content: The generated text response.
        confidence: Confidence score (0-100) for the response.
    """

    def __init__(self, content: str, confidence: float = 50.0) -> None:
        self.content = content
        self.confidence = confidence


class BaseModelProvider(ABC):
    """Abstract base class for all LLM providers.

    Defines the interface that every provider must implement.
    New providers (OpenAI, Anthropic, Google, local models) can
    be added by subclassing this and implementing the three methods.
    """

    @abstractmethod
    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        """Generate an initial opinion on a question.

        Args:
            question: The debate question.
            context: Optional additional context (domain, instructions, etc.).

        Returns:
            ModelResponse containing the generated opinion and confidence.
        """
        ...

    @abstractmethod
    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        """Critique another model's response.

        Args:
            question: The original debate question.
            response: The response to critique.
            context: Optional additional context.

        Returns:
            ModelResponse containing critique and counterarguments.
        """
        ...

    @abstractmethod
    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        """Revise a position after receiving a critique.

        Args:
            question: The original debate question.
            original_response: The model's initial response.
            critique: The critique received from another model.
            context: Optional additional context.

        Returns:
            ModelResponse containing revised opinion and updated confidence.
        """
        ...
