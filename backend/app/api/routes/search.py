import logging
from fastapi import APIRouter

from backend.app.schemas.search import SearchRequest, SearchResponse, SearchResult
from backend.app.services import embedding_service, vector_store_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest) -> SearchResponse:
    """Semantic search over stored document chunks.

    Embeds the query using the same model used at ingestion time, then
    queries Qdrant for the top_k most similar chunks. Returns scored
    chunks with full metadata — no LLM answer generation.
    """
    logger.info("Search request: query=%r top_k=%d", request.query, request.top_k)

    query_embeddings = embedding_service.embed_chunks([request.query])
    if not query_embeddings:
        return SearchResponse(query=request.query, top_k=request.top_k, results=[])

    scored_chunks = vector_store_service.search_chunks(
        query_embedding=query_embeddings[0],
        top_k=request.top_k,
    )

    results = [
        SearchResult(
            document_id=sc.document_id,
            original_filename=sc.original_filename,
            file_type=sc.file_type,
            chunk_index=sc.chunk_index,
            chunk_text=sc.chunk_text,
            score=sc.score,
            word_count=sc.word_count,
            character_count=sc.character_count,
        )
        for sc in scored_chunks
    ]

    logger.info("Search returned %d results.", len(results))
    return SearchResponse(query=request.query, top_k=request.top_k, results=results)
