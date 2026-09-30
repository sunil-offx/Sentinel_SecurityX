"""Unit tests for quarantine isolation, safety boundaries, and restore operations."""

import tempfile
from pathlib import Path

import pytest

from app.core.quarantine import QuarantineManager
from app.database.database import Database


@pytest.fixture
def quarantine_env():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        vault_dir = base_dir / "quarantine_vault"
        db_path = base_dir / "test.db"
        test_db = Database(db_path=db_path)

        # Monkey-patch global db in quarantine module
        import app.core.quarantine as q_mod

        orig_db = q_mod.db
        q_mod.db = test_db

        manager = QuarantineManager(quarantine_dir=vault_dir)

        yield manager, base_dir, test_db

        q_mod.db = orig_db


def test_quarantine_and_restore_cycle(quarantine_env):
    manager, base_dir, test_db = quarantine_env

    # Create dummy suspicious file
    source_file = base_dir / "suspicious_test.exe"
    source_file.write_bytes(b"Simulated suspicious executable payload")
    orig_content = source_file.read_bytes()

    # 1. Quarantine
    record = manager.quarantine_file(
        file_path=source_file,
        sha256="abc123" * 10,
        reason="Test high entropy detection",
        risk_score=78,
    )

    assert not source_file.exists(), "Source file should have been moved"
    q_file = Path(record.quarantine_path)
    assert q_file.exists(), "Quarantined file must exist in vault"
    assert q_file.read_bytes() == orig_content

    # 2. Restore
    success = manager.restore_file(record.id)
    assert success is True
    assert source_file.exists(), "Source file must be restored"
    assert not q_file.exists(), "Quarantine storage file should be moved back"
    assert source_file.read_bytes() == orig_content


def test_quarantine_and_delete(quarantine_env):
    manager, base_dir, test_db = quarantine_env

    source_file = base_dir / "delete_me.bat"
    source_file.write_text("del *.*", encoding="utf-8")

    record = manager.quarantine_file(
        file_path=source_file,
        sha256="deadbeef" * 8,
        reason="Malicious script deletion command",
        risk_score=90,
    )

    q_file = Path(record.quarantine_path)
    assert q_file.exists()

    # Delete permanently
    del_ok = manager.permanently_delete(record.id)
    assert del_ok is True
    assert not q_file.exists()

    # Check status in db
    records = test_db.get_quarantine_records()
    assert records[0].status == "DELETED"
