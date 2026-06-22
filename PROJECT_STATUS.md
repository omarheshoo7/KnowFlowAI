# Project Status — KnowFlow AI

Milestone: 4 (Text Chunking)

Summary
- Status: Complete.
- Deliverables: Word-based overlapping chunking service integrated into the upload flow.

What was built
- `backend/app/services/chunking_service.py` — Splits extracted text into overlapping word-based chunks.
- `backend/app/schemas/document.py` — Extended with chunk_count field.
- `backend/app/api/routes/documents.py` — Upload route now calls chunking after successful extraction.
- `backend/tests/test_chunking.py` — 18 new tests (unit + integration).

Chunking behaviour
- Default chunk_size_words=500, chunk_overlap_words=100 (step=400 words).
- Each Chunk carries: chunk_index, text, word_count, character_count.
- Failed extraction → chunk_count=0.
- Upload response message: "Document uploaded, text extracted, and chunked successfully".

Open items
- Decide primary vector DB for v1 (options: Pinecone, Weaviate, FAISS).
- Choose embedding provider (OpenAI or open-source alternative).

Next milestone
- Milestone 5: Embeddings — generate vector embeddings for each chunk and store in a vector database.
