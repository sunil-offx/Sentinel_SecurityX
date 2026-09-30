"""Unit tests for the risk scoring engine and categorization thresholds."""

from datetime import datetime
from pathlib import Path

from app.core.analyzer import StaticAnalysisResult
from app.core.hasher import FileMetadata
from app.core.risk_engine import RiskEngine
from app.database.models import RiskLevel
from app.detection.yara_engine import YaraMatch


def make_metadata(extension: str = ".txt", size: int = 1000) -> FileMetadata:
    return FileMetadata(
        path=Path("sample" + extension),
        file_name="sample" + extension,
        size=size,
        size_formatted="1 KB",
        sha256="0" * 64,
        md5="0" * 32,
        sha1="0" * 40,
        file_type="Test File",
        extension=extension,
        created_time=datetime.utcnow(),
        modified_time=datetime.utcnow(),
    )


def test_risk_clean_file_is_safe():
    engine = RiskEngine()
    meta = make_metadata(".txt")
    static = StaticAnalysisResult(entropy=3.5, entropy_level="NORMAL")
    res = engine.evaluate(meta, static, [])

    assert res.risk_level == RiskLevel.SAFE
    assert res.risk_score <= 29


def test_risk_critical_yara_plus_injection():
    engine = RiskEngine()
    meta = make_metadata(".exe")
    static = StaticAnalysisResult(
        entropy=7.4,
        entropy_level="HIGH",
        is_pe=True,
        suspicious_apis=["CreateRemoteThread", "WriteProcessMemory", "VirtualAllocEx"],
    )
    yara_matches = [
        YaraMatch(
            rule_name="Suspicious_Process_Injection",
            severity="CRITICAL",
            description="Process injection pattern",
        )
    ]
    res = engine.evaluate(meta, static, yara_matches)

    assert res.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert res.risk_score >= 60
    assert len(res.detections) >= 3
    assert len(res.reasons) > 0
