# Product Requirements — KnowFlow AI

Objective
- Build a RAG knowledge-base platform for business documents that returns cited AI answers.

Target users
- Small to mid-sized teams needing searchable internal documentation, contracts, SOPs, and reports.

Core features (v1)
- Secure document upload (PDF/DOCX/TXT) with metadata capture.
- Text extraction (no OCR) and normalization.
- Chunking with overlap, embeddings, and vector indexing.
- FastAPI-based ingestion and QA API endpoints.
- Cited answers referencing source documents and chunk locations.
- Document library listing and basic metadata search.

Non-goals (v1)
- No OCR, no enterprise SSO integrations, and no polished public website in v1.

Success metrics
- 90% of queries return an answer referencing at least one relevant source.
- Average query latency < 1.5s for retrieval; LLM latency excluded.
- Basic security: authenticated access and encryption in transit.

Constraints and assumptions
- Start with hosted managed vector DB for faster time-to-market.
- Use well-known embedding APIs initially.
