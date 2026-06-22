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

Milestone 2 (current)
- Document upload endpoint with file type validation and local storage.
- `POST /api/documents/upload` — accepts .pdf, .docx, .txt, .md; rejects all others.

Running the backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn backend.app.main:app --reload
```

Test the upload endpoint with curl

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/your/document.pdf"
```

Running tests

```bash
pytest
```

Next steps
- Milestone 3: Text extraction from uploaded documents.

Contact
- Project: KnowFlow AI
