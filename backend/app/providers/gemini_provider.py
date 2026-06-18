"""Gemini provider — Google's Gemini models via the generative AI API.

Configured entirely through environment variables:
- GEMINI_API_KEY: Your Google AI API key
- GEMINI_MODEL: Model identifier (default: gemini-2.5-flash)

Used for Agent A (balanced analyst) and the Consensus Agent (synthesis).
"""

from app.core.config import settings
from app.providers.base import BaseModelProvider, ModelResponse, ProviderError


class GeminiProvider(BaseModelProvider):
    """Provider using Google's Gemini API.

    Used for Agent A (balanced analyst) with Gemini 2.5 Flash.
    """

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL

    def _call(self, system_prompt: str, user_message: str) -> ModelResponse:
        if not self.api_key:
            raise ProviderError(
                "GEMINI_API_KEY is not configured. Set it in your .env file.",
                "GeminiProvider",
            )

        response = self.call_with_retry(
            self._make_request,
            system_prompt,
            user_message,
        )
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ProviderError(
                f"Empty response from Gemini API: {data}",
                "GeminiProvider",
            )
        content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        confidence = self.extract_confidence(content)
        return ModelResponse(content=content, confidence=confidence)

    def _make_request(self, system_prompt: str, user_message: str, timeout: int = 60):
        import requests
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        return requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_message}"}],
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                },
            },
            timeout=timeout,
        )

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a balanced analyst in a structured AI debate. "
                "Your role is to provide a well-reasoned, even-handed analysis of "
                "the question. Consider multiple perspectives, weigh pros and cons, "
                "and arrive at a nuanced position. Be objective and thorough. "
                "End with a confidence score (e.g., 'Confidence: 85')."
            ),
            user_message=f"Debate question: {question}\n\nProvide your analysis:",
        )

    def critique_response(self, question: str, response: str, context: str | None = None) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a balanced analyst in a structured AI debate. "
                "Your role is to evaluate the given argument fairly. Identify both "
                "its strengths and weaknesses. Acknowledge valid points while "
                "pointing out areas that need more evidence or better reasoning. "
                "End with a confidence score (e.g., 'Confidence: 80')."
            ),
            user_message=f"Question: {question}\n\nResponse to analyze:\n{response}",
        )

    def revise_position(
        self, question: str, original_response: str, critique: str, context: str | None = None
    ) -> ModelResponse:
        return self._call(
            system_prompt=(
                "You are a balanced analyst in a structured AI debate. "
                "You have received a critique of your original analysis. "
                "Review the critique carefully. Update your position if the critique "
                "raises valid points. If you maintain your stance, strengthen your "
                "reasoning. Aim for a position that incorporates the best insights "
                "from all sides. End with a confidence score (e.g., 'Confidence: 88')."
            ),
            user_message=(
                f"Question: {question}\n\nYour original analysis:\n{original_response}\n\n"
                f"Critique received:\n{critique}\n\nProvide your revised analysis:"
            ),
        )
