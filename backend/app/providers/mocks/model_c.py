"""Mock provider for Model C.

Returns deterministic responses for development and testing.
"""

from app.providers.base import BaseModelProvider, ModelResponse


class ModelCProvider(BaseModelProvider):
    """Mock implementation of Model C."""

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return ModelResponse(
            content=f"Mock response from Model-C considering: {question[:50]}...",
            confidence=79.0,
        )

    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-C critiques: The reasoning pattern overlooks important "
                    f"contextual factors and relies on generalizations. "
                    f"A more nuanced approach would strengthen the argument.",
            confidence=71.0,
        )

    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        return ModelResponse(
            content=f"Model-C revised position: The critique raises valid points. "
                    f"I have refined my position to incorporate the feedback "
                    f"while maintaining my core stance.",
            confidence=85.0,
        )
