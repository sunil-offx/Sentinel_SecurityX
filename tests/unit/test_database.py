"""Unit tests for SQLite database operations and audit retention."""

import tempfile
from pathlib import Path

import pytest

from app.database.database import Database
from app.database.models import DetectionRecord, QuarantineRecord, RiskLevel, ScannedFileRecord


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_sentinelx.db"
        test_db = Database(db_path=db_path)
        yield test_db


def test_add_and_query_scan(temp_db):
    record = ScannedFileRecord(
        path="C:\\test\\malicious.exe",
        sha256="abcd" * 16,
        size=1024,
        risk_score=75,
        risk_level=RiskLevel.HIGH.value,
        file_type="Executable File",
        detections=[
            DetectionRecord(
                detection_type="YARA",
                severity=RiskLevel.HIGH.value,
                reason="Matched test signature",
            )
        ],
    )
    file_id = temp_db.add_scan_result(record)
    assert file_id is not None
    assert file_id > 0

    recent = temp_db.get_recent_scans(limit=10)
    assert len(recent) == 1
    assert recent[0].path == "C:\\test\\malicious.exe"
    assert recent[0].risk_score == 75
    assert len(recent[0].detections) == 1
    assert recent[0].detections[0].reason == "Matched test signature"


def test_quarantine_crud(temp_db):
    q_rec = QuarantineRecord(
        original_path="C:\\Users\\test\\Downloads\\payload.exe",
        quarantine_path="C:\\vault\\isolated.qtn",
        sha256="1234" * 16,
        reason="High entropy and injection APIs",
        risk_score=85,
    )
    qid = temp_db.add_quarantine_record(q_rec)
    assert qid > 0

    active_items = temp_db.get_quarantine_records(status="QUARANTINED")
    assert len(active_items) == 1
    assert active_items[0].sha256 == "1234" * 16

    temp_db.update_quarantine_status(qid, "RESTORED")
    active_after = temp_db.get_quarantine_records(status="QUARANTINED")
    assert len(active_after) == 0


def test_database_stats(temp_db):
    rec_safe = ScannedFileRecord(
        path="safe.dll", sha256="1" * 64, size=500, risk_score=10, risk_level=RiskLevel.SAFE.value
    )
    rec_threat = ScannedFileRecord(
        path="bad.exe",
        sha256="2" * 64,
        size=1500,
        risk_score=85,
        risk_level=RiskLevel.CRITICAL.value,
    )
    temp_db.add_scan_result(rec_safe)
    temp_db.add_scan_result(rec_threat)

    stats = temp_db.get_stats()
    assert stats["total_scanned"] == 2
    assert stats["threats_detected"] == 1
    assert stats["safe_count"] == 1
    assert stats["critical_count"] == 1
