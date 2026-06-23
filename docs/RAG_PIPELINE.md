# RAG Pipeline

Overview
- Retrieval-Augmented Generation (RAG) pipeline combines vector retrieval with LLM prompting to produce grounded answers.

Pipeline steps
1. Query normalization and embedding (query encoder).
2. Vector search (top-K) with optional metadata filters.
3. Optional reranking of retrieved chunks (cross-encoder or heuristic scoring).
4. Prompt assembly: include top-N chunks with source metadata and the user question.
5. LLM call for answer generation with explicit instruction to cite sources.
6. Post-processing: extract citations, format answer, attach source list.

Chunking (implemented — Milestone 4)
- Strategy: word-based sliding window.
- Default chunk_size_words=500, chunk_overlap_words=100 (step=400 words, 20% overlap).
- Each chunk carries: chunk_index, text, word_count, character_count.
- Service: `backend/app/services/chunking_service.py`

Embeddings (implemented — Milestone 5)
- Provider architecture: `EmbeddingProvider` ABC → `LocalBGEProvider` / `FakeEmbeddingProvider`.
- Default model: `BAAI/bge-small-en-v1.5` via sentence-transformers (384-dim vectors).
- Lazy model load — only initialised on first real request; tests bypass via `FakeEmbeddingProvider`.
- Service: `backend/app/services/embedding_service.py`
- Config: `embedding_provider`, `embedding_model_name`, `embedding_batch_size` in `core/config.py`.
- Vectors are internal — not exposed in API responses.

Vector storage (implemented — Milestone 6)
- Provider architecture: `VectorStore` ABC → `QdrantVectorStore` / `FakeVectorStore`.
- `QdrantVectorStore` auto-creates collection `knowflow_documents`, upserts one point per chunk.
- Each point stores the 384-dim embedding plus full payload (text, filename, chunk_index, etc.).
- Tests use `FakeVectorStore` — no Docker or network connection required.
- Service: `backend/app/services/vector_store_service.py`
- Config: `qdrant_url`, `qdrant_collection_name`, `vector_size`, `vector_distance` in `core/config.py`.

Retrieval (implemented — Milestone 7)
- Endpoint: `POST /api/search` — accepts `{"query": "...", "top_k": N}`.
- Query text is embedded with the same `LocalBGEProvider` used at ingestion (384-dim BGE-small-en-v1.5).
- `search_chunks(query_embedding, top_k)` calls `VectorStore.search()` and returns `List[ScoredChunk]`.
- `QdrantVectorStore.search()` calls `client.search()` with cosine similarity.
- Results include: document_id, original_filename, file_type, chunk_index, chunk_text, score, word_count, character_count.
- Empty/blank queries → HTTP 422. Empty collection → HTTP 200 with empty results list.
- Tests use `FakeVectorStore.search()` — returns stored entries in insertion order with score 0.99.
- Service: `backend/app/services/vector_store_service.py`
- Schemas: `backend/app/schemas/search.py`
- Route: `backend/app/api/routes/search.py`

Retrieval tuning (planned)
- Tune top_k and minimum score thresholds.
- Consider hybrid search (sparse BM25 + dense) for better recall on short queries.

Answer generation (planned — Milestone 8)
- Feed top-N retrieved chunks + user query into an LLM prompt.
- LLM returns an answer with inline citations referencing source documents.

Citation format
- Inline bracketed citations with document_id and chunk_index, plus a sources array.
