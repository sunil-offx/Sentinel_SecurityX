"""Unit tests for YARA rule detection and matching."""

from pathlib import Path

from app.detection.yara_engine import yara_engine

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_yara_engine_loaded():
    assert yara_engine.is_loaded is True
    assert yara_engine.rules is not None


def test_yara_match_test_token():
    sample_path = FIXTURES_DIR / "test_yara_sample.bin"
    matches = yara_engine.scan_file(sample_path)

    assert len(matches) >= 1
    rule_names = [m.rule_name for m in matches]
    assert "SentinelX_Test_Rule" in rule_names


def test_yara_clean_file_no_match():
    clean_path = FIXTURES_DIR / "clean_sample.exe"
    matches = yara_engine.scan_file(clean_path)
    # The clean minimal PE should not trigger malware rules
    test_matches = [m for m in matches if m.rule_name == "SentinelX_Test_Rule"]
    assert len(test_matches) == 0
