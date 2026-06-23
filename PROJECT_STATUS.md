# Project Status — KnowFlow AI

**Current milestone:** 8 — RAG Answer Generation with Citations — **Complete**
**Next milestone:** 9 — SaaS Frontend Dashboard

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
| 6 | Vector Database / Qdrant | Complete |
| 7 | Semantic Retrieval | Complete |
| 8 | RAG Answer Generation with Citations | **Complete** |
| 9 | SaaS Frontend Dashboard | Next |
| 10 | Deployment & Portfolio Polish | Planned |

---

## Milestone 8 — RAG Answer Generation with Citations (latest)

**Deliverables**
- `backend/app/services/llm_service.py` — `LLMProvider` ABC, `OllamaLLMProvider`, `FakeLLMProvider`, `generate_answer()`, `_build_prompt()`
- `backend/app/services/rag_service.py` — `answer_question()`, `RagSource`, `RagResult`
- `backend/app/schemas/chat.py` — `ChatRequest`, `CitationSource`, `ChatResponse`
- `backend/app/api/routes/chat.py` — `POST /api/chat`
- `backend/app/main.py` — chat router registered
- `backend/app/core/config.py` — extended with `llm_provider`, `ollama_base_url`, `ollama_model_name`, `llm_timeout_seconds`
- `backend/tests/conftest.py` — added `fake_llm_provider` autouse fixture
- `backend/tests/test_chat.py` — 22 new tests; 115 total passing
- `requirements.txt` — added `httpx==0.27.0`

**Behaviour**
- `POST /api/chat` accepts `{"question": "...", "top_k": 5}` (top_k 1–20, default 5)
- Pipeline: embed question → Qdrant top-K search → format numbered context → Ollama prompt → extract `[N]` citations
- Prompt grounds the LLM on retrieved excerpts only; instructs to cite as `[1]`, `[2]`, etc.
- Empty collection or failed embedding → returns "I could not find relevant information in the uploaded documents."
- Tests: `FakeLLMProvider` returns a deterministic response with `[1]` — no Ollama, no network

---

## Milestone 7 — Semantic Retrieval

**Deliverables**
- `backend/app/schemas/search.py` — `SearchRequest`, `SearchResult`, `SearchResponse`
- `backend/app/api/routes/search.py` — `POST /api/search`
- `backend/app/services/vector_store_service.py` — `ScoredChunk`, `search()` on ABC and implementations, `search_chunks()`
- `backend/tests/test_search.py` — 20 new tests; 93 total passing

**Behaviour**
- `POST /api/search` accepts `{"query": "...", "top_k": N}` (top_k 1–20, default 5)
- Empty query or whitespace → HTTP 422; empty collection → HTTP 200 with empty results

---

## Milestone 6 — Vector Database / Qdrant

**Deliverables**
- `backend/app/services/vector_store_service.py` — `VectorStore` ABC, `QdrantVectorStore`, `FakeVectorStore`, `store_chunks()`
- `backend/app/core/config.py` — `qdrant_url`, `qdrant_collection_name`, `vector_size`, `vector_distance`
- `backend/app/schemas/document.py` — `stored_vector_count` field
- `backend/tests/test_vector_store.py` — 13 new tests; 73 total passing

---

## Milestone 5 — Embeddings Foundation

**Deliverables**
- `backend/app/services/embedding_service.py` — `LocalBGEProvider`, `FakeEmbeddingProvider`, `embed_chunks()`
- `backend/tests/test_embeddings.py` — 13 new tests; 60 total passing

---

## Milestone 4 — Text Chunking

**Deliverables**
- `backend/app/services/chunking_service.py` — word-based sliding-window chunking
- `backend/tests/test_chunking.py` — 18 new tests; 47 total passing

---

## Milestone 3 — Text Extraction

**Deliverables**
- `backend/app/services/text_extraction_service.py` — PyMuPDF, python-docx, plain read; scanned PDF detection
- 13 new tests; 29 total passing

---

## Milestone 2 — Document Upload & File Validation

**Deliverables**
- `POST /api/documents/upload` endpoint, extension validation, UUID storage
- 13 new tests; 16 total passing

---

## Milestone 1 — FastAPI Backend Foundation

**Deliverables**
- FastAPI app, CORS, Pydantic settings, logging, `GET /api/health`; 3 tests passing

---

## Milestone 0 — Planning & Documentation

**Deliverables**
- Architecture doc, PRD, RAG pipeline plan, ingestion plan, testing strategy, deployment plan, vector DB comparison, citation strategy
