import uuid
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ChunkPoint:
    chunk_index: int
    text: str
    word_count: int
    character_count: int
    embedding: List[float]


@dataclass
class ScoredChunk:
    """A retrieved chunk with its similarity score. Returned by search()."""
    document_id: str
    original_filename: str
    stored_filename: str
    file_type: str
    chunk_index: int
    chunk_text: str
    score: float
    word_count: int
    character_count: int


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class VectorStore(ABC):
    """Abstract interface — swap Qdrant for any other backend without changing callers."""

    @abstractmethod
    def store(
        self,
        document_id: str,
        original_filename: str,
        stored_filename: str,
        file_type: str,
        points: List[ChunkPoint],
    ) -> int:
        """Persist chunk embeddings with metadata. Returns number of vectors stored."""

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[ScoredChunk]:
        """Return up to top_k chunks most similar to query_embedding, ordered by score desc."""


# ---------------------------------------------------------------------------
# Qdrant implementation
# ---------------------------------------------------------------------------

class QdrantVectorStore(VectorStore):
    """Production store backed by a running Qdrant instance.

    qdrant-client is imported lazily inside __init__ so that importing this
    module does not require the library to be present.
    """

    def __init__(
        self,
        url: str,
        collection_name: str,
        vector_size: int,
        distance: str,
    ) -> None:
        from qdrant_client import QdrantClient  # lazy import

        self._client = QdrantClient(url=url)
        self._collection_name = collection_name
        self._vector_size = vector_size
        self._distance = distance
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        distance_map = {
            "Cosine": Distance.COSINE,
            "Dot": Distance.DOT,
            "Euclid": Distance.EUCLID,
        }
        existing = {c.name for c in self._client.get_collections().collections}
        if self._collection_name not in existing:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._vector_size,
                    distance=distance_map.get(self._distance, Distance.COSINE),
                ),
            )
            logger.info("Created Qdrant collection '%s'.", self._collection_name)
        else:
            logger.debug("Qdrant collection '%s' already exists.", self._collection_name)

    def store(
        self,
        document_id: str,
        original_filename: str,
        stored_filename: str,
        file_type: str,
        points: List[ChunkPoint],
    ) -> int:
        from qdrant_client.models import PointStruct

        if not points:
            return 0

        qdrant_points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=point.embedding,
                payload={
                    "document_id": document_id,
                    "original_filename": original_filename,
                    "stored_filename": stored_filename,
                    "file_type": file_type,
                    "chunk_index": point.chunk_index,
                    "chunk_text": point.text,
                    "word_count": point.word_count,
                    "character_count": point.character_count,
                },
            )
            for point in points
        ]
        self._client.upsert(
            collection_name=self._collection_name,
            points=qdrant_points,
        )
        logger.info(
            "Stored %d vectors for '%s' in collection '%s'.",
            len(qdrant_points),
            original_filename,
            self._collection_name,
        )
        return len(qdrant_points)

    def search(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[ScoredChunk]:
        hits = self._client.search(
            collection_name=self._collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
        results = []
        for hit in hits:
            p = hit.payload or {}
            results.append(ScoredChunk(
                document_id=p.get("document_id", ""),
                original_filename=p.get("original_filename", ""),
                stored_filename=p.get("stored_filename", ""),
                file_type=p.get("file_type", ""),
                chunk_index=p.get("chunk_index", 0),
                chunk_text=p.get("chunk_text", ""),
                score=hit.score,
                word_count=p.get("word_count", 0),
                character_count=p.get("character_count", 0),
            ))
        logger.info(
            "Search returned %d results from collection '%s'.",
            len(results),
            self._collection_name,
        )
        return results


# ---------------------------------------------------------------------------
# Fake implementation — for tests (no Docker, no network)
# ---------------------------------------------------------------------------

class FakeVectorStore(VectorStore):
    """In-memory store used in tests.

    Inspect .stored_points and .stored_metadata after calling store()
    to verify what was persisted. search() returns stored entries in
    insertion order with a fixed score of 0.99.
    """

    def __init__(self) -> None:
        self.stored_points: List[ChunkPoint] = []
        self.stored_metadata: List[dict] = []
        # Per-point entries with full metadata — used by search()
        self._entries: List[dict] = []

    def store(
        self,
        document_id: str,
        original_filename: str,
        stored_filename: str,
        file_type: str,
        points: List[ChunkPoint],
    ) -> int:
        self.stored_points.extend(points)
        self.stored_metadata.append(
            {
                "document_id": document_id,
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "file_type": file_type,
            }
        )
        for point in points:
            self._entries.append(
                {
                    "document_id": document_id,
                    "original_filename": original_filename,
                    "stored_filename": stored_filename,
                    "file_type": file_type,
                    "chunk_index": point.chunk_index,
                    "chunk_text": point.text,
                    "word_count": point.word_count,
                    "character_count": point.character_count,
                }
            )
        return len(points)

    def search(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[ScoredChunk]:
        results = []
        for entry in self._entries[:top_k]:
            results.append(ScoredChunk(
                document_id=entry["document_id"],
                original_filename=entry["original_filename"],
                stored_filename=entry["stored_filename"],
                file_type=entry["file_type"],
                chunk_index=entry["chunk_index"],
                chunk_text=entry["chunk_text"],
                score=0.99,
                word_count=entry["word_count"],
                character_count=entry["character_count"],
            ))
        return results


# ---------------------------------------------------------------------------
# Module-level store (lazy initialised on first use)
# ---------------------------------------------------------------------------

_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Return the active store, initialising from config if needed."""
    global _vector_store
    if _vector_store is None:
        from backend.app.core.config import settings

        _vector_store = QdrantVectorStore(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection_name,
            vector_size=settings.vector_size,
            distance=settings.vector_distance,
        )
    return _vector_store


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def store_chunks(
    document_id: str,
    original_filename: str,
    stored_filename: str,
    file_type: str,
    chunks: list,
    embeddings: List[List[float]],
) -> int:
    """Build ChunkPoints from chunks + embeddings and persist them.

    Returns the number of vectors stored (0 for empty inputs).
    chunks is a list of chunking_service.Chunk objects.
    """
    if not chunks or not embeddings:
        return 0

    points = [
        ChunkPoint(
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            word_count=chunk.word_count,
            character_count=chunk.character_count,
            embedding=embedding,
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    return get_vector_store().store(
        document_id=document_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=file_type,
        points=points,
    )


def search_chunks(
    query_embedding: List[float],
    top_k: int,
) -> List[ScoredChunk]:
    """Search for the top_k chunks most similar to query_embedding.

    Returns an empty list when the store is empty or query_embedding is empty.
    """
    if not query_embedding:
        return []
    return get_vector_store().search(query_embedding, top_k)
