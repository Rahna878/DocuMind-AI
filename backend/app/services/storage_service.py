"""
Storage service for persisting uploaded files securely on disk.
Uses random UUID-based keys to prevent path traversal and collision attacks.
"""

import os
import uuid
from pathlib import Path

# Base directory for storing uploaded files
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(file_bytes: bytes, file_extension: str) -> tuple[str, str]:
    """Save bytes to a secure storage path using a generated UUID.

    Returns:
        (storage_key, absolute_filepath)
    """
    storage_key = f"{uuid.uuid4().hex}.{file_extension.lstrip('.')}"
    file_path = UPLOAD_DIR / storage_key

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return storage_key, str(file_path)


def delete_upload_file(storage_key: str) -> None:
    """Clean up a stored file safely if processing fails."""
    try:
        file_path = UPLOAD_DIR / storage_key
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
    except Exception:
        pass

