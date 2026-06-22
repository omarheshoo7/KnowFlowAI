# Project Status — KnowFlow AI

Milestone: 2 (Document Upload and File Validation)

Summary
- Status: Complete.
- Deliverables: POST /api/documents/upload endpoint with extension validation and local file storage.

What was built
- `backend/app/api/routes/documents.py` — POST /api/documents/upload route.
- `backend/app/services/storage_service.py` — Extension validation and safe local file save.
- `backend/app/schemas/document.py` — DocumentUploadResponse Pydantic schema.
- `backend/storage/uploads/` — Local upload directory (contents git-ignored).
- `backend/tests/test_documents.py` — 13 tests covering success and rejection cases.
- Added `python-multipart` to requirements.txt.

Supported file types: .pdf, .docx, .txt, .md
Rejected file types: .jpg, .jpeg, .png, and any unsupported extension.

Open items
- Decide primary vector DB for v1 (options: Pinecone, Weaviate, FAISS).
- Choose embedding provider (OpenAI or open-source alternative).

Next milestone
- Milestone 3: Text extraction from uploaded documents (PDF, DOCX, TXT, MD).
