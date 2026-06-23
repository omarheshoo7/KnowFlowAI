import io
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.chat import ChatRequest
from backend.app.services.llm_service import FakeLLMProvider
import backend.app.services.llm_service as llm_service
import backend.app.services.storage_service as storage_service

client = TestClient(app)

NO_INFO_MESSAGE = "I could not find relevant information in the uploaded documents."


# ---------------------------------------------------------------------------
# Helper — redirect uploads to tmp_path so no files land on disk
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path):
    with patch.object(storage_service, "UPLOAD_DIR", tmp_path):
        yield


def _upload_txt(content: str = "word " * 600):
    return client.post(
        "/api/documents/upload",
        files={"file": ("doc.txt", io.BytesIO(content.encode()), "text/plain")},
    )


def _chat(question: str = "What is the refund policy?", top_k: int = 5):
    return client.post("/api/chat", json={"question": question, "top_k": top_k})


# ---------------------------------------------------------------------------
# Schema validation — ChatRequest
# ---------------------------------------------------------------------------

def test_chat_request_default_top_k():
    req = ChatRequest(question="What is the policy?")
    assert req.top_k == 5


def test_chat_request_custom_top_k():
    req = ChatRequest(question="test", top_k=3)
    assert req.top_k == 3


def test_chat_request_strips_whitespace():
    req = ChatRequest(question="  hello  ")
    assert req.question == "hello"


def test_chat_request_empty_question_raises():
    with pytest.raises(ValidationError):
        ChatRequest(question="")


def test_chat_request_blank_question_raises():
    with pytest.raises(ValidationError):
        ChatRequest(question="   ")


def test_chat_request_top_k_zero_raises():
    with pytest.raises(ValidationError):
        ChatRequest(question="test", top_k=0)


def test_chat_request_top_k_above_twenty_raises():
    with pytest.raises(ValidationError):
        ChatRequest(question="test", top_k=21)


# ---------------------------------------------------------------------------
# POST /api/chat — empty collection
# ---------------------------------------------------------------------------

def test_chat_endpoint_returns_200():
    response = _chat()
    assert response.status_code == 200


def test_chat_endpoint_response_shape():
    data = _chat().json()
    assert "question" in data
    assert "answer" in data
    assert "citations" in data
    assert "sources" in data
    assert "retrieval_count" in data


def test_chat_endpoint_empty_collection_returns_no_info_message():
    data = _chat().json()
    assert data["answer"] == NO_INFO_MESSAGE


def test_chat_endpoint_empty_collection_empty_sources():
    data = _chat().json()
    assert data["sources"] == []
    assert data["citations"] == []


def test_chat_endpoint_empty_collection_retrieval_count_zero():
    data = _chat().json()
    assert data["retrieval_count"] == 0


def test_chat_endpoint_echoes_question():
    data = _chat(question="What is the return window?").json()
    assert data["question"] == "What is the return window?"


def test_chat_endpoint_empty_question_rejected():
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/chat — after upload (FakeVectorStore holds chunks)
# ---------------------------------------------------------------------------

def test_chat_after_upload_returns_200():
    _upload_txt()
    response = _chat()
    assert response.status_code == 200


def test_chat_after_upload_answer_is_string():
    _upload_txt()
    data = _chat().json()
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_chat_after_upload_retrieval_count_positive():
    _upload_txt()
    data = _chat().json()
    assert data["retrieval_count"] > 0


def test_chat_after_upload_has_sources():
    _upload_txt()
    data = _chat().json()
    assert len(data["sources"]) > 0


def test_chat_after_upload_source_has_required_fields():
    _upload_txt()
    data = _chat().json()
    source = data["sources"][0]
    assert "source_id" in source
    assert "document_id" in source
    assert "original_filename" in source
    assert "file_type" in source
    assert "chunk_index" in source
    assert "score" in source
    assert "chunk_text_preview" in source


def test_chat_after_upload_citations_is_list():
    _upload_txt()
    data = _chat().json()
    assert isinstance(data["citations"], list)


def test_chat_after_upload_citations_contain_bracket_refs():
    _upload_txt()
    data = _chat().json()
    # FakeLLMProvider returns FIXED_RESPONSE which contains "[1]"
    assert "[1]" in data["citations"]


def test_fake_llm_provider_is_active_in_tests():
    # Confirm the conftest fixture replaced the real provider
    assert isinstance(llm_service._provider, FakeLLMProvider)
