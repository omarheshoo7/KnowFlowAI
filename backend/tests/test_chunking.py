import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import chunking_service
import backend.app.services.storage_service as storage_service

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests — chunking_service.chunk_text() directly
# ---------------------------------------------------------------------------

def test_empty_string_returns_no_chunks():
    assert chunking_service.chunk_text("") == []


def test_whitespace_only_returns_no_chunks():
    assert chunking_service.chunk_text("   \n\n   ") == []


def test_short_text_produces_one_chunk():
    text = " ".join(["word"] * 100)  # 100 words < 500 default
    chunks = chunking_service.chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].word_count == 100


def test_long_text_produces_multiple_chunks():
    # 1100 words with size=500 overlap=100 → step=400
    # chunk 0: 0-499, chunk 1: 400-899, chunk 2: 800-1099  → 3 chunks
    text = " ".join([str(i) for i in range(1100)])
    chunks = chunking_service.chunk_text(text)
    assert len(chunks) == 3


def test_chunk_indices_are_sequential():
    text = " ".join(["word"] * 1100)
    chunks = chunking_service.chunk_text(text)
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_first_chunk_has_correct_word_count():
    text = " ".join([str(i) for i in range(1100)])
    chunks = chunking_service.chunk_text(text)
    assert chunks[0].word_count == 500


def test_last_chunk_contains_remaining_words():
    # 1100 words: last chunk starts at 800, has 300 words
    text = " ".join([str(i) for i in range(1100)])
    chunks = chunking_service.chunk_text(text)
    assert chunks[-1].word_count == 300


def test_overlap_is_correct():
    """Last N words of chunk[i] should match first N words of chunk[i+1]."""
    words = [str(i) for i in range(200)]
    text = " ".join(words)
    chunks = chunking_service.chunk_text(text, chunk_size_words=50, chunk_overlap_words=10)

    tail = chunks[0].text.split()[-10:]
    head = chunks[1].text.split()[:10]
    assert tail == head


def test_character_count_matches_text_length():
    text = " ".join(["hello"] * 600)
    chunks = chunking_service.chunk_text(text)
    for chunk in chunks:
        assert chunk.character_count == len(chunk.text)


def test_no_empty_chunks():
    text = " ".join(["word"] * 1000)
    chunks = chunking_service.chunk_text(text)
    for chunk in chunks:
        assert chunk.text.strip() != ""
        assert chunk.word_count > 0


def test_custom_chunk_size():
    text = " ".join(["word"] * 100)
    chunks = chunking_service.chunk_text(text, chunk_size_words=30, chunk_overlap_words=5)
    assert len(chunks) > 1
    assert chunks[0].word_count == 30


def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunking_service.chunk_text("some text", chunk_size_words=10, chunk_overlap_words=10)

    with pytest.raises(ValueError):
        chunking_service.chunk_text("some text", chunk_size_words=10, chunk_overlap_words=15)


def test_exact_multiple_of_step():
    # 400 words, size=200, overlap=0, step=200 → exactly 2 chunks
    text = " ".join(["word"] * 400)
    chunks = chunking_service.chunk_text(text, chunk_size_words=200, chunk_overlap_words=0)
    assert len(chunks) == 2
    assert all(c.word_count == 200 for c in chunks)


# ---------------------------------------------------------------------------
# Integration tests — POST /api/documents/upload includes chunk_count
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


def test_txt_upload_response_includes_chunk_count():
    content = (" ".join(["word"] * 600)).encode("utf-8")
    response = _upload_bytes("doc.txt", content, "text/plain")
    data = response.json()
    assert response.status_code == 200
    assert "chunk_count" in data
    assert isinstance(data["chunk_count"], int)
    assert data["chunk_count"] >= 1


def test_txt_upload_chunk_count_is_positive_for_real_content():
    content = (" ".join([f"word{i}" for i in range(600)])).encode("utf-8")
    response = _upload_bytes("notes.txt", content, "text/plain")
    data = response.json()
    assert data["extraction_status"] == "success"
    assert data["chunk_count"] == 2  # 600 words, step=400 → chunks at 0 and 400


def test_md_upload_returns_chunk_count():
    content = ("# Title\n\n" + " ".join(["word"] * 100)).encode("utf-8")
    response = _upload_bytes("readme.md", content, "text/markdown")
    data = response.json()
    assert response.status_code == 200
    assert data["chunk_count"] >= 1


def test_scanned_pdf_returns_chunk_count_zero():
    import fitz
    doc = fitz.open()
    doc.new_page()  # blank — no text
    import io as _io
    buf = _io.BytesIO()
    doc.save(buf)
    doc.close()

    response = _upload_bytes("scan.pdf", buf.getvalue(), "application/pdf")
    data = response.json()
    assert response.status_code == 200
    assert data["extraction_status"] == "failed"
    assert data["chunk_count"] == 0


def test_upload_message_includes_chunked_on_success():
    content = "Hello world. " * 50
    response = _upload_bytes("notes.txt", content.encode("utf-8"), "text/plain")
    data = response.json()
    assert "chunked" in data["message"].lower()
