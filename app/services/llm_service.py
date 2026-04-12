"""
Reusable LLM service layer.

Provides a unified interface for generating text completions from
different LLM providers (OpenAI, Gemini).  The active provider is
selected via the ``LLM_PROVIDER`` environment variable.

Usage::

    from app.services.llm_service import LLMService

    llm = LLMService()
    result = await llm.generate("Summarise this workflow...")
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LLMError(Exception):
    """Raised when an LLM call fails."""

    def __init__(self, detail: str, provider: str = "") -> None:
        self.detail = detail
        self.provider = provider
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Send *prompt* to the provider and return the text response."""


# ---------------------------------------------------------------------------
# OpenAI provider
# ---------------------------------------------------------------------------

class OpenAIProvider(BaseLLMProvider):
    """OpenAI / ChatGPT completion provider."""

    name = "openai"

    def __init__(self) -> None:
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._client = None  # created lazily on first generate()
        self._available = True

        if not self._api_key:
            logger.warning(
                "OPENAI_API_KEY is not set. OpenAI calls will fail at runtime."
            )

        # Check import availability without creating a client
        try:
            import openai as _  # noqa: F401
        except ImportError:
            self._available = False
            logger.warning(
                "openai package not installed. "
                "Install with: pip install openai"
            )

    def _get_client(self):
        """Lazily create the AsyncOpenAI client on first use."""
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if not self._available:
            raise LLMError(
                "openai package is not installed.", provider=self.name
            )
        if not self._api_key:
            raise LLMError(
                "OPENAI_API_KEY environment variable is not set.",
                provider=self.name,
            )

        _model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if content is None:
                raise LLMError(
                    "OpenAI returned an empty response.", provider=self.name
                )

            logger.info(
                "OpenAI [%s] — prompt %d chars → response %d chars",
                _model, len(prompt), len(content),
            )
            return content.strip()

        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(
                f"OpenAI API error: {exc}", provider=self.name
            ) from exc


# ---------------------------------------------------------------------------
# Gemini provider (placeholder)
# ---------------------------------------------------------------------------

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini completion provider using the updated ``google-genai`` SDK.
    """

    name = "gemini"

    def __init__(self) -> None:
        self._api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = None  # created lazily
        self._available = True

        if not self._api_key:
            logger.warning(
                "GEMINI_API_KEY is not set. Gemini calls will fail at runtime."
            )

        # Check import availability without creating a client
        try:
            import google.genai as _  # noqa: F401
        except ImportError:
            self._available = False
            logger.warning(
                "google-genai package not installed. "
                "Install with: pip install google-genai"
            )

    def _get_client(self):
        """Lazily initialize the google-genai Client on first use."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if not self._available:
            raise LLMError(
                "google-genai package is not installed.",
                provider=self.name,
            )
        if not self._api_key:
            raise LLMError(
                "GEMINI_API_KEY environment variable is not set.",
                provider=self.name,
            )

        _model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        try:
            from google.genai import types
            
            client = self._get_client()
            response = await client.aio.models.generate_content(
                model=_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            content = response.text
            if not content:
                raise LLMError(
                    "Gemini returned an empty response.", provider=self.name
                )

            logger.info(
                "Gemini [%s] — prompt %d chars → response %d chars",
                _model, len(prompt), len(content),
            )
            return content.strip()

        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(
                f"Gemini API error: {exc}", provider=self.name
            ) from exc


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

_PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


def _resolve_provider(name: str) -> BaseLLMProvider:
    cls = _PROVIDERS.get(name.lower())
    if cls is None:
        raise LLMError(
            f"Unknown LLM provider '{name}'. "
            f"Available: {', '.join(_PROVIDERS.keys())}",
        )
    return cls()


# ---------------------------------------------------------------------------
# Public façade
# ---------------------------------------------------------------------------

class LLMService:
    """
    Unified LLM gateway.

    Picks the active provider from the ``LLM_PROVIDER`` env var
    (default: ``openai``).  All callers use ``.generate()`` and
    never need to know which provider is behind it.

    Example::

        llm = LLMService()                       # uses default provider
        llm = LLMService(provider="gemini")       # explicit override

        text = await llm.generate("Summarise: ...")
    """

    def __init__(self, provider: Optional[str] = None) -> None:
        self._provider_name = (
            provider
            or os.getenv("LLM_PROVIDER", "openai")
        ).lower()
        self._provider = _resolve_provider(self._provider_name)
        logger.info("LLMService initialised with provider: %s", self._provider_name)

    # -- Core API ------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a completion for *prompt*.

        Parameters
        ----------
        prompt : str
            The full prompt text.  Do **not** hardcode prompts in this
            layer — compose them in the calling service.
        model : str, optional
            Override the default model for this call.
        temperature : float
            Sampling temperature (0 = deterministic, 1 = creative).
        max_tokens : int
            Maximum tokens in the response.

        Returns
        -------
        str
            The generated text, stripped of leading/trailing whitespace.

        Raises
        ------
        LLMError
            On any provider or network failure.
        """
        return await self._provider.generate(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # -- Introspection -------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def __repr__(self) -> str:
        return f"LLMService(provider={self._provider_name!r})"
