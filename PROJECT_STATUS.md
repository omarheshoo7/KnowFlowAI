# Project Status — KnowFlow AI

**Current milestone:** 6 — Vector Database / Qdrant — **Complete**
**Next milestone:** 7 — Semantic Retrieval

---

## All milestones

| # | Name | Status |
|---|---|---|
| 0 | Planning & Documentation | Complete |
| 1 | FastAPI Backend Foundation | Complete |
| 2 | Document Upload & File Validation | Complete |
| 3 | Text Extraction | Complete |
| 4 | Text Chunking | Complete |
| 5 | Embeddings Foundation | Complete |
| 6 | Vector Database / Qdrant | **Complete** |
| 7 | Semantic Retrieval | Next |
| 8 | RAG Answer Generation with Citations | Planned |
| 9 | SaaS Frontend Dashboard | Planned |
| 10 | Deployment & Portfolio Polish | Planned |

---

## Milestone 6 — Vector Database / Qdrant (latest)

**Deliverables**
- `backend/app/services/vector_store_service.py` — `VectorStore` ABC, `QdrantVectorStore`, `FakeVectorStore`, `store_chunks()` public function
- `backend/app/core/config.py` — extended with `qdrant_url`, `qdrant_collection_name`, `vector_size`, `vector_distance`
- `backend/app/schemas/document.py` — extended with `stored_vector_count` field
- `backend/app/api/routes/documents.py` — calls `store_chunks` after embedding; returns `stored_vector_count`
- `backend/tests/conftest.py` — added `fake_vector_store_provider` autouse fixture
- `backend/tests/test_vector_store.py` — 13 new tests (unit + integration); 73 total passing
- `qdrant-client==1.9.1` added to requirements.txt

**Behaviour**
- `QdrantVectorStore` creates the collection if it doesn't exist, then upserts one PointStruct per chunk
- Each point: UUID id, 384-dim vector, payload with document_id/filename/file_type/chunk_index/chunk_text/word_count/character_count
- Tests: `FakeVectorStore` — in-memory list, no Docker or network
- Failed extraction → stored_vector_count=0

---

## Milestone 5 — Embeddings Foundation

**Deliverables**
- `backend/app/services/embedding_service.py` — provider-based architecture with `LocalBGEProvider`, `FakeEmbeddingProvider`, and `embed_chunks()` public function
- `backend/app/core/config.py` — extended with `embedding_provider`, `embedding_model_name`, `embedding_batch_size`
- `backend/app/schemas/document.py` — extended with `embedding_count` field
- `backend/app/api/routes/documents.py` — calls embedding after chunking; returns `embedding_count`
- `backend/tests/conftest.py` — session `autouse` fixture patches all tests to use `FakeEmbeddingProvider`
- `backend/tests/test_embeddings.py` — 13 new tests (unit + integration); 60 total passing
- `sentence-transformers==3.0.1` added to requirements.txt

**Behaviour**
- Default provider: `LocalBGEProvider` using `BAAI/bge-small-en-v1.5` (384-dim vectors)
- Tests: `FakeEmbeddingProvider` — returns `[0.1] * 384` per chunk, zero model load, deterministic
- Failed extraction → embedding_count=0
- Vectors are internal — not included in API responses

---

## Milestone 4 — Text Chunking

**Deliverables**
- `backend/app/services/chunking_service.py` — word-based sliding-window chunking with configurable size and overlap
- `backend/app/schemas/document.py` — extended with `chunk_count` field
- `backend/app/api/routes/documents.py` — calls chunking after successful extraction
- `backend/tests/test_chunking.py` — 18 new tests (unit + integration); 47 total passing

**Behaviour**
- Default: chunk_size_words=500, chunk_overlap_words=100 (step=400 words, 20% overlap)
- Each `Chunk` carries: chunk_index, text, word_count, character_count
- Failed extraction → chunk_count=0
- Success message: "Document uploaded, text extracted, and chunked successfully"

---

## Milestone 3 — Text Extraction

**Deliverables**
- `backend/app/services/text_extraction_service.py` — PyMuPDF for PDF, python-docx for DOCX, plain read for TXT/MD
- Scanned/blank PDF detection → clear OCR rejection message
- Response fields: extraction_status, text_length, text_preview (capped at 300 chars)
- 13 new tests; 29 total passing at completion

---

## Milestone 2 — Document Upload & File Validation

**Deliverables**
- `POST /api/documents/upload` endpoint
- Extension validation — accepts .pdf, .docx, .txt, .md; rejects others with HTTP 400
- `StorageService` saves files to `backend/storage/uploads/` with UUID filenames
- 13 new tests; 16 total passing at completion

---

## Milestone 1 — FastAPI Backend Foundation

**Deliverables**
- FastAPI app with CORS middleware, Pydantic settings, and stdout logging
- `GET /api/health` endpoint
- pytest setup; 3 tests passing

---

## Milestone 0 — Planning & Documentation

**Deliverables**
- Architecture doc, PRD, RAG pipeline plan, ingestion plan, testing strategy, deployment plan, vector DB comparison, citation strategy

---

## Open decisions

- Confirm embedding model for Milestone 5 (local BGE via sentence-transformers is the current plan)
- Confirm vector DB for Milestone 6 (Qdrant is the current plan)
