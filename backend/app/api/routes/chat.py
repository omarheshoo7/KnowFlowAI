import logging
from fastapi import APIRouter

from backend.app.schemas.chat import ChatRequest, ChatResponse, CitationSource
from backend.app.services import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """RAG answer generation endpoint.

    Retrieves the most relevant document chunks for the question, sends them
    to the configured LLM with a grounding prompt, and returns the answer
    with inline citations and a source list.

    No real LLM or Qdrant connection is required to run the test suite —
    tests use FakeLLMProvider and FakeVectorStore via conftest.py fixtures.
    """
    logger.info("Chat request: question=%r top_k=%d", request.question, request.top_k)

    result = rag_service.answer_question(
        question=request.question,
        top_k=request.top_k,
    )

    return ChatResponse(
        question=result.question,
        answer=result.answer,
        citations=result.citations,
        sources=[
            CitationSource(
                source_id=src.source_id,
                document_id=src.document_id,
                original_filename=src.original_filename,
                file_type=src.file_type,
                chunk_index=src.chunk_index,
                score=src.score,
                chunk_text_preview=src.chunk_text_preview,
            )
            for src in result.sources
        ],
        retrieval_count=result.retrieval_count,
    )
