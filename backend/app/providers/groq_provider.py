"""Groq provider — fast inference via Groq API (Llama, Mixtral, etc.).

Configured entirely through environment variables:
- GROQ_API_KEY: Your Groq API key
- GROQ_MODEL: Model identifier (default: llama-3.1-8b-instant)
"""

from app.core.config import settings
from app.providers.base import BaseModelProvider, ModelResponse, ProviderError


class GroqProvider(BaseModelProvider):
    """Provider using Groq's ultra-fast inference API.

    Used for Agent B (critical reviewer) with Llama 3.1 8B Instant.
    """

    def __init__(self) -> None:
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL

    def _call(self, system_prompt: str, user_message: str) -> ModelResponse:
        if not self.api_key:
            raise ProviderError(
                "GROQ_API_KEY is not configured. Set it in your .env file.",
                "GroqProvider",
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

    def _make_request(self, system_prompt: str, user_message: str, timeout: int = 60):
        import requests
        return requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            timeout=timeout,
        )

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a critical reviewer in a structured AI debate. "
                "Your role is to focus on weaknesses, practical concerns, and potential "
                "failure modes in any proposal or argument. Be thorough but constructive. "
                "Ground your critique in real-world constraints and empirical considerations. "
                "End your response with a confidence score (e.g., 'Confidence: 85')."
            ),
            user_message=f"Debate question: {question}\n\nProvide your analysis:",
        )

    def critique_response(self, question: str, response: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a critical reviewer in a structured AI debate. "
                "Your role is to scrutinize arguments for logical gaps, unsupported "
                "assumptions, overlooked practical concerns, and edge cases. "
                "Be sharp but fair. End with a confidence score (e.g., 'Confidence: 78')."
            ),
            user_message=f"Question: {question}\n\nResponse to critique:\n{response}",
        )

    def revise_position(
        self, question: str, original_response: str, critique: str, context: str | None = None
    ) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a critical reviewer in a structured AI debate. "
                "You have received a critique of your original position. "
                "Review it carefully. If the critique reveals genuine weaknesses, "
                "revise your position. If it does not, defend your stance with "
                "stronger reasoning. End with a confidence score (e.g., 'Confidence: 88')."
            ),
            user_message=(
                f"Question: {question}\n\nYour original analysis:\n{original_response}\n\n"
                f"Critique received:\n{critique}\n\nProvide your revised position:"
            ),
        )
