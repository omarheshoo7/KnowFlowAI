# API Reference (planned)

This file outlines the planned FastAPI endpoints for v1.

Auth
- `POST /auth/token` — Exchange credentials for access token (TBD auth scheme)

Ingestion
- `POST /documents/upload` — Upload a document file (multipart). Returns document id and status.
- `GET /documents/{id}` — Get document metadata and extraction status.
- `GET /documents` — List documents with pagination and filters.

Processing
- `POST /documents/{id}/process` — Trigger extraction/chunking/embedding for a document.

Search & QA
- `POST /qa` — Query body: {"query": "...", "filters": {...}, "top_k": 5}. Returns answer, sources, and confidence.
- `POST /search` — Return top-K chunks for a query.

Admin
- `GET /health` — System health
- `GET /metrics` — Operational metrics (prometheus)

Notes
- All responses include trace IDs for auditability.
- API will support pagination, filtering, and RBAC enforced via middleware.
