"""Data models for SentinelX database and analysis results."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class RiskLevel(StrEnum):
    """Risk severity categorization."""

    SAFE = "SAFE"
    LOW = "LOW"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionType(StrEnum):
    """Categories of detection triggers."""

    YARA = "YARA"
    ENTROPY = "ENTROPY"
    SUSPICIOUS_IMPORT = "SUSPICIOUS_IMPORT"
    SUSPICIOUS_SECTION = "SUSPICIOUS_SECTION"
    SUSPICIOUS_SCRIPT = "SUSPICIOUS_SCRIPT"
    EXTENSION = "EXTENSION"
    HEURISTIC = "HEURISTIC"


@dataclass
class DetectionRecord:
    """Detection item associated with a scanned file."""

    id: int | None = None
    file_id: int | None = None
    detection_type: str = DetectionType.HEURISTIC.value
    severity: str = RiskLevel.LOW.value
    reason: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ScannedFileRecord:
    """Record of a scanned file stored in database."""

    id: int | None = None
    path: str = ""
    sha256: str = ""
    md5: str = ""
    sha1: str = ""
    size: int = 0
    scanned_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    risk_score: int = 0
    risk_level: str = RiskLevel.SAFE.value
    file_type: str = ""
    detections: list[DetectionRecord] = field(default_factory=list)


@dataclass
class QuarantineRecord:
    """Quarantined file metadata record."""

    id: int | None = None
    original_path: str = ""
    quarantine_path: str = ""
    sha256: str = ""
    reason: str = ""
    risk_score: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "QUARANTINED"  # QUARANTINED, RESTORED, DELETED
