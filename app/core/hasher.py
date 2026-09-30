"""Cryptographic hashing and file metadata extraction."""

import hashlib
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileMetadata:
    """Metadata and hashes for an inspected file."""

    path: Path
    file_name: str
    size: int
    size_formatted: str
    sha256: str
    md5: str
    sha1: str
    file_type: str
    extension: str
    created_time: datetime
    modified_time: datetime


def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"


def calculate_hashes_and_metadata(file_path: Path) -> FileMetadata:
    """Calculate SHA-256, MD5, SHA-1 and gather file metadata in a single streaming pass.

    Args:
        file_path: Path to target file.

    Returns:
        FileMetadata dataclass containing calculated hashes and attributes.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If access is denied.
    """
    resolved_path = Path(file_path).resolve()
    if not resolved_path.exists() or not resolved_path.is_file():
        raise FileNotFoundError(f"Target file does not exist or is not a file: {resolved_path}")

    stat = resolved_path.stat()
    size = stat.st_size
    created_time = datetime.fromtimestamp(stat.st_ctime)
    modified_time = datetime.fromtimestamp(stat.st_mtime)

    sha256_hash = hashlib.sha256()
    md5_hash = hashlib.md5(usedforsecurity=False)  # nosec B324
    sha1_hash = hashlib.sha1(usedforsecurity=False)  # nosec B324

    # Stream in 64 KB chunks
    chunk_size = 64 * 1024
    with open(resolved_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256_hash.update(chunk)
            md5_hash.update(chunk)
            sha1_hash.update(chunk)

    extension = resolved_path.suffix.lower()
    mime_type, _ = mimetypes.guess_type(str(resolved_path))
    file_type = mime_type or (f"{extension[1:].upper()} File" if extension else "Binary File")

    return FileMetadata(
        path=resolved_path,
        file_name=resolved_path.name,
        size=size,
        size_formatted=format_file_size(size),
        sha256=sha256_hash.hexdigest(),
        md5=md5_hash.hexdigest(),
        sha1=sha1_hash.hexdigest(),
        file_type=file_type,
        extension=extension,
        created_time=created_time,
        modified_time=modified_time,
    )


def calculate_sha256(file_path: Path) -> str:
    """Calculate only SHA-256 hash for a file."""
    sha256_hash = hashlib.sha256()
    resolved_path = Path(file_path).resolve()
    with open(resolved_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()
