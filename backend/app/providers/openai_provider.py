"""OpenAI provider — real LLM implementation using the OpenAI API.

Configured entirely through environment variables:
- OPENAI_API_KEY: Your OpenAI API key
- OPENAI_MODEL: Model identifier (default: gpt-4o-mini)

The provider uses appropriate system prompts for each debate phase:
opinion generation, critique, and revision.
"""

from app.core.config import settings
from app.providers.base import BaseModelProvider, ModelResponse


class OpenAIProvider(BaseModelProvider):
    """Real LLM provider using OpenAI's chat completions API.

    Uses the model specified in OPENAI_MODEL env var.
    Falls back to gpt-4o-mini if not configured.
    """

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def _call_openai(self, system_prompt: str, user_message: str) -> ModelResponse:
        """Make an OpenAI chat completion call and extract response + confidence.

        Args:
            system_prompt: The system-level instruction.
            user_message: The user message content.

        Returns:
            ModelResponse with content and parsed confidence score.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "OpenAI provider requires the 'openai' package. "
                "Install it with: pip install openai"
            )

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Set it in your .env file."
            )

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=2048,
        )

        content = response.choices[0].message.content or ""
        confidence = self._extract_confidence(content)

        return ModelResponse(content=content, confidence=confidence)

    @staticmethod
    def _extract_confidence(text: str) -> float:
        """Extract a confidence score from the response text.

        Looks for a pattern like "Confidence: 85" or "confidence: 85%"
        in the last few lines of the response. Returns 50.0 if not found.
        """
        import re

        lines = text.strip().split("\n")
        for line in reversed(lines):
            match = re.search(
                r"(?:confidence|Confidence)[:\s]*(\d{1,3})(?:%|/100)?",
                line,
            )
            if match:
                score = float(match.group(1))
                return min(max(score, 0.0), 100.0)
        return 50.0

    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        return self._call_openai(
            system_prompt=(
                "You are a participant in a structured AI debate. "
                "Generate a clear, well-reasoned opinion on the given question. "
                "Include your position, supporting arguments, and a confidence score "
                "at the end (e.g., 'Confidence: 85')."
            ),
            user_message=question,
        )

    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        return self._call_openai(
            system_prompt=(
                "You are a critique agent in a structured AI debate. "
                "Analyze the given response and identify logical inconsistencies, "
                "weak assumptions, missing evidence, or alternative perspectives. "
                "Include a confidence score at the end (e.g., 'Confidence: 78')."
            ),
            user_message=f"Question: {question}\n\nResponse to critique:\n{response}",
        )

    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        return self._call_openai(
            system_prompt=(
                "You are a participant in a structured AI debate. "
                "You have received a critique of your original position. "
                "Review the critique carefully and revise your position if warranted. "
                "You may maintain, modify, or strengthen your stance. "
                "Include a confidence score at the end (e.g., 'Confidence: 88')."
            ),
            user_message=(
                f"Question: {question}\n\n"
                f"Your original position:\n{original_response}\n\n"
                f"Critique received:\n{critique}\n\n"
                f"Provide your revised position:"
            ),
        )
