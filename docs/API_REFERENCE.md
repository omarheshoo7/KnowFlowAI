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
  "message": "Document uploaded, text extracted, chunked, and embedded successfully",
  "extraction_status": "success",
  "text_length": 4821,
  "text_preview": "Introduction\n\nThis report covers...",
  "chunk_count": 10,
  "embedding_count": 10
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
  "embedding_count": 0
}
```

Error response — unsupported file type (HTTP 400):
```json
{
  "detail": "Unsupported file type '.png'. Allowed: ['.docx', '.md', '.pdf', '.txt']"
}
```

---

## Planned endpoints

Auth
- `POST /auth/token` — Exchange credentials for access token (TBD auth scheme)

Ingestion
- `GET /documents/{id}` — Get document metadata and extraction status.
- `GET /documents` — List documents with pagination and filters.

Processing
- `POST /documents/{id}/process` — Trigger extraction/chunking/embedding for a document.

Search & QA
- `POST /qa` — Query body: {"query": "...", "filters": {...}, "top_k": 5}. Returns answer, sources, and confidence.
- `POST /search` — Return top-K chunks for a query.

Admin
- `GET /metrics` — Operational metrics (prometheus)
