"""Mock provider for Model A.

Returns deterministic responses for development and testing.
"""

from app.providers.base import BaseModelProvider, ModelResponse


class ModelAProvider(BaseModelProvider):
    """Mock implementation of Model A.

    Provides predictable responses so the system can be
    developed and tested without real LLM API calls.
    """

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return ModelResponse(
            content=f"Mock response from Model-A regarding: {question[:50]}...",
            confidence=82.0,
        )

    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-A critiques: The argument lacks sufficient evidence and "
                    f"does not consider alternative perspectives. "
                    f"Further analysis is required to validate the claims.",
            confidence=78.0,
        )

    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-A revised position: After considering the critique, "
                    f"I acknowledge the limitations in my initial reasoning. "
                    f"Updated position incorporates the feedback provided.",
            confidence=88.0,
        )
