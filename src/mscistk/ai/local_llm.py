"""Thin client for interacting with a local LLM endpoint (e.g. Ollama)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

LOGGER = logging.getLogger(__name__)


class LocalLLMError(RuntimeError):
    """Raised when the local LLM endpoint cannot process a request."""


@dataclass
class LocalLLMConfig:
    """Configuration for the LocalLLMClient."""

    endpoint: str = "http://127.0.0.1:11434/api/generate"
    default_model: str = "llama3"
    timeout: int = 60
    verify_ssl: bool = True


class LocalLLMClient:
    """HTTP client that talks to a local LLM endpoint (Ollama-compatible)."""

    def __init__(self, config: Optional[LocalLLMConfig] = None):
        self.config = config or LocalLLMConfig()

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using the configured LLM endpoint.

        Args:
            prompt: Prompt text sent to the model.
            model: Override for the default model from config.
            temperature: Sampling temperature (0-1 range usually).
            max_tokens: Maximum tokens to predict (mapped to `num_predict`).

        Returns:
            Text response from the local LLM.

        Raises:
            LocalLLMError: If the endpoint cannot be reached or responds with
                an unexpected payload.
        """

        payload: Dict[str, Any] = {
            "model": model or self.config.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(
                self.config.endpoint,
                json=payload,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
        except requests.RequestException as exc:
            raise LocalLLMError(
                f"Local LLM endpoint unreachable: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise LocalLLMError(
                f"Local LLM returned HTTP {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise LocalLLMError("Local LLM returned non-JSON response") from exc

        # Ollama-compatible responses use the `response` field when `stream=False`.
        text = data.get("response")

        # Allow alternative response shapes for other providers.
        if text is None and "choices" in data:
            choices = data["choices"]
            if isinstance(choices, list) and choices:
                text = choices[0].get("text") or choices[0].get("message", {}).get(
                    "content"
                )

        if not text:
            LOGGER.debug("Unexpected LLM payload: %s", data)
            raise LocalLLMError("Local LLM response missing text payload")

        return text.strip()
