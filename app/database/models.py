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
    ML_MALWARE = "ML_MALWARE"
    PROCESS_ANOMALY = "PROCESS_ANOMALY"
    NETWORK_ANOMALY = "NETWORK_ANOMALY"
    EVENT_LOG_ALERT = "EVENT_LOG_ALERT"
    THREAT_INTEL = "THREAT_INTEL"


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


@dataclass
class ProcessAlertRecord:
    """Alert record for suspicious process activity."""

    id: int | None = None
    pid: int = 0
    process_name: str = ""
    ppid: int = 0
    parent_name: str = ""
    command_line: str = ""
    severity: str = RiskLevel.HIGH.value
    reason: str = ""
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "ACTIVE"  # ACTIVE, TERMINATED, DISMISSED


@dataclass
class NetworkAlertRecord:
    """Alert record for suspicious outbound network connections."""

    id: int | None = None
    pid: int = 0
    process_name: str = ""
    local_addr: str = ""
    remote_addr: str = ""
    remote_port: int = 0
    protocol: str = "TCP"
    severity: str = RiskLevel.HIGH.value
    reason: str = ""
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class EventLogRecord:
    """Ingested security/system event log record."""

    id: int | None = None
    event_id: int = 0
    channel: str = ""
    provider: str = ""
    severity: str = RiskLevel.LOW.value
    message: str = ""
    event_time: str = ""
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ThreatIntelRecord:
    """Cached threat intelligence lookup record."""

    id: int | None = None
    indicator_type: str = "SHA256"  # SHA256, IP, DOMAIN
    indicator_value: str = ""
    score: int = 0
    malicious_count: int = 0
    total_count: int = 0
    details_json: str = "{}"
    cached_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

