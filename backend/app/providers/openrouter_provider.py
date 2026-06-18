"""OpenRouter provider — unified access to models via OpenRouter.

Configured entirely through environment variables:
- OPENROUTER_API_KEY: Your OpenRouter API key
- OPENROUTER_MODEL: Model identifier (default: deepseek/deepseek-r1)
"""

from app.core.config import settings
from app.providers.base import BaseModelProvider, ModelResponse, ProviderError


class OpenRouterProvider(BaseModelProvider):
    """Provider using OpenRouter's unified API.

    Used for Agent C (devil's advocate) with DeepSeek R1.
    """

    TIMEOUT: int = 120  # DeepSeek R1 can be slower

    def __init__(self) -> None:
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL

    def _call(self, system_prompt: str, user_message: str) -> ModelResponse:
        if not self.api_key:
            raise ProviderError(
                "OPENROUTER_API_KEY is not configured. Set it in your .env file.",
                "OpenRouterProvider",
            )

        response = self.call_with_retry(
            self._make_request,
            system_prompt,
            user_message,
        )
        data = response.json()
        content = data["choices"][0]["message"]["content"] or ""
        confidence = self.extract_confidence(content)
        return ModelResponse(content=content, confidence=confidence)

    def _make_request(self, system_prompt: str, user_message: str, timeout: int = 120):
        import requests
        return requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://synapse-ai.app",
                "X-Title": "Synapse AI",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            timeout=timeout,
        )

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a devil's advocate in a structured AI debate. "
                "Your role is to challenge assumptions, explore alternative viewpoints, "
                "and question conventional thinking. Push back against the obvious answer. "
                "Raise uncomfortable questions and consider perspectives others might miss. "
                "Be provocative but reasoned. End with a confidence score (e.g., 'Confidence: 82')."
            ),
            user_message=f"Debate question: {question}\n\nProvide your perspective:",
        )

    def critique_response(self, question: str, response: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a devil's advocate in a structured AI debate. "
                "Your role is to challenge the given argument by finding hidden assumptions, "
                "alternative interpretations, and unexplored angles. Question everything "
                "that is taken for granted. End with a confidence score (e.g., 'Confidence: 79')."
            ),
            user_message=f"Question: {question}\n\nResponse to challenge:\n{response}",
        )

    def revise_position(
        self, question: str, original_response: str, critique: str, context: str | None = None
    ) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a devil's advocate in a structured AI debate. "
                "You have received a critique of your original position. "
                "Consider whether the critique reveals assumptions you didn't examine. "
                "Revise your position if the critique identifies genuine gaps, or "
                "counter-challenge if your original stance still holds. "
                "End with a confidence score (e.g., 'Confidence: 86')."
            ),
            user_message=(
                f"Question: {question}\n\nYour original position:\n{original_response}\n\n"
                f"Critique received:\n{critique}\n\nProvide your revised position:"
            ),
        )
