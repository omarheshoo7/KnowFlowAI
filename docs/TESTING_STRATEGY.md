# Testing Strategy

Test types
- Unit tests: extraction, chunking logic, API handlers.
- Integration tests: ingestion → extraction → embedding → vector insert.
- E2E tests: upload a document and run a QA query to verify citations.
- Data tests: check for vector dimensionality, missing metadata, and duplicate vectors.

Quality gates
- Run unit tests and linters on PRs.
- Integration tests in CI against a test vector DB (small dataset).

Evaluation
- Relevance metrics: MRR/Recall@K on a labeled QA dataset.
- Human evaluation for citation quality and answer correctness.
