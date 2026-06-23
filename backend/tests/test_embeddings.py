import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import embedding_service
from backend.app.services.embedding_service import FakeEmbeddingProvider
import backend.app.services.storage_service as storage_service

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests — embedding_service.embed_chunks() via FakeEmbeddingProvider
# (conftest.py patches _provider to FakeEmbeddingProvider for all tests)
# ---------------------------------------------------------------------------

def test_embed_chunks_empty_list_returns_empty():
    result = embedding_service.embed_chunks([])
    assert result == []


def test_embed_chunks_returns_one_vector_per_chunk():
    texts = ["First chunk text.", "Second chunk text.", "Third chunk text."]
    result = embedding_service.embed_chunks(texts)
    assert len(result) == 3


def test_embed_chunks_single_text():
    result = embedding_service.embed_chunks(["Only one chunk."])
    assert len(result) == 1


def test_embed_chunks_vectors_are_lists_of_floats():
    texts = ["chunk one", "chunk two"]
    result = embedding_service.embed_chunks(texts)
    for vector in result:
        assert isinstance(vector, list)
        assert all(isinstance(v, float) for v in vector)


def test_embed_chunks_vector_size_matches_bge_small():
    result = embedding_service.embed_chunks(["some text"])
    assert len(result[0]) == FakeEmbeddingProvider.VECTOR_SIZE


def test_embed_chunks_count_matches_input_count():
    texts = [f"chunk number {i}" for i in range(10)]
    result = embedding_service.embed_chunks(texts)
    assert len(result) == len(texts)


def test_fake_provider_returns_floats_directly():
    provider = FakeEmbeddingProvider()
    result = provider.embed(["hello", "world"])
    assert len(result) == 2
    assert len(result[0]) == FakeEmbeddingProvider.VECTOR_SIZE
    assert all(isinstance(v, float) for v in result[0])


def test_fake_provider_empty_input_returns_empty():
    provider = FakeEmbeddingProvider()
    assert provider.embed([]) == []


# ---------------------------------------------------------------------------
# Integration tests — POST /api/documents/upload includes embedding_count
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path):
    with patch.object(storage_service, "UPLOAD_DIR", tmp_path):
        yield


def _upload_bytes(filename: str, content: bytes, content_type: str):
    return client.post(
        "/api/documents/upload",
        files={"file": (filename, io.BytesIO(content), content_type)},
    )


def test_upload_response_includes_embedding_count_field():
    content = ("word " * 100).encode("utf-8")
    response = _upload_bytes("doc.txt", content, "text/plain")
    data = response.json()
    assert response.status_code == 200
    assert "embedding_count" in data
    assert isinstance(data["embedding_count"], int)


def test_txt_upload_embedding_count_equals_chunk_count():
    content = (" ".join([f"word{i}" for i in range(600)])).encode("utf-8")
    response = _upload_bytes("notes.txt", content, "text/plain")
    data = response.json()
    assert data["extraction_status"] == "success"
    assert data["embedding_count"] == data["chunk_count"]
    assert data["embedding_count"] > 0


def test_scanned_pdf_returns_embedding_count_zero():
    import fitz
    import io as _io
    doc = fitz.open()
    doc.new_page()  # blank — no text layer
    buf = _io.BytesIO()
    doc.save(buf)
    doc.close()

    response = _upload_bytes("scan.pdf", buf.getvalue(), "application/pdf")
    data = response.json()
    assert response.status_code == 200
    assert data["extraction_status"] == "failed"
    assert data["embedding_count"] == 0


def test_upload_success_message_mentions_embedded():
    content = ("word " * 100).encode("utf-8")
    response = _upload_bytes("doc.txt", content, "text/plain")
    data = response.json()
    assert "embedded" in data["message"].lower()


def test_md_upload_embedding_count_positive():
    content = ("# Title\n\n" + "word " * 200).encode("utf-8")
    response = _upload_bytes("doc.md", content, "text/markdown")
    data = response.json()
    assert response.status_code == 200
    assert data["embedding_count"] >= 1
