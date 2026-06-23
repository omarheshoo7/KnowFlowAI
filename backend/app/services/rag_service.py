import re
import logging
from dataclasses import dataclass
from typing import List

from backend.app.services import embedding_service, vector_store_service, llm_service

logger = logging.getLogger(__name__)

# How many characters of a chunk to include as the preview in sources
PREVIEW_LENGTH = 200


# ---------------------------------------------------------------------------
# Data model returned by answer_question()
# ---------------------------------------------------------------------------

@dataclass
class RagSource:
    source_id: str          # "[1]", "[2]", …
    document_id: str
    original_filename: str
    file_type: str
    chunk_index: int
    score: float
    chunk_text_preview: str


@dataclass
class RagResult:
    question: str
    answer: str
    citations: List[str]    # e.g. ["[1]", "[2]"]
    sources: List[RagSource]
    retrieval_count: int


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def answer_question(question: str, top_k: int = 5) -> RagResult:
    """Full RAG pipeline: embed → search → format context → generate → extract citations.

    Returns a no-information RagResult when the collection is empty or the
    query cannot be embedded.
    """
    logger.info("RAG pipeline started: question=%r top_k=%d", question, top_k)

    # 1. Embed the question
    query_embeddings = embedding_service.embed_chunks([question])
    if not query_embeddings:
        logger.warning("Embedding returned empty list for question=%r", question)
        return _empty_result(question)

    # 2. Retrieve top-K chunks
    scored_chunks = vector_store_service.search_chunks(
        query_embedding=query_embeddings[0],
        top_k=top_k,
    )

    if not scored_chunks:
        logger.info("No chunks retrieved for question=%r", question)
        return _empty_result(question)

    # 3. Build citation sources (numbered [1], [2], …)
    sources = [
        RagSource(
            source_id=f"[{i + 1}]",
            document_id=sc.document_id,
            original_filename=sc.original_filename,
            file_type=sc.file_type,
            chunk_index=sc.chunk_index,
            score=sc.score,
            chunk_text_preview=sc.chunk_text[:PREVIEW_LENGTH],
        )
        for i, sc in enumerate(scored_chunks)
    ]

    # 4. Build context dicts for the LLM prompt
    context_chunks = [
        {
            "source_id": src.source_id,
            "original_filename": src.original_filename,
            "chunk_text": sc.chunk_text,
        }
        for src, sc in zip(sources, scored_chunks)
    ]

    # 5. Generate grounded answer
    answer = llm_service.generate_answer(question, context_chunks)

    # 6. Extract citation references actually mentioned in the answer
    citations = sorted(set(re.findall(r"\[\d+\]", answer)))

    logger.info(
        "RAG pipeline complete: %d sources retrieved, %d citations in answer.",
        len(sources),
        len(citations),
    )

    return RagResult(
        question=question,
        answer=answer,
        citations=citations,
        sources=sources,
        retrieval_count=len(scored_chunks),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_result(question: str) -> RagResult:
    return RagResult(
        question=question,
        answer="I could not find relevant information in the uploaded documents.",
        citations=[],
        sources=[],
        retrieval_count=0,
    )
