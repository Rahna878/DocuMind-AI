"""
Unit tests for document processing, validation, and chunking logic.
"""

import pytest
from app.services.document_processor import (
    DocumentProcessingError,
    chunk_text,
    extract_text,
    validate_file,
)


def test_validate_file_valid_txt():
    content = b"Hello DocuMind AI"
    file_type = validate_file("notes.txt", len(content), content)
    assert file_type == "txt"


def test_validate_file_valid_pdf():
    content = b"%PDF-1.4 test"
    file_type = validate_file("report.PDF", len(content), content)
    assert file_type == "pdf"


def test_validate_file_empty_rejected():
    with pytest.raises(DocumentProcessingError, match="empty"):
        validate_file("empty.txt", 0, b"")


def test_validate_file_unsupported_extension():
    content = b"some data"
    with pytest.raises(DocumentProcessingError, match="Unsupported file type"):
        validate_file("archive.zip", len(content), content)


def test_extract_text_txt():
    content = b"This is a test document with plain text content."
    pages = extract_text(content, "txt")
    assert len(pages) == 1
    assert pages[0][0] == 1
    assert "This is a test document" in pages[0][1]


def test_chunk_text_overlap():
    pages = [(1, "A" * 800)]
    chunks = chunk_text(pages, chunk_size=300, chunk_overlap=50)

    assert len(chunks) > 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1
    # Check that chunks have content
    assert len(chunks[0]["content"]) <= 300
    assert len(chunks[1]["content"]) <= 300
    assert chunks[0]["page_number"] == 1


def test_chunk_text_invalid_overlap():
    pages = [(1, "Test content")]
    with pytest.raises(ValueError, match="strictly less"):
        chunk_text(pages, chunk_size=100, chunk_overlap=100)

