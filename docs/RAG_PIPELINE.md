# RAG Pipeline

Overview
- Retrieval-Augmented Generation (RAG) pipeline combines vector retrieval with LLM prompting to produce grounded answers.

Pipeline steps
1. Query normalization and embedding (query encoder).
2. Vector search (top-K) with optional metadata filters.
3. Optional reranking of retrieved chunks (cross-encoder or heuristic scoring).
4. Prompt assembly: include top-N chunks with source metadata and the user question.
5. LLM call for answer generation with explicit instruction to cite sources.
6. Post-processing: extract citations, format answer, attach source list.

Chunking guidance
- Chunk size: 500-800 tokens recommended
- Overlap: 20-30% to preserve context

Retrieval tuning
- Start with cosine similarity; tune top_k and score thresholds.
- Consider hybrid search (sparse BM25 + dense) for better recall.

Citation format
- Inline bracketed citations with document id and chunk index, plus a sources array.
