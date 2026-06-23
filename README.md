# KnowFlow AI

**KnowFlow AI** is a SaaS-style RAG knowledge-base platform for English business documents. It allows users to upload searchable documents, extract text without OCR, split content into overlapping chunks, generate embeddings, and later retrieve cited answers through an AI assistant.

---

**Status:** In active development
**Completed through:** Milestone 9 — SaaS Frontend Dashboard
**Next:** Milestone 10 — Deployment & Portfolio Polish

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
- RAG answer generation — `POST /api/chat` retrieves chunks, builds a grounded prompt, calls a local LLM, returns an answer with inline `[1]` style citations and a sources list
- Provider-based LLM architecture — `OllamaLLMProvider` (default) + `FakeLLMProvider` (tests)
- Empty collection returns a clear "no information found" message; no hallucination
- Full pytest coverage for all completed milestones (115 tests passing)
- SaaS frontend dashboard — Next.js 14 + TypeScript + Tailwind CSS; Upload, Chat, Search panels with loading states, error banners, and empty states; backend health indicator

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
| LLM (answer generation) | Ollama (local, free) — default model `llama3.2:3b` |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |

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
| 8 | RAG Answer Generation with Citations | Complete |
| 9 | SaaS Frontend Dashboard | Complete |
| 10 | Deployment & Portfolio Polish | Planned |

---

## Frontend setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Copy environment variables
cp .env.local.example .env.local
# Edit .env.local if your backend runs on a different port

# 3. Start the development server
npm run dev
# → http://localhost:3000

# 4. (Optional) Production build
npm run build
```

The frontend expects the FastAPI backend at `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_BASE_URL`).

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

---

### `POST /api/chat`

RAG answer generation. Retrieves the most relevant chunks for the question, sends them to a local Ollama LLM with a grounding prompt, and returns a cited answer.

**Request body:**
```json
{
  "question": "What is the refund policy?",
  "top_k": 5
}
```

**Success response (documents uploaded):**
```json
{
  "question": "What is the refund policy?",
  "answer": "Refund requests must be submitted within 30 days of purchase [1]. Items must be in original condition [2].",
  "citations": ["[1]", "[2]"],
  "sources": [
    {
      "source_id": "[1]",
      "document_id": "a3f1c2d4...",
      "original_filename": "policy.pdf",
      "file_type": "pdf",
      "chunk_index": 3,
      "score": 0.87,
      "chunk_text_preview": "Refund requests must be submitted within 30 days..."
    }
  ],
  "retrieval_count": 2
}
```

**No documents uploaded (empty collection):**
```json
{
  "question": "What is the refund policy?",
  "answer": "I could not find relevant information in the uploaded documents.",
  "citations": [],
  "sources": [],
  "retrieval_count": 0
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

# 5. Start Ollama and pull a model (required for /api/chat; not needed for tests)
ollama serve
ollama pull llama3.2:3b
# → API: http://localhost:11434

# 6. Start the backend
PYTHONPATH=. uvicorn backend.app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)

# 7. Run the test suite
# No Docker, no Ollama, no model downloads required — all fakes are used automatically
PYTHONPATH=. pytest
```

> **Tests vs. real use**
> - `pytest` uses `FakeEmbeddingProvider`, `FakeVectorStore`, and `FakeLLMProvider` automatically via `conftest.py`. No external services needed.
> - Real manual use requires Qdrant (Docker) + Ollama running locally.

### Manual end-to-end flow

```bash
# 1. Upload a document
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@your_document.pdf"

# 2. Search for relevant chunks (no LLM)
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "top_k": 5}'

# 3. Ask a question and get a cited AI answer
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?", "top_k": 5}'
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
│   │   │       ├── search.py            # POST /api/search
│   │   │       └── chat.py              # POST /api/chat
│   │   ├── services/
│   │   │   ├── storage_service.py       # File validation and local save
│   │   │   ├── text_extraction_service.py  # PDF/DOCX/TXT/MD extraction
│   │   │   ├── chunking_service.py      # Overlapping word-based chunking
│   │   │   ├── embedding_service.py     # BGE embeddings (local / fake)
│   │   │   ├── vector_store_service.py  # Qdrant store + search (real / fake)
│   │   │   ├── llm_service.py           # Ollama LLM (real / fake)
│   │   │   └── rag_service.py           # RAG pipeline orchestration
│   │   └── schemas/
│   │       ├── document.py              # Upload response model
│   │       ├── search.py                # Search request / result / response
│   │       └── chat.py                  # Chat request / citation / response
│   ├── storage/
│   │   └── uploads/                     # Uploaded files (git-ignored)
│   └── tests/
│       ├── conftest.py                  # Fake providers for all three services
│       ├── test_health.py
│       ├── test_documents.py
│       ├── test_text_extraction.py
│       ├── test_chunking.py
│       ├── test_embeddings.py
│       ├── test_vector_store.py
│       ├── test_search.py
│       └── test_chat.py
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                   # Root layout — Inter font, global styles
│   │   ├── page.tsx                     # Dashboard — tab navigation
│   │   └── globals.css                  # Tailwind base styles
│   ├── components/
│   │   ├── ApiStatus.tsx                # Backend health indicator
│   │   ├── UploadPanel.tsx              # Document upload panel
│   │   ├── ChatPanel.tsx                # AI Q&A panel
│   │   └── SearchPanel.tsx              # Semantic search panel
│   ├── lib/
│   │   └── api.ts                       # Typed fetch wrappers for all endpoints
│   ├── types/
│   │   └── index.ts                     # TypeScript interfaces for API responses
│   ├── .env.local.example               # Copy to .env.local before running
│   └── package.json
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
| RAG pipeline foundations | Upload → extract → chunk → embed → store → search → LLM answer with citations |
| Provider / fake pattern | Swappable implementations (LocalBGE / Fake, Qdrant / Fake, Ollama / Fake) for fast offline tests |
| Test-driven development | 115 passing tests across unit and integration layers, zero real services needed |
| Modular AI engineering | Each concern (storage, extraction, chunking, embeddings, retrieval, LLM) lives in its own service |
| Frontend engineering | Next.js 14 App Router, TypeScript, Tailwind CSS — tabbed dashboard connecting all backend endpoints |
| SaaS product thinking | Structured milestone plan from backend to frontend to deployment |

---

## Roadmap

- **Milestone 10** — Deployment, monitoring, and portfolio polish
