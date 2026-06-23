import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

# Preview length for context chunks sent to the LLM
CHUNK_PREVIEW_LENGTH = 200


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract base — swap Ollama for any other LLM backend without changing callers."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the response text."""


# ---------------------------------------------------------------------------
# Ollama implementation
# ---------------------------------------------------------------------------

class OllamaLLMProvider(LLMProvider):
    """Calls a locally running Ollama instance.

    httpx is imported lazily inside complete() so that importing this module
    does not require the library to be installed unless Ollama is actually used.
    Ollama must be running at base_url before any request is made.
    """

    def __init__(self, base_url: str, model_name: str, timeout: int = 60) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout
        logger.info(
            "OllamaLLMProvider configured: model=%s url=%s",
            self._model_name,
            self._base_url,
        )

    def complete(self, prompt: str) -> str:
        import httpx  # lazy import — not needed in tests

        url = f"{self._base_url}/api/generate"
        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
        }
        logger.debug("Sending prompt to Ollama model '%s'.", self._model_name)
        response = httpx.post(url, json=payload, timeout=self._timeout)
        response.raise_for_status()
        answer = response.json()["response"]
        logger.debug("Ollama returned %d chars.", len(answer))
        return answer


# ---------------------------------------------------------------------------
# Fake implementation — for tests (no Ollama, no network, deterministic)
# ---------------------------------------------------------------------------

class FakeLLMProvider(LLMProvider):
    """Returns a fixed answer that includes a [1] citation.

    Lets tests verify the full response shape without a real LLM.
    """

    FIXED_RESPONSE = (
        "Based on the retrieved documents, the information is as follows [1]. "
        "Please refer to the source document for full details."
    )

    def complete(self, prompt: str) -> str:
        return self.FIXED_RESPONSE


# ---------------------------------------------------------------------------
# Module-level provider (lazy initialised on first use)
# ---------------------------------------------------------------------------

_provider: Optional[LLMProvider] = None


def get_provider() -> LLMProvider:
    """Return the active provider, initialising from config if needed."""
    global _provider
    if _provider is None:
        from backend.app.core.config import settings

        if settings.llm_provider == "ollama":
            _provider = OllamaLLMProvider(
                base_url=settings.ollama_base_url,
                model_name=settings.ollama_model_name,
                timeout=settings.llm_timeout_seconds,
            )
        else:
            raise ValueError(
                f"Unknown llm_provider: '{settings.llm_provider}'. "
                "Supported values: 'ollama'."
            )
    return _provider


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_answer(question: str, context_chunks: List[dict]) -> str:
    """Build a RAG prompt and return the LLM's grounded answer.

    Each item in context_chunks must have keys:
      source_id       e.g. "[1]"
      original_filename
      chunk_text

    Returns the fixed no-information message when context_chunks is empty
    so callers don't need to guard against it.
    """
    if not context_chunks:
        return "I could not find relevant information in the uploaded documents."

    prompt = _build_prompt(question, context_chunks)
    return get_provider().complete(prompt)


def _build_prompt(question: str, context_chunks: List[dict]) -> str:
    excerpts = []
    for chunk in context_chunks:
        excerpts.append(
            f"{chunk['source_id']} (from \"{chunk['original_filename']}\"):\n"
            f"{chunk['chunk_text']}"
        )
    context = "\n\n".join(excerpts)

    return (
        "You are a helpful business document assistant.\n\n"
        "Rules:\n"
        "- Answer using ONLY the document excerpts provided below.\n"
        "- Cite sources inline using their reference numbers, e.g. [1] or [2].\n"
        "- If the excerpts do not contain enough information to answer, respond with exactly:\n"
        '  "I could not find relevant information in the uploaded documents."\n'
        "- Keep the answer concise and professional.\n\n"
        "Document excerpts:\n"
        f"{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
