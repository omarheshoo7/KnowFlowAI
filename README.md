# KnowFlow AI

**KnowFlow AI** is a SaaS-style RAG knowledge-base platform for English business documents. It allows users to upload searchable documents, extract text without OCR, split content into overlapping chunks, generate embeddings, and later retrieve cited answers through an AI assistant.

---

**Status:** In active development
**Completed through:** Milestone 7 — Semantic Retrieval
**Next:** Milestone 8 — RAG Answer Generation with Citations

---

## Features completed

- FastAPI backend with health endpoint, CORS, config, and structured logging
- Document upload endpoint with strict file-type validation
- Accepts: `.pdf` (text-native), `.docx`, `.txt`, `.md`
- Rejects: `.jpg`, `.png`, scanned PDFs, and any unsupported extension — HTTP 400
- Local file storage with UUID-based safe filenames
- Text extraction — PyMuPDF for PDF, python-docx for DOCX, plain read for TXT/MD
- Scanned/image-only PDF detection with a clear user-facing message (no OCR in v1)
- Word-based overlapping chunking — 500 words per chunk, 100-word overlap
- Provider-based embedding architecture — `BAAI/bge-small-en-v1.5` (384-dim) via sentence-transformers
- `FakeEmbeddingProvider` for tests — no model download, fast and deterministic
- Qdrant vector store — auto-creates collection, upserts one point per chunk with full payload
- `FakeVectorStore` for tests — in-memory, no Docker or network required
- Semantic search endpoint — `POST /api/search` embeds the query and returns top-K scored chunks
- Input validation: empty/blank queries rejected (HTTP 422), `top_k` clamped 1–20
- Full pytest coverage for all completed milestones (93 tests passing)

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Data validation | Pydantic v2 + pydantic-settings |
| PDF extraction | PyMuPDF (fitz) |
| DOCX extraction | python-docx |
| File uploads | python-multipart |
| Testing | pytest + httpx |
| Embeddings | sentence-transformers / BAAI/bge-small-en-v1.5 |
| Vector database | Qdrant (self-hosted via Docker) |
| Frontend (upcoming) | TBD |

---

## Milestones

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
| 8 | RAG Answer Generation with Citations | **Next** |
| 9 | SaaS Frontend Dashboard | Planned |
| 10 | Deployment & Portfolio Polish | Planned |

---

## API endpoints

### `GET /api/health`

Returns backend health status.

```json
{
  "status": "ok",
  "service": "KnowFlow AI Backend",
  "version": "0.1.0"
}
```

### `POST /api/documents/upload`

Upload a document file (`multipart/form-data`). Validates the file type, saves it locally, extracts text, chunks it, embeds it, and stores vectors in a single call.

**Supported:** `.pdf` (text-native), `.docx`, `.txt`, `.md`

**Example request:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@quarterly_report.pdf"
```

**Success response:**
```json
{
  "filename": "quarterly_report.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "message": "Document uploaded, text extracted, chunked, embedded, and stored successfully",
  "extraction_status": "success",
  "text_length": 18432,
  "text_preview": "Q3 Financial Summary\n\nRevenue grew 14% year-over-year...",
  "chunk_count": 37,
  "embedding_count": 37,
  "stored_vector_count": 37
}
```

**Scanned/image PDF response:**
```json
{
  "filename": "scan.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "message": "This document appears to be scanned or image-based. KnowFlow AI v1 supports searchable documents only.",
  "extraction_status": "failed",
  "text_length": 0,
  "text_preview": "",
  "chunk_count": 0,
  "embedding_count": 0,
  "stored_vector_count": 0
}
```

**Unsupported file type:**
```json
{
  "detail": "Unsupported file type '.png'. Allowed: ['.docx', '.md', '.pdf', '.txt']"
}
```

---

### `POST /api/search`

Semantic search over all stored document chunks. Embeds the query with the same model used at ingestion and returns the top-K most similar chunks with scores.

**Request body:**
```json
{
  "query": "What is the refund policy?",
  "top_k": 5
}
```

- `query` — required, must not be blank
- `top_k` — optional, integer 1–20, default 5

**Success response:**
```json
{
  "query": "What is the refund policy?",
  "top_k": 5,
  "results": [
    {
      "document_id": "a3f1c2d4...",
      "original_filename": "policy.pdf",
      "file_type": "pdf",
      "chunk_index": 3,
      "chunk_text": "Refund requests must be submitted within 30 days...",
      "score": 0.87,
      "word_count": 120,
      "character_count": 700
    }
  ]
}
```

**Empty collection (no documents uploaded yet):**
```json
{
  "query": "What is the refund policy?",
  "top_k": 5,
  "results": []
}
```

**Validation error (blank query):**
```json
{
  "detail": [{"type": "value_error", "loc": ["body", "query"], "msg": "Value error, query must not be blank"}]
}
```

Interactive API docs are available at `http://localhost:8000/docs` when the server is running.

---

## Local setup

```bash
# 1. Clone the repo
git clone https://github.com/omarheshoo7/KnowFlowAI.git
cd KnowFlowAI

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Start Qdrant (required for real uploads and search; not needed for tests)
docker run -p 6333:6333 qdrant/qdrant
# → REST API: http://localhost:6333
# → Dashboard: http://localhost:6333/dashboard

# 5. Start the backend
uvicorn backend.app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)

# 6. Run the test suite (no Docker required — uses FakeVectorStore)
PYTHONPATH=. pytest
```

### Manual end-to-end flow

```bash
# Upload a document
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@your_document.pdf"

# Search for relevant chunks
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "top_k": 5}'
```

---

## Project structure

```
KnowFlowAI/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app, CORS, router registration
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic settings from env vars
│   │   │   └── logging.py               # Stdout logging setup
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py            # GET /api/health
│   │   │       ├── documents.py         # POST /api/documents/upload
│   │   │       └── search.py            # POST /api/search
│   │   ├── services/
│   │   │   ├── storage_service.py       # File validation and local save
│   │   │   ├── text_extraction_service.py  # PDF/DOCX/TXT/MD extraction
│   │   │   ├── chunking_service.py      # Overlapping word-based chunking
│   │   │   ├── embedding_service.py     # BGE embeddings (local / fake)
│   │   │   └── vector_store_service.py  # Qdrant store + search (real / fake)
│   │   └── schemas/
│   │       ├── document.py              # Upload response model
│   │       └── search.py                # Search request / result / response
│   ├── storage/
│   │   └── uploads/                     # Uploaded files (git-ignored)
│   └── tests/
│       ├── conftest.py                  # FakeEmbeddingProvider + FakeVectorStore fixtures
│       ├── test_health.py
│       ├── test_documents.py
│       ├── test_text_extraction.py
│       ├── test_chunking.py
│       ├── test_embeddings.py
│       ├── test_vector_store.py
│       └── test_search.py
├── docs/                                # Architecture and planning docs
├── CLAUDE.md                            # AI assistant project instructions
├── README.md
├── PROJECT_STATUS.md
├── CHANGELOG.md
├── requirements.txt
└── requirements-dev.txt
```

---

## OCR policy

KnowFlow AI v1 supports **searchable/text-native documents only**. Scanned PDFs, screenshots, handwritten documents, and image-based files are intentionally rejected. When a PDF contains no extractable text layer, the API returns a clear message explaining the limitation.

OCR and document-intelligence support may be added in a future version.

---

## What this project demonstrates

| Area | Detail |
|---|---|
| Backend API design | Clean FastAPI structure with separated routes, services, and schemas |
| Document processing | Multi-format text extraction pipeline (PDF, DOCX, TXT, MD) |
| RAG pipeline foundations | Upload → extract → chunk → embed → store → semantic search, end to end |
| Provider / fake pattern | Swappable implementations (LocalBGE / Fake, Qdrant / Fake) enable fast, offline tests |
| Test-driven development | 93 passing tests across unit and integration layers, zero mocking of business logic |
| Modular AI engineering | Each concern (storage, extraction, chunking, embeddings, retrieval) lives in its own service |
| SaaS product thinking | Structured milestone plan from backend to frontend to deployment |

---

## Roadmap

- **Milestone 8** — RAG answer generation: feed retrieved chunks into an LLM and return an answer with inline citations
- **Milestone 9** — SaaS frontend dashboard for document upload, search, and Q&A
- **Milestone 10** — Deployment, monitoring, and portfolio polish
