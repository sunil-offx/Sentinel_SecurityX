"""Unit tests for cryptographic hasher and metadata extraction."""

from pathlib import Path

import pytest

from app.core.hasher import calculate_hashes_and_metadata, calculate_sha256, format_file_size

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_format_file_size():
    assert format_file_size(500) == "500 B"
    assert "KB" in format_file_size(2048)
    assert "MB" in format_file_size(5 * 1024 * 1024)
    assert "GB" in format_file_size(2 * 1024 * 1024 * 1024)


def test_calculate_hashes_known_fixture():
    fixture_path = FIXTURES_DIR / "suspicious_extension.txt"
    metadata = calculate_hashes_and_metadata(fixture_path)

    assert metadata.file_name == "suspicious_extension.txt"
    assert metadata.extension == ".txt"
    assert len(metadata.sha256) == 64
    assert len(metadata.md5) == 32
    assert len(metadata.sha1) == 40
    assert metadata.size > 0

    # Ensure single sha256 matches composite calculation
    single_sha = calculate_sha256(fixture_path)
    assert single_sha == metadata.sha256


def test_hasher_non_existent_file():
    with pytest.raises(FileNotFoundError):
        calculate_hashes_and_metadata(Path("non_existent_sentinelx_file.xyz"))
