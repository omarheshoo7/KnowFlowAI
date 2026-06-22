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

Chunking (implemented — Milestone 4)
- Strategy: word-based sliding window.
- Default chunk_size_words=500, chunk_overlap_words=100 (step=400 words, 20% overlap).
- Each chunk carries: chunk_index, text, word_count, character_count.
- Service: `backend/app/services/chunking_service.py`

Retrieval tuning
- Start with cosine similarity; tune top_k and score thresholds.
- Consider hybrid search (sparse BM25 + dense) for better recall.

Citation format
- Inline bracketed citations with document id and chunk index, plus a sources array.
