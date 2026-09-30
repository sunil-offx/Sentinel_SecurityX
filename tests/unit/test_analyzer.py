"""Unit tests for static analyzer, entropy computation, and script heuristics."""

from pathlib import Path

from app.core.analyzer import (
    calculate_entropy,
    static_analyzer,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_calculate_entropy_bounds():
    # Empty data
    assert calculate_entropy(b"") == 0.0

    # Low entropy (uniform bytes)
    uniform = b"AAAAAAAAAA" * 100
    assert calculate_entropy(uniform) == 0.0

    # High entropy (random distribution)
    high_entropy_path = FIXTURES_DIR / "high_entropy_sample.bin"
    data = high_entropy_path.read_bytes()
    entropy = calculate_entropy(data)
    assert entropy > 7.5


def test_analyze_high_entropy_file():
    high_entropy_path = FIXTURES_DIR / "high_entropy_sample.bin"
    result = static_analyzer.analyze(high_entropy_path)
    assert result.entropy_level == "HIGH"
    assert any("High entropy" in r for r in result.reasons)


def test_analyze_script_heuristics():
    script_path = FIXTURES_DIR / "test_script.ps1"
    result = static_analyzer.analyze(script_path)

    assert len(result.script_triggers) > 0
    assert any("PowerShell Dynamic Code Execution" in t for t in result.script_triggers)
    assert any("Hidden Window" in t for t in result.script_triggers)


def test_analyze_clean_pe_structure():
    pe_path = FIXTURES_DIR / "clean_sample.exe"
    result = static_analyzer.analyze(pe_path)
    assert result.is_pe is True
    assert len(result.pe_sections) >= 1
    assert result.pe_sections[0].name.startswith(".text")
