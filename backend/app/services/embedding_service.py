import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

# BGE-small-en-v1.5 produces 384-dimensional vectors.
BGE_VECTOR_SIZE = 384


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class EmbeddingProvider(ABC):
    """Abstract base — swap implementations without changing callers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return one embedding vector per input text."""


# ---------------------------------------------------------------------------
# Local provider — sentence-transformers / BAAI/bge-small-en-v1.5
# ---------------------------------------------------------------------------

class LocalBGEProvider(EmbeddingProvider):
    """Runs BAAI/bge-small-en-v1.5 entirely on the local machine.

    sentence-transformers is imported lazily inside __init__ so that simply
    importing this module does not load the library or download a model.
    """

    def __init__(self, model_name: str, batch_size: int = 32) -> None:
        from sentence_transformers import SentenceTransformer  # lazy import
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        self._batch_size = batch_size
        logger.info("Embedding model loaded.")

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors = self._model.encode(
            texts,
            batch_size=self._batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vectors.tolist()


# ---------------------------------------------------------------------------
# Fake provider — for tests (no model download, fast, deterministic)
# ---------------------------------------------------------------------------

class FakeEmbeddingProvider(EmbeddingProvider):
    """Returns fixed-size zero vectors. Never loads a real model.

    Use in tests by patching embedding_service._provider:
        embedding_service._provider = FakeEmbeddingProvider()
    """

    VECTOR_SIZE = BGE_VECTOR_SIZE

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return [[0.1] * self.VECTOR_SIZE for _ in texts]


# ---------------------------------------------------------------------------
# Module-level provider (lazy initialised on first use)
# ---------------------------------------------------------------------------

_provider: Optional[EmbeddingProvider] = None


def get_provider() -> EmbeddingProvider:
    """Return the active provider, initialising it from config if needed."""
    global _provider
    if _provider is None:
        from backend.app.core.config import settings

        if settings.embedding_provider == "local":
            _provider = LocalBGEProvider(
                model_name=settings.embedding_model_name,
                batch_size=settings.embedding_batch_size,
            )
        else:
            raise ValueError(
                f"Unknown embedding_provider: '{settings.embedding_provider}'. "
                "Supported values: 'local'."
            )
    return _provider


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_chunks(chunk_texts: List[str]) -> List[List[float]]:
    """Generate one embedding vector per chunk text.

    Returns an empty list for empty input without touching the provider.
    Vectors are lists of floats — do not include them in API responses.
    """
    if not chunk_texts:
        return []
    embeddings = get_provider().embed(chunk_texts)
    logger.debug("Embedded %d chunks.", len(embeddings))
    return embeddings
