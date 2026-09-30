"""Integration tests for the complete detection pipeline: File -> Scanner -> Detection -> Database."""

import tempfile
from pathlib import Path

import pytest

from app.core.scanner import FileScanner
from app.database.database import Database
from app.database.models import RiskLevel

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def isolated_pipeline():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "pipeline_test.db"
        test_db = Database(db_path=db_path)

        # Patch global db
        import app.core.scanner as s_mod

        orig_db = s_mod.db
        s_mod.db = test_db

        scanner = FileScanner(save_to_db=True)

        yield scanner, test_db

        s_mod.db = orig_db


def test_clean_file_pipeline(isolated_pipeline):
    scanner, test_db = isolated_pipeline
    clean_sample = FIXTURES_DIR / "clean_sample.exe"

    result = scanner.scan_file(clean_sample)

    assert result.metadata.file_name == "clean_sample.exe"
    assert len(result.metadata.sha256) == 64
    assert result.assessment.risk_level in (RiskLevel.SAFE, RiskLevel.LOW)
    assert result.db_record_id is not None

    # Verify presence in database
    recent = test_db.get_recent_scans(limit=10)
    assert len(recent) == 1
    assert recent[0].sha256 == result.metadata.sha256


def test_yara_trigger_pipeline(isolated_pipeline):
    scanner, test_db = isolated_pipeline
    yara_sample = FIXTURES_DIR / "test_yara_sample.bin"

    result = scanner.scan_file(yara_sample)

    assert len(result.yara_matches) >= 1
    assert result.assessment.risk_score >= 40
    assert result.db_record_id is not None

    recent = test_db.get_recent_scans(limit=10)
    assert len(recent[0].detections) >= 1


def test_script_heuristic_pipeline(isolated_pipeline):
    scanner, test_db = isolated_pipeline
    script_sample = FIXTURES_DIR / "test_script.ps1"

    result = scanner.scan_file(script_sample)

    assert len(result.static_analysis.script_triggers) >= 1
    assert result.assessment.risk_score >= 40
    assert any("Dynamic Code Execution" in r for r in result.assessment.reasons)


def test_directory_scan_pipeline(isolated_pipeline):
    scanner, test_db = isolated_pipeline

    progress_events = []

    def on_progress(cur, tot, path, res):
        progress_events.append((cur, tot, path, res is not None))

    results = scanner.scan_directory(FIXTURES_DIR, filter_extensions=False, progress_cb=on_progress)

    assert len(results) >= 4
    assert len(progress_events) >= 4
    assert progress_events[-1][0] == progress_events[-1][1]  # cur == tot at end
