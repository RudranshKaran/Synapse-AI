"""Mock provider for Model B.

Returns deterministic responses for development and testing.
"""

from app.providers.base import BaseModelProvider, ModelResponse


class ModelBProvider(BaseModelProvider):
    """Mock implementation of Model B."""

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return ModelResponse(
            content=f"Mock response from Model-B analyzing: {question[:50]}...",
            confidence=76.0,
        )

    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-B critiques: The response makes several assumptions "
                    f"that may not hold in all scenarios. "
                    f"Consider edge cases and potential exceptions.",
            confidence=74.0,
        )

    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-B revised position: Upon reflection, I have adjusted "
                    f"my position to address the valid concerns raised. "
                    f"The updated response better accounts for complexity.",
            confidence=80.0,
        )
