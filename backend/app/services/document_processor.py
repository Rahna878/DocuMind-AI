"""
Document processing and text extraction services.

Provides:
  - File validation (PDF & TXT allowed, size constraints)
  - Text extraction from TXT and PDF documents
  - Fixed-size overlapping chunking strategy
"""

import io
from pypdf import PdfReader

# Maximum allowed file size: 20 MB
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


class DocumentProcessingError(Exception):
    """Raised when text extraction or processing fails."""


def validate_file(filename: str, file_size: int, file_bytes: bytes) -> str:
    """Validate file extension and size.

    Returns normalized file_type (e.g. 'pdf' or 'txt').
    """
    if not filename:
        raise DocumentProcessingError("Filename is required.")

    lower_name = filename.lower()
    ext = None
    for allowed in ALLOWED_EXTENSIONS:
        if lower_name.endswith(allowed):
            ext = allowed[1:]  # 'pdf' or 'txt'
            break

    if not ext:
        raise DocumentProcessingError(
            f"Unsupported file type. Only PDF and TXT files are accepted (got: {filename})."
        )

    if file_size <= 0 or len(file_bytes) == 0:
        raise DocumentProcessingError("Uploaded file is empty.")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise DocumentProcessingError(
            f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    return ext


def extract_text(file_bytes: bytes, file_type: str) -> list[tuple[int, str]]:
    """Extract text from file bytes.

    Returns a list of tuples: (page_number or 1, text_content).
    """
    extracted_pages: list[tuple[int, str]] = []

    if file_type == "txt":
        try:
            # Try utf-8 first, fallback to latin-1
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1")
            except Exception as exc:
                raise DocumentProcessingError(f"Could not decode text file: {exc}") from exc

        if not text.strip():
            raise DocumentProcessingError("The text file contains no readable text.")

        extracted_pages.append((1, text))

    elif file_type == "pdf":
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            if len(reader.pages) == 0:
                raise DocumentProcessingError("The PDF has no pages.")

            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append((idx, page_text))

            if not extracted_pages:
                raise DocumentProcessingError(
                    "No extractable text found in PDF (it may contain only scanned images)."
                )

        except DocumentProcessingError:
            raise
        except Exception as exc:
            raise DocumentProcessingError(f"Failed to parse PDF document: {exc}") from exc

    else:
        raise DocumentProcessingError(f"Unsupported file type: {file_type}")

    return extracted_pages


def chunk_text(
    pages: list[tuple[int, str]],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """Split text into overlapping chunks while preserving page numbers where possible.

    Args:
        pages: List of (page_number, text) tuples.
        chunk_size: Target characters per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        List of dicts: [{"content": str, "page_number": int | None, "chunk_index": int}]
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be strictly less than chunk_size")

    chunks: list[dict] = []
    chunk_index = 0

    for page_num, page_text in pages:
        cleaned_text = " ".join(page_text.split())
        if not cleaned_text:
            continue

        start = 0
        text_len = len(cleaned_text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_slice = cleaned_text[start:end].strip()

            if chunk_slice:
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": chunk_slice,
                    "page_number": page_num,
                })
                chunk_index += 1

            if end >= text_len:
                break

            start += chunk_size - chunk_overlap

    return chunks

