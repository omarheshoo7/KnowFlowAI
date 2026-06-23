import io
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.search import SearchRequest
from backend.app.services.vector_store_service import FakeVectorStore, ChunkPoint
import backend.app.services.storage_service as storage_service

client = TestClient(app)

FAKE_EMBEDDING = [0.1] * 384


# ---------------------------------------------------------------------------
# Helper — redirect uploads to tmp_path so no real files land on disk
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path):
    with patch.object(storage_service, "UPLOAD_DIR", tmp_path):
        yield


def _upload_txt(client, content: str = "word " * 200):
    return client.post(
        "/api/documents/upload",
        files={"file": ("doc.txt", io.BytesIO(content.encode()), "text/plain")},
    )


# ---------------------------------------------------------------------------
# Schema validation — SearchRequest
# ---------------------------------------------------------------------------

def test_search_request_default_top_k():
    req = SearchRequest(query="What is the refund policy?")
    assert req.top_k == 5


def test_search_request_custom_top_k():
    req = SearchRequest(query="test", top_k=10)
    assert req.top_k == 10


def test_search_request_strips_whitespace_from_query():
    req = SearchRequest(query="  hello  ")
    assert req.query == "hello"


def test_search_request_empty_query_raises():
    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_search_request_blank_query_raises():
    with pytest.raises(ValidationError):
        SearchRequest(query="   ")


def test_search_request_top_k_below_one_raises():
    with pytest.raises(ValidationError):
        SearchRequest(query="test", top_k=0)


def test_search_request_top_k_above_twenty_raises():
    with pytest.raises(ValidationError):
        SearchRequest(query="test", top_k=21)


# ---------------------------------------------------------------------------
# FakeVectorStore.search() unit tests
# ---------------------------------------------------------------------------

def test_fake_store_search_empty_store_returns_empty():
    store = FakeVectorStore()
    results = store.search(FAKE_EMBEDDING, top_k=5)
    assert results == []


def test_fake_store_search_returns_stored_chunks():
    store = FakeVectorStore()
    points = [ChunkPoint(chunk_index=0, text="hello world", word_count=2,
                         character_count=11, embedding=FAKE_EMBEDDING)]
    store.store("doc1", "file.txt", "uuid.txt", "txt", points)
    results = store.search(FAKE_EMBEDDING, top_k=5)
    assert len(results) == 1
    assert results[0].chunk_text == "hello world"
    assert results[0].score == 0.99
    assert results[0].document_id == "doc1"
    assert results[0].original_filename == "file.txt"


def test_fake_store_search_respects_top_k():
    store = FakeVectorStore()
    points = [
        ChunkPoint(chunk_index=i, text=f"chunk {i}", word_count=2,
                   character_count=7, embedding=FAKE_EMBEDDING)
        for i in range(10)
    ]
    store.store("doc1", "file.txt", "uuid.txt", "txt", points)
    results = store.search(FAKE_EMBEDDING, top_k=3)
    assert len(results) == 3


# ---------------------------------------------------------------------------
# POST /api/search endpoint tests
# ---------------------------------------------------------------------------

def test_search_endpoint_returns_200():
    response = client.post("/api/search", json={"query": "test query"})
    assert response.status_code == 200


def test_search_endpoint_response_shape():
    response = client.post("/api/search", json={"query": "test query"})
    data = response.json()
    assert "query" in data
    assert "top_k" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_endpoint_echoes_query_and_top_k():
    response = client.post("/api/search", json={"query": "refund policy", "top_k": 3})
    data = response.json()
    assert data["query"] == "refund policy"
    assert data["top_k"] == 3


def test_search_endpoint_default_top_k_is_five():
    response = client.post("/api/search", json={"query": "test"})
    data = response.json()
    assert data["top_k"] == 5


def test_search_endpoint_empty_store_returns_empty_results():
    # FakeVectorStore starts empty for every test (autouse conftest fixture)
    response = client.post("/api/search", json={"query": "what is the return policy"})
    data = response.json()
    assert data["results"] == []


def test_search_endpoint_empty_query_rejected():
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 422


def test_search_endpoint_top_k_zero_rejected():
    response = client.post("/api/search", json={"query": "test", "top_k": 0})
    assert response.status_code == 422


def test_search_returns_results_after_upload():
    # Upload first — FakeVectorStore stores the chunks.
    # Same FakeVectorStore instance is used for the search call within this test.
    _upload_txt(client, content="word " * 600)
    response = client.post("/api/search", json={"query": "word", "top_k": 5})
    data = response.json()
    assert response.status_code == 200
    assert len(data["results"]) > 0


def test_search_result_has_all_required_fields():
    _upload_txt(client, content="word " * 600)
    response = client.post("/api/search", json={"query": "word", "top_k": 1})
    data = response.json()
    result = data["results"][0]
    assert "document_id" in result
    assert "original_filename" in result
    assert "file_type" in result
    assert "chunk_index" in result
    assert "chunk_text" in result
    assert "score" in result
    assert "word_count" in result
    assert "character_count" in result


def test_search_result_score_is_float():
    _upload_txt(client, content="word " * 600)
    response = client.post("/api/search", json={"query": "word", "top_k": 1})
    data = response.json()
    assert isinstance(data["results"][0]["score"], float)
