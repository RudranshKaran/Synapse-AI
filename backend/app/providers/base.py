"""Base provider — abstract interface for all LLM providers.

All LLM providers must implement this interface to be
compatible with the Synapse AI orchestration system.
"""

import re
import time
from abc import ABC, abstractmethod

import requests


class ProviderError(Exception):
    """Raised when a provider encounters a non-retryable error."""

    def __init__(self, message: str, provider_name: str, status_code: int = 500) -> None:
        self.provider_name = provider_name
        self.status_code = status_code
        super().__init__(f"[{provider_name}] {message}")


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

    # Default retry and timeout settings — providers can override
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    TIMEOUT: int = 60

    @abstractmethod
    def generate_response(self, question: str, context: str | None = None) -> ModelResponse:
        ...

    @abstractmethod
    def critique_response(
        self, question: str, response: str, context: str | None = None
    ) -> ModelResponse:
        ...

    @abstractmethod
    def revise_position(
        self,
        question: str,
        original_response: str,
        critique: str,
        context: str | None = None,
    ) -> ModelResponse:
        ...

    # ── Standardized helpers for subclasses ────────────────

    @staticmethod
    def extract_confidence(text: str, default: float = 50.0) -> float:
        """Extract a confidence score from response text.

        Looks for patterns like 'Confidence: 85' or 'confidence: 85%'
        in the last lines of text. Returns default if not found.
        """
        lines = text.strip().split("\n")
        for line in reversed(lines):
            match = re.search(
                r"(?:confidence|Confidence)[:\s]*(-?\d{1,3})(?:%|/100)?",
                line,
            )
            if match:
                score = float(match.group(1))
                return min(max(score, 0.0), 100.0)
        return default

    def call_with_retry(
        self, fn, *args, **kwargs
    ) -> requests.Response:
        """Call an HTTP function with retry logic.

        Retries on 5xx, 429 (rate limit), and connection errors.
        Raises ProviderError on failure.
        """
        last_error: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = fn(*args, timeout=self.TIMEOUT, **kwargs)
                if response.status_code < 500 and response.status_code != 429:
                    return response
                # Retry on server errors and rate limits
                last_error = ProviderError(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    self.__class__.__name__,
                    response.status_code,
                )
                if response.status_code == 429:
                    # Rate limit — wait longer
                    time.sleep(self.RETRY_DELAY * (2 ** attempt) * 2)
                else:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
            except requests.Timeout as e:
                last_error = ProviderError(
                    f"Request timed out after {self.TIMEOUT}s",
                    self.__class__.__name__,
                )
                time.sleep(self.RETRY_DELAY * (2 ** attempt))
            except requests.ConnectionError as e:
                last_error = ProviderError(
                    f"Connection error: {e}",
                    self.__class__.__name__,
                )
                time.sleep(self.RETRY_DELAY * (2 ** attempt))
            except requests.RequestException as e:
                raise ProviderError(
                    f"Request failed: {e}",
                    self.__class__.__name__,
                )

        raise ProviderError(
            f"Max retries exceeded: {last_error}",
            self.__class__.__name__,
        )
