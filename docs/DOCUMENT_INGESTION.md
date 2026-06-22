# Document Ingestion

Supported file types (v1)
- PDF (with text layer), DOCX, TXT

Flow
1. Client uploads file to `POST /documents/upload`.
2. Server validates file type and size, stores raw file in object storage, and creates a metadata record.
3. Extraction worker picks up new records and extracts text content.
4. After extraction, chunking and embedding jobs are enqueued.

Metadata
- `document_id`, `filename`, `uploaded_by`, `uploaded_at`, `source`, `tags`, `status`, `pages`.

Storage
- Raw files: S3-compatible object store
- Metadata: PostgreSQL (or equivalent)
- Vectors: Vector DB

Failure handling
- Keep ingestion audit logs and retry queues for transient failures.
- For unsupported files (images-only PDFs), mark as `needs_manual_processing`.
