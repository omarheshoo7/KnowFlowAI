# API Reference

## Implemented endpoints

### GET /api/health
Returns backend health status.

Response:
```json
{
  "status": "ok",
  "service": "KnowFlow AI Backend",
  "version": "0.1.0"
}
```

### POST /api/documents/upload
Upload a document file. Accepts multipart/form-data.

Supported file types: `.pdf`, `.docx`, `.txt`, `.md`

Unsupported types (returns HTTP 400): `.jpg`, `.jpeg`, `.png`, and any other extension.

Example request:
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@report.pdf"
```

Success response — searchable document (HTTP 200):
```json
{
  "filename": "report.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "message": "Document uploaded, text extracted, chunked, embedded, and stored successfully",
  "extraction_status": "success",
  "text_length": 4821,
  "text_preview": "Introduction\n\nThis report covers...",
  "chunk_count": 10,
  "embedding_count": 10,
  "stored_vector_count": 10
}
```

Success response — scanned/image PDF (HTTP 200, extraction failed):
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

Error response — unsupported file type (HTTP 400):
```json
{
  "detail": "Unsupported file type '.png'. Allowed: ['.docx', '.md', '.pdf', '.txt']"
}
```

### POST /api/search

Semantic search over stored document chunks. Embeds the query using the same model used at ingestion, runs top-K cosine search against Qdrant, and returns scored chunks. No LLM answer generation.

Request body:
```json
{
  "query": "What is the refund policy?",
  "top_k": 5
}
```

- `query` — required string, must not be blank
- `top_k` — optional integer 1–20, default 5

Success response (HTTP 200):
```json
{
  "query": "What is the refund policy?",
  "top_k": 5,
  "results": [
    {
      "document_id": "a3f1c2d4e5f6...",
      "original_filename": "policy.pdf",
      "file_type": "pdf",
      "chunk_index": 3,
      "chunk_text": "Refund requests must be submitted within 30 days of purchase...",
      "score": 0.87,
      "word_count": 120,
      "character_count": 700
    }
  ]
}
```

Empty collection response (HTTP 200):
```json
{
  "query": "What is the refund policy?",
  "top_k": 5,
  "results": []
}
```

Validation error — blank query (HTTP 422):
```json
{
  "detail": [{"type": "value_error", "loc": ["body", "query"], "msg": "Value error, query must not be blank"}]
}
```

### POST /api/chat

RAG answer generation. Retrieves top-K chunks, builds a grounded prompt, calls a local Ollama LLM, and returns a cited answer.

Request body:
```json
{
  "question": "What is the refund policy?",
  "top_k": 5
}
```

- `question` — required, must not be blank
- `top_k` — optional integer 1–20, default 5

Success response with documents (HTTP 200):
```json
{
  "question": "What is the refund policy?",
  "answer": "Refunds must be requested within 30 days of purchase [1].",
  "citations": ["[1]"],
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
  "retrieval_count": 1
}
```

Empty collection response (HTTP 200):
```json
{
  "question": "What is the refund policy?",
  "answer": "I could not find relevant information in the uploaded documents.",
  "citations": [],
  "sources": [],
  "retrieval_count": 0
}
```

---

## Planned endpoints

Auth
- `POST /auth/token` — Exchange credentials for access token (TBD auth scheme)

Ingestion
- `GET /documents/{id}` — Get document metadata and extraction status.
- `GET /documents` — List documents with pagination and filters.

Admin
- `GET /metrics` — Operational metrics (prometheus)
