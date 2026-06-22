# Citation Strategy

Goals
- Provide transparent, auditable answers that reference sources.

Citation model
- Inline citations: use bracketed references like `[doc:123#chunk:5]` inline.
- Sources array: return structured metadata for each cited chunk (document id, filename, page range, snippet).

Generation rules
- Only cite chunks actually used in prompt context.
- Prefer the highest-scoring chunks but avoid redundant citations.
- Include confidence and optionally a provenance score.

User-facing
- Link citations to the document viewer with highlighted chunk ranges.
- Allow users to inspect the original text and jump to source.
