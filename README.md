# KnowFlow AI

**KnowFlow AI** is a SaaS-style RAG knowledge-base platform for English business documents. It allows users to upload searchable documents, extract text without OCR, split content into overlapping chunks, generate embeddings, and later retrieve cited answers through an AI assistant.

---

**Status:** In active development
**Completed through:** Milestone 4 — Text Chunking
**Next:** Milestone 5 — Embeddings Foundation

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
- Full pytest coverage for all completed milestones (47 tests passing)

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
| Embeddings (upcoming) | sentence-transformers / BGE |
| Vector database (upcoming) | Qdrant |
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
| 5 | Embeddings Foundation | **Next** |
| 6 | Vector Database / Qdrant | Planned |
| 7 | Semantic Retrieval | Planned |
| 8 | RAG Answer Generation with Citations | Planned |
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

Upload a document file (`multipart/form-data`). Validates the file type, saves it locally, extracts text, and splits it into chunks in a single call.

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
  "message": "Document uploaded, text extracted, and chunked successfully",
  "extraction_status": "success",
  "text_length": 18432,
  "text_preview": "Q3 Financial Summary\n\nRevenue grew 14% year-over-year...",
  "chunk_count": 37
}
```

**Scanned/image PDF response:**
```json
{
  "filename": "scan.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "message": "This document appears to be scanned or image-based. KnowFlow AI v1 supports searchable documents only. OCR/document intelligence support may be added in a future version.",
  "extraction_status": "failed",
  "text_length": 0,
  "text_preview": "",
  "chunk_count": 0
}
```

**Unsupported file type:**
```json
{
  "detail": "Unsupported file type '.png'. Allowed: ['.docx', '.md', '.pdf', '.txt']"
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

# 4. Start the backend
uvicorn backend.app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)

# 5. Run the test suite
pytest
```

---

## Project structure

```
KnowFlowAI/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, router registration
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings from env vars
│   │   │   └── logging.py           # Stdout logging setup
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py        # GET /api/health
│   │   │       └── documents.py     # POST /api/documents/upload
│   │   ├── services/
│   │   │   ├── storage_service.py   # File validation and local save
│   │   │   ├── text_extraction_service.py  # PDF/DOCX/TXT/MD extraction
│   │   │   └── chunking_service.py  # Overlapping word-based chunking
│   │   └── schemas/
│   │       └── document.py          # Pydantic response models
│   ├── storage/
│   │   └── uploads/                 # Uploaded files (git-ignored)
│   └── tests/
│       ├── test_health.py
│       ├── test_documents.py
│       ├── test_text_extraction.py
│       └── test_chunking.py
├── docs/                            # Architecture and planning docs
├── CLAUDE.md                        # AI assistant project instructions
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
| RAG pipeline foundations | Text chunking with overlap, ready for embedding and vector retrieval |
| Test-driven development | 47 passing tests across unit and integration layers |
| Modular AI engineering | Each concern (storage, extraction, chunking) lives in its own service module |
| SaaS product thinking | Structured milestone plan from backend to frontend to deployment |

---

## Roadmap

- **Milestone 5** — Generate vector embeddings for each chunk using local BGE embeddings (sentence-transformers)
- **Milestone 6** — Store and query vectors with Qdrant vector database
- **Milestone 7** — Semantic retrieval endpoint: query → top-K relevant chunks
- **Milestone 8** — RAG answer generation with inline citations referencing source documents
- **Milestone 9** — SaaS frontend dashboard for document upload, search, and Q&A
- **Milestone 10** — Deployment, monitoring, and portfolio polish
