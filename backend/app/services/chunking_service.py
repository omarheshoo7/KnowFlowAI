import logging
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE_WORDS = 500
DEFAULT_CHUNK_OVERLAP_WORDS = 100


@dataclass
class Chunk:
    chunk_index: int
    text: str
    word_count: int
    character_count: int


def chunk_text(
    text: str,
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> List[Chunk]:
    """Split text into overlapping word-based chunks.

    Returns an empty list for blank/empty input.
    Raises ValueError if overlap >= chunk_size.
    """
    if chunk_overlap_words >= chunk_size_words:
        raise ValueError(
            f"chunk_overlap_words ({chunk_overlap_words}) must be less than "
            f"chunk_size_words ({chunk_size_words})"
        )

    words = text.split() if text else []
    if not words:
        return []

    step = chunk_size_words - chunk_overlap_words
    chunks: List[Chunk] = []
    start = 0

    while start < len(words):
        chunk_words = words[start : start + chunk_size_words]
        chunk_text_str = " ".join(chunk_words)
        chunks.append(
            Chunk(
                chunk_index=len(chunks),
                text=chunk_text_str,
                word_count=len(chunk_words),
                character_count=len(chunk_text_str),
            )
        )
        start += step

    logger.debug("Chunked %d words into %d chunks", len(words), len(chunks))
    return chunks
