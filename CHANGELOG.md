# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - Milestone 9 — SaaS Frontend Dashboard
- Added `frontend/` — Next.js 14 App Router project with TypeScript and Tailwind CSS.
- Added `frontend/app/layout.tsx` — root layout with Inter font and global Tailwind styles.
- Added `frontend/app/page.tsx` — dashboard page with sticky header and Upload / Chat / Search tab navigation.
- Added `frontend/components/ApiStatus.tsx` — polls `GET /api/health` on mount; shows online/offline dot and backend version.
- Added `frontend/components/UploadPanel.tsx` — drag-and-drop file zone; validates extension client-side; displays chunk_count, embedding_count, stored_vector_count, text_preview, extraction_status.
- Added `frontend/components/ChatPanel.tsx` — textarea + top-k input; calls `POST /api/chat`; renders grounded answer, citation badges, and per-source text previews with score.
- Added `frontend/components/SearchPanel.tsx` — search bar + top-k input; calls `POST /api/search`; renders result cards with similarity progress bar, word count, char count.
- Added `frontend/lib/api.ts` — typed `fetch` wrappers for health, upload, search, and chat endpoints.
- Added `frontend/types/index.ts` — TypeScript interfaces for `HealthResponse`, `UploadResponse`, `SearchResponse`, `ChatResponse`, `CitationSource`, `SearchResult`.
- Added `frontend/package.json`, `tsconfig.json`, `next.config.js`, `tailwind.config.ts`, `postcss.config.js`, `.eslintrc.json`.
- Added `frontend/.env.local.example` — documents `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.
- `npm run build` passes clean — zero TypeScript and ESLint errors.
- Backend 115 tests unaffected (still all passing).

## [0.9.0] - Milestone 8 — RAG Answer Generation with Citations
- Added `llm_service.py` with `LLMProvider` ABC, `OllamaLLMProvider`, `FakeLLMProvider`, and `generate_answer()`.
- Added `rag_service.py` — orchestrates embed → search → format context → generate → extract citations.
- Added `POST /api/chat` endpoint in `backend/app/api/routes/chat.py`.
- Added `ChatRequest`, `CitationSource`, `ChatResponse` schemas in `backend/app/schemas/chat.py`.
- Extended `config.py` with `llm_provider`, `ollama_base_url`, `ollama_model_name`, `llm_timeout_seconds`.
- Extended `conftest.py` with `fake_llm_provider` autouse fixture — no Ollama required for tests.
- Added `httpx==0.27.0` to `requirements.txt` (used by `OllamaLLMProvider`).
- `OllamaLLMProvider` calls `POST /api/generate` on a local Ollama instance with `stream: false`.
- `FakeLLMProvider` returns a deterministic response containing `[1]` for citation extraction.
- Empty retrieval returns the fixed message: "I could not find relevant information in the uploaded documents."
- LLM prompt instructs the model to cite sources as `[1]`, `[2]`, etc.; answer grounded on retrieved chunks only.
- Citations are extracted from the answer text via `re.findall(r"\[\d+\]", answer)`.
- Added 22 new tests (schema, unit, integration); 115 total, all passing.
- Updated CLAUDE.md, PROJECT_STATUS.md, CHANGELOG.md, README.md, docs/.

## [0.8.0] - Milestone 7 — Semantic Retrieval
- Added `POST /api/search` endpoint: embeds query with `LocalBGEProvider`, runs top-K cosine search, returns scored chunks.
- Added `backend/app/schemas/search.py` — `SearchRequest` (query, top_k 1–20), `SearchResult`, `SearchResponse`.
- Added `backend/app/api/routes/search.py` and registered at `/api/search` in `main.py`.
- Extended `VectorStore` ABC with `search(query_embedding, top_k) → List[ScoredChunk]`.
- Added `ScoredChunk` dataclass to `vector_store_service.py`.
- `QdrantVectorStore.search()` calls `client.search()` and maps `ScoredPoint` payloads to `ScoredChunk`.
- `FakeVectorStore.search()` returns stored entries in insertion order with score 0.99 — no Docker needed.
- `FakeVectorStore.store()` now also populates `_entries` list for per-point metadata lookups.
- Added `search_chunks()` public function to `vector_store_service.py`.
- Added 20 new tests (schema, unit, integration); 93 total, all passing.
- Updated CLAUDE.md, PROJECT_STATUS.md, CHANGELOG.md, README.md, docs/.

## [0.7.0] - Milestone 6 — Vector Database / Qdrant
- Added `vector_store_service` with `VectorStore` ABC, `QdrantVectorStore`, and `FakeVectorStore`.
- `QdrantVectorStore` auto-creates the Qdrant collection and upserts one point per chunk with full payload.
- `FakeVectorStore` is an in-memory store used in tests — no Docker or network required.
- Extended `config.py` with `qdrant_url`, `qdrant_collection_name`, `vector_size`, `vector_distance`.
- Extended `DocumentUploadResponse` schema with `stored_vector_count`.
- Upload route calls `store_chunks` after embedding; message updated to include "stored".
- Extended `conftest.py` with `fake_vector_store_provider` autouse fixture.
- Added `qdrant-client==1.9.1` to requirements.txt.
- Added 13 new tests (unit + integration); 73 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.6.0] - Milestone 5 — Embeddings Foundation
- Added `embedding_service` with provider-based architecture.
- `LocalBGEProvider` wraps sentence-transformers / BAAI/bge-small-en-v1.5 (384-dim, lazy import).
- `FakeEmbeddingProvider` provides deterministic zero vectors for tests — no model download.
- `conftest.py` auto-patches all tests to use `FakeEmbeddingProvider` via `autouse` fixture.
- Extended `config.py` with `embedding_provider`, `embedding_model_name`, `embedding_batch_size`.
- Extended `DocumentUploadResponse` schema with `embedding_count`.
- Upload route now embeds chunks after chunking; `embedding_count` included in response.
- Upload success message updated to include "embedded".
- Added `sentence-transformers==3.0.1` to requirements.txt.
- Added 13 new tests (unit + integration); 60 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.5.0] - Milestone 4 — Text Chunking
- Added `chunking_service` with word-based overlapping chunk splitting.
- Default: chunk_size_words=500, chunk_overlap_words=100 (step=400).
- Each chunk carries chunk_index, text, word_count, character_count.
- Extended `DocumentUploadResponse` schema with `chunk_count`.
- Upload route calls chunking after successful extraction; chunk_count=0 on failure.
- Upload success message updated to include "chunked".
- Added 18 new tests (unit + integration); 47 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.4.0] - Milestone 3 — Text Extraction
- Added `text_extraction_service` supporting PDF (PyMuPDF/fitz), DOCX (python-docx), TXT, and Markdown.
- Scanned/image-based PDFs are detected and return a clear rejection message instead of empty text.
- Extended `DocumentUploadResponse` schema with `extraction_status`, `text_length`, and `text_preview`.
- Upload endpoint now extracts text immediately after saving the file.
- `text_preview` is capped at 300 characters.
- Added `pymupdf==1.24.5` and `python-docx==1.1.2` to requirements.txt.
- Added 13 new tests (unit + integration); 29 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.3.0] - Milestone 2 — Document Upload and File Validation
- Added `POST /api/documents/upload` endpoint.
- Added extension validation — accepts .pdf, .docx, .txt, .md; rejects all others with HTTP 400.
- Added `StorageService` that saves uploads to `backend/storage/uploads/` with UUID-based filenames.
- Added `DocumentUploadResponse` Pydantic schema.
- Added `python-multipart` dependency for multipart file uploads.
- Added `.gitignore` rule to exclude uploaded files but track the uploads folder.
- Added 13 pytest tests covering all success and rejection cases (16 total, all passing).

## [0.2.0] - Milestone 1 — Backend Foundation
- Created FastAPI backend scaffold under `backend/`.
- Added `GET /api/health` endpoint returning status, service name, and version.
- Added CORS middleware with configurable allowed origins.
- Added Pydantic settings loaded from environment variables.
- Added basic stdout logging setup.
- Added `requirements.txt`, `requirements-dev.txt`, and `.env.example`.
- Added pytest test suite covering the health endpoint.

## [0.1.0] - Milestone 0 — Documentation scaffold
- Created project documentation and planning structure.
- Added PRD, architecture, RAG pipeline, ingestion, vector DB, and testing strategy docs.
