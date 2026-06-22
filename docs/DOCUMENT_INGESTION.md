# Document Ingestion

Supported file types (v1)
- PDF (with text layer), DOCX, TXT, Markdown (.md)

Flow (current implementation)
1. Client uploads file to `POST /api/documents/upload`.
2. Server validates file extension (pdf, docx, txt, md — others → HTTP 400).
3. File is saved to `backend/storage/uploads/` with a UUID filename.
4. Text is extracted immediately: PyMuPDF for PDF, python-docx for DOCX, plain read for TXT/MD.
5. Extracted text is split into overlapping word-based chunks (500 words, 100-word overlap).
6. Response includes filename, file_type, extraction_status, text_length, text_preview, chunk_count.

Planned (future milestones)
7. Each chunk is embedded into a vector.
8. Vectors are stored in a vector database for retrieval.

Metadata
- `document_id`, `filename`, `uploaded_by`, `uploaded_at`, `source`, `tags`, `status`, `pages`.

Storage
- Raw files: S3-compatible object store
- Metadata: PostgreSQL (or equivalent)
- Vectors: Vector DB

Failure handling
- Keep ingestion audit logs and retry queues for transient failures.
- For unsupported files (images-only PDFs), mark as `needs_manual_processing`.
