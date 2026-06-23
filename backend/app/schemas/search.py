from typing import List
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank")
        return v.strip()


class SearchResult(BaseModel):
    document_id: str
    original_filename: str
    file_type: str
    chunk_index: int
    chunk_text: str
    score: float
    word_count: int
    character_count: int


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]
