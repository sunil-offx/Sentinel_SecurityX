"""End-to-end workflow tests validating MVP Acceptance Criteria (AT-01 through AT-05)."""

import tempfile
import time
from pathlib import Path

import pytest

from app.core.quarantine import QuarantineManager
from app.core.scanner import FileScanner
from app.database.database import Database
from app.monitoring.download_monitor import DownloadMonitor

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def e2e_system():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        db_path = base_dir / "sentinelx_e2e.db"
        q_dir = base_dir / "quarantine_vault"
        dl_dir = base_dir / "downloads"
        dl_dir.mkdir(parents=True, exist_ok=True)

        test_db = Database(db_path=db_path)

        # Patch db in modules
        import app.core.quarantine as q_mod
        import app.core.scanner as s_mod

        orig_s_db = s_mod.db
        orig_q_db = q_mod.db
        s_mod.db = test_db
        q_mod.db = test_db

        scanner = FileScanner()
        quarantine_mgr = QuarantineManager(quarantine_dir=q_dir)

        yield {
            "db": test_db,
            "scanner": scanner,
            "quarantine": quarantine_mgr,
            "downloads_dir": dl_dir,
            "base_dir": base_dir,
        }

        s_mod.db = orig_s_db
        q_mod.db = orig_q_db


def test_at_01_file_scanning(e2e_system):
    """AT-01 — Given a valid executable, when scanned, SentinelX calculates metadata and SHA-256."""
    scanner = e2e_system["scanner"]
    sample = FIXTURES_DIR / "clean_sample.exe"

    result = scanner.scan_file(sample)

    assert result.metadata.sha256 is not None
    assert len(result.metadata.sha256) == 64
    assert result.metadata.size > 0
    assert result.metadata.created_time is not None
    assert result.metadata.modified_time is not None


def test_at_02_detection(e2e_system):
    """AT-02 — Given a fixture containing a known test pattern, detection engine identifies it."""
    scanner = e2e_system["scanner"]
    sample = FIXTURES_DIR / "test_yara_sample.bin"

    result = scanner.scan_file(sample)

    assert len(result.yara_matches) >= 1
    assert result.yara_matches[0].rule_name == "SentinelX_Test_Rule"
    assert result.assessment.risk_score >= 40


def test_at_03_quarantine(e2e_system):
    """AT-03 — Given a suspicious file, when quarantined, file is moved to quarantine directory."""
    scanner = e2e_system["scanner"]
    q_mgr = e2e_system["quarantine"]
    base_dir = e2e_system["base_dir"]

    # Create dummy suspicious executable
    suspicious_file = base_dir / "threat.exe"
    suspicious_file.write_bytes(b"Simulated threat content")

    res = scanner.scan_file(suspicious_file)
    rec = q_mgr.quarantine_file(
        file_path=suspicious_file,
        sha256=res.metadata.sha256,
        reason="Suspicious pattern detected",
        risk_score=res.assessment.risk_score,
    )

    # Verify original file no longer exists at source
    assert not suspicious_file.exists()

    # Verify file exists in quarantine
    q_path = Path(rec.quarantine_path)
    assert q_path.exists()
    assert q_path.parent == q_mgr.quarantine_dir


def test_at_04_history(e2e_system):
    """AT-04 — Given a completed scan, scan appears in Scan History."""
    scanner = e2e_system["scanner"]
    test_db = e2e_system["db"]
    sample = FIXTURES_DIR / "clean_sample.exe"

    result = scanner.scan_file(sample)
    recent = test_db.get_recent_scans(limit=5)

    assert len(recent) >= 1
    assert recent[0].sha256 == result.metadata.sha256
    assert recent[0].id == result.db_record_id


def test_at_05_download_monitoring(e2e_system):
    """AT-05 — Given Downloads directory is monitored, when new supported file appears, queued for analysis."""
    dl_dir = e2e_system["downloads_dir"]
    scanned_results = []

    def on_scanned(res):
        scanned_results.append(res)

    monitor = DownloadMonitor(
        watch_dir=dl_dir,
        poll_interval_seconds=0.3,
        on_file_scanned=on_scanned,
    )
    monitor.start()

    try:
        # Simulate browser dropping a new executable in Downloads
        new_file = dl_dir / "incoming_payload.bat"
        new_file.write_text("powershell -enc AAAA\n", encoding="utf-8")

        # Allow monitor thread polling loop to catch and process file
        for _ in range(40):
            if len(scanned_results) >= 1:
                break
            time.sleep(0.1)

        assert len(scanned_results) >= 1
        assert scanned_results[0].metadata.file_name == "incoming_payload.bat"
    finally:
        monitor.stop()
