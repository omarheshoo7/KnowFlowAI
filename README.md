# KnowFlow AI

KnowFlow AI is a full-stack Retrieval-Augmented Generation (RAG) knowledge-base platform for searchable business documents.

Vision
- Help teams search and get cited AI answers over their business documents.
- Make knowledge discovery fast, accurate, and auditable.

v1 Scope (Milestone 0 → v0.1)
- No OCR in v1 — only documents with an extractable text layer (PDF text, DOCX, TXT).
- Document upload and secure storage.
- Text extraction, chunking, embedding generation, and vector search.
- FastAPI backend with a well-defined API for ingestion and QA flows.
- Cited AI answers that reference source documents.

What's in this repo

Milestone 0
- Documentation and planning: architecture, PRD, RAG pipeline, ingestion, testing, deployment plan.

Milestone 1
- FastAPI backend scaffold with health endpoint, CORS, config, and logging.
- `GET /api/health` → `{ "status": "ok", "service": "...", "version": "..." }`

Milestone 2
- Document upload endpoint with file type validation and local storage.
- `POST /api/documents/upload` — accepts .pdf, .docx, .txt, .md; rejects all others.

Milestone 3
- Text extraction integrated into the upload flow.
- Searchable PDFs, DOCX, TXT, and MD return extracted text on upload.
- Scanned/image PDFs are detected and rejected with a clear message (no OCR).
- Response includes `extraction_status`, `text_length`, and `text_preview`.

Milestone 4 (current)
- Extracted text is split into overlapping word-based chunks.
- Default: 500 words per chunk, 100-word overlap between chunks.
- Response now includes `chunk_count`.

Running the backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn backend.app.main:app --reload
```

Test the upload → extract → chunk pipeline

```bash
# Upload a text file and see chunk_count in the response
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/notes.txt"

# Interactive API docs
open http://localhost:8000/docs
```

Running tests

```bash
pytest
```

Next steps
- Milestone 5: Embeddings — generate vector embeddings for each chunk.

Contact
- Project: KnowFlow AI
