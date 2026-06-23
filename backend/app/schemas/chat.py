from typing import List
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be blank")
        return v.strip()


class CitationSource(BaseModel):
    source_id: str
    document_id: str
    original_filename: str
    file_type: str
    chunk_index: int
    score: float
    chunk_text_preview: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    citations: List[str]
    sources: List[CitationSource]
    retrieval_count: int
