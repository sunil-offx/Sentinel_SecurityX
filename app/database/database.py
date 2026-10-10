"""SQLite database management and persistence layer for SentinelX."""

import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from app.config.settings import settings
from app.database.models import (
    DetectionRecord,
    EventLogRecord,
    NetworkAlertRecord,
    ProcessAlertRecord,
    QuarantineRecord,
    RiskLevel,
    ScannedFileRecord,
    ThreatIntelRecord,
)


class Database:
    """Manages SQLite storage for scans, detections, and quarantined files."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.db_path
        self._lock = threading.Lock()
        self._ensure_parent_dir()
        self.init_db()

    def _ensure_parent_dir(self) -> None:
        """Ensure parent directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provide a contextual database connection with row factory and foreign keys."""
        conn = sqlite3.connect(str(self.db_path), timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Create database tables and indexes if they do not exist."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()

            # Files table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    md5 TEXT,
                    sha1 TEXT,
                    size INTEGER NOT NULL,
                    scanned_at TEXT NOT NULL,
                    risk_score INTEGER NOT NULL DEFAULT 0,
                    risk_level TEXT NOT NULL DEFAULT 'SAFE',
                    file_type TEXT
                );
                """
            )

            # Detections table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    detection_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                );
                """
            )

            # Quarantine table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quarantine (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_path TEXT NOT NULL,
                    quarantine_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    risk_score INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'QUARANTINED'
                );
                """
            )

            # Phase 2: Process alerts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS process_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pid INTEGER NOT NULL,
                    process_name TEXT NOT NULL,
                    ppid INTEGER NOT NULL DEFAULT 0,
                    parent_name TEXT DEFAULT '',
                    command_line TEXT DEFAULT '',
                    severity TEXT NOT NULL DEFAULT 'HIGH',
                    reason TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE'
                );
                """
            )

            # Phase 3: Network alerts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS network_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pid INTEGER NOT NULL,
                    process_name TEXT NOT NULL,
                    local_addr TEXT,
                    remote_addr TEXT,
                    remote_port INTEGER,
                    protocol TEXT DEFAULT 'TCP',
                    severity TEXT NOT NULL DEFAULT 'HIGH',
                    reason TEXT NOT NULL,
                    detected_at TEXT NOT NULL
                );
                """
            )

            # Phase 3: Windows Event log telemetry records table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS event_log_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    provider TEXT DEFAULT '',
                    severity TEXT NOT NULL DEFAULT 'LOW',
                    message TEXT NOT NULL,
                    event_time TEXT DEFAULT '',
                    detected_at TEXT NOT NULL
                );
                """
            )

            # Phase 3: Threat intelligence cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS threat_intel_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    indicator_type TEXT NOT NULL,
                    indicator_value TEXT NOT NULL UNIQUE,
                    score INTEGER NOT NULL DEFAULT 0,
                    malicious_count INTEGER NOT NULL DEFAULT 0,
                    total_count INTEGER NOT NULL DEFAULT 0,
                    details_json TEXT DEFAULT '{}',
                    cached_at TEXT NOT NULL
                );
                """
            )

            # Indexes for high performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_scanned_at ON files(scanned_at DESC);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_detections_file_id ON detections(file_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_quarantine_status ON quarantine(status);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_proc_alerts_status ON process_alerts(status);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_net_alerts_time ON network_alerts(detected_at DESC);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_event_logs_time ON event_log_records(detected_at DESC);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ti_indicator ON threat_intel_cache(indicator_value);"
            )


    def add_scan_result(self, record: ScannedFileRecord) -> int:
        """Store a scanned file record and its detections."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO files (path, sha256, md5, sha1, size, scanned_at, risk_score, risk_level, file_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.path,
                    record.sha256,
                    record.md5,
                    record.sha1,
                    record.size,
                    record.scanned_at,
                    record.risk_score,
                    record.risk_level,
                    record.file_type,
                ),
            )
            file_id = cursor.lastrowid
            record.id = file_id

            for det in record.detections:
                cursor.execute(
                    """
                    INSERT INTO detections (file_id, detection_type, severity, reason, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (file_id, det.detection_type, det.severity, det.reason, det.created_at),
                )
                det.file_id = file_id

            return file_id

    def get_recent_scans(self, limit: int = 100) -> list[ScannedFileRecord]:
        """Fetch the most recent scan records."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, path, sha256, md5, sha1, size, scanned_at, risk_score, risk_level, file_type
                FROM files
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            file_rows = cursor.fetchall()
            results: list[ScannedFileRecord] = []

            for f in file_rows:
                cursor.execute(
                    """
                    SELECT id, file_id, detection_type, severity, reason, created_at
                    FROM detections
                    WHERE file_id = ?
                    """,
                    (f["id"],),
                )
                det_rows = cursor.fetchall()
                detections = [
                    DetectionRecord(
                        id=d["id"],
                        file_id=d["file_id"],
                        detection_type=d["detection_type"],
                        severity=d["severity"],
                        reason=d["reason"],
                        created_at=d["created_at"],
                    )
                    for d in det_rows
                ]

                results.append(
                    ScannedFileRecord(
                        id=f["id"],
                        path=f["path"],
                        sha256=f["sha256"],
                        md5=f["md5"] or "",
                        sha1=f["sha1"] or "",
                        size=f["size"],
                        scanned_at=f["scanned_at"],
                        risk_score=f["risk_score"],
                        risk_level=f["risk_level"],
                        file_type=f["file_type"] or "",
                        detections=detections,
                    )
                )

            return results

    def add_quarantine_record(self, record: QuarantineRecord) -> int:
        """Add a new quarantined item."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO quarantine (original_path, quarantine_path, sha256, reason, risk_score, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.original_path,
                    record.quarantine_path,
                    record.sha256,
                    record.reason,
                    record.risk_score,
                    record.created_at,
                    record.status,
                ),
            )
            record.id = cursor.lastrowid
            return record.id

    def get_quarantine_records(self, status: str | None = None) -> list[QuarantineRecord]:
        """Fetch quarantine records optionally filtered by status."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    """
                    SELECT id, original_path, quarantine_path, sha256, reason, risk_score, created_at, status
                    FROM quarantine
                    WHERE status = ?
                    ORDER BY id DESC
                    """,
                    (status,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, original_path, quarantine_path, sha256, reason, risk_score, created_at, status
                    FROM quarantine
                    ORDER BY id DESC
                    """
                )
            rows = cursor.fetchall()
            return [
                QuarantineRecord(
                    id=r["id"],
                    original_path=r["original_path"],
                    quarantine_path=r["quarantine_path"],
                    sha256=r["sha256"],
                    reason=r["reason"],
                    risk_score=r["risk_score"],
                    created_at=r["created_at"],
                    status=r["status"],
                )
                for r in rows
            ]

    def update_quarantine_status(self, record_id: int, status: str) -> bool:
        """Update the status of a quarantined file."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE quarantine SET status = ? WHERE id = ?",
                (status, record_id),
            )
            return cursor.rowcount > 0

    # --- Phase 2: Process Monitoring Methods ---

    def add_process_alert(self, record: ProcessAlertRecord) -> int:
        """Store a suspicious process alert."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO process_alerts (pid, process_name, ppid, parent_name, command_line, severity, reason, detected_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.pid,
                    record.process_name,
                    record.ppid,
                    record.parent_name,
                    record.command_line,
                    record.severity,
                    record.reason,
                    record.detected_at,
                    record.status,
                ),
            )
            record.id = cursor.lastrowid
            return record.id

    def get_process_alerts(
        self, status: str | None = None, limit: int = 100
    ) -> list[ProcessAlertRecord]:
        """Fetch process alerts filtered optionally by status."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    """
                    SELECT id, pid, process_name, ppid, parent_name, command_line, severity, reason, detected_at, status
                    FROM process_alerts
                    WHERE status = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (status, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, pid, process_name, ppid, parent_name, command_line, severity, reason, detected_at, status
                    FROM process_alerts
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [
                ProcessAlertRecord(
                    id=r["id"],
                    pid=r["pid"],
                    process_name=r["process_name"],
                    ppid=r["ppid"],
                    parent_name=r["parent_name"] or "",
                    command_line=r["command_line"] or "",
                    severity=r["severity"],
                    reason=r["reason"],
                    detected_at=r["detected_at"],
                    status=r["status"],
                )
                for r in rows
            ]

    def update_process_alert_status(self, alert_id: int, status: str) -> bool:
        """Update status of a process alert (e.g. TERMINATED or DISMISSED)."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE process_alerts SET status = ? WHERE id = ?",
                (status, alert_id),
            )
            return cursor.rowcount > 0

    # --- Phase 3: Network & Telemetry Methods ---

    def add_network_alert(self, record: NetworkAlertRecord) -> int:
        """Store a suspicious network connection alert."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO network_alerts (pid, process_name, local_addr, remote_addr, remote_port, protocol, severity, reason, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.pid,
                    record.process_name,
                    record.local_addr,
                    record.remote_addr,
                    record.remote_port,
                    record.protocol,
                    record.severity,
                    record.reason,
                    record.detected_at,
                ),
            )
            record.id = cursor.lastrowid
            return record.id

    def get_network_alerts(self, limit: int = 100) -> list[NetworkAlertRecord]:
        """Fetch recent network alerts."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, pid, process_name, local_addr, remote_addr, remote_port, protocol, severity, reason, detected_at
                FROM network_alerts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                NetworkAlertRecord(
                    id=r["id"],
                    pid=r["pid"],
                    process_name=r["process_name"],
                    local_addr=r["local_addr"] or "",
                    remote_addr=r["remote_addr"] or "",
                    remote_port=r["remote_port"] or 0,
                    protocol=r["protocol"] or "TCP",
                    severity=r["severity"],
                    reason=r["reason"],
                    detected_at=r["detected_at"],
                )
                for r in rows
            ]

    def add_event_log_record(self, record: EventLogRecord) -> int:
        """Store an ingested Windows Event Log audit record."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO event_log_records (event_id, channel, provider, severity, message, event_time, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.event_id,
                    record.channel,
                    record.provider,
                    record.severity,
                    record.message,
                    record.event_time,
                    record.detected_at,
                ),
            )
            record.id = cursor.lastrowid
            return record.id

    def get_event_log_records(
        self, severity: str | None = None, limit: int = 100
    ) -> list[EventLogRecord]:
        """Fetch recent Windows Event Log records."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            if severity:
                cursor.execute(
                    """
                    SELECT id, event_id, channel, provider, severity, message, event_time, detected_at
                    FROM event_log_records
                    WHERE severity = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (severity, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, event_id, channel, provider, severity, message, event_time, detected_at
                    FROM event_log_records
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [
                EventLogRecord(
                    id=r["id"],
                    event_id=r["event_id"],
                    channel=r["channel"],
                    provider=r["provider"] or "",
                    severity=r["severity"],
                    message=r["message"],
                    event_time=r["event_time"] or "",
                    detected_at=r["detected_at"],
                )
                for r in rows
            ]

    # --- Phase 3: Threat Intelligence Cache ---

    def set_threat_intel_cache(self, record: ThreatIntelRecord) -> int:
        """Store or update cached threat intel lookup."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO threat_intel_cache (indicator_type, indicator_value, score, malicious_count, total_count, details_json, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(indicator_value) DO UPDATE SET
                    score = excluded.score,
                    malicious_count = excluded.malicious_count,
                    total_count = excluded.total_count,
                    details_json = excluded.details_json,
                    cached_at = excluded.cached_at
                """,
                (
                    record.indicator_type,
                    record.indicator_value,
                    record.score,
                    record.malicious_count,
                    record.total_count,
                    record.details_json,
                    record.cached_at,
                ),
            )
            return cursor.lastrowid

    def get_threat_intel_cache(self, indicator_value: str) -> ThreatIntelRecord | None:
        """Fetch cached threat intel record if available."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, indicator_type, indicator_value, score, malicious_count, total_count, details_json, cached_at
                FROM threat_intel_cache
                WHERE indicator_value = ?
                """,
                (indicator_value,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return ThreatIntelRecord(
                id=row["id"],
                indicator_type=row["indicator_type"],
                indicator_value=row["indicator_value"],
                score=row["score"],
                malicious_count=row["malicious_count"],
                total_count=row["total_count"],
                details_json=row["details_json"],
                cached_at=row["cached_at"],
            )

    def get_stats(self) -> dict:
        """Retrieve aggregated application metrics for the dashboard."""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            total_scanned = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM files WHERE risk_level IN (?, ?)",
                (RiskLevel.HIGH.value, RiskLevel.CRITICAL.value),
            )
            threats_detected = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM quarantine WHERE status = 'QUARANTINED'")
            active_quarantined = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM process_alerts WHERE status = 'ACTIVE'")
            active_process_alerts = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM network_alerts")
            total_network_alerts = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM event_log_records")
            total_event_logs = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN risk_level = 'SAFE' THEN 1 ELSE 0 END) as safe_count,
                    SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low_count,
                    SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_count,
                    SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count
                FROM files
                """
            )
            dist = cursor.fetchone()
            safe_count = dist["safe_count"] or 0
            low_count = dist["low_count"] or 0
            high_count = dist["high_count"] or 0
            critical_count = dist["critical_count"] or 0

            return {
                "total_scanned": total_scanned,
                "threats_detected": threats_detected,
                "active_quarantined": active_quarantined,
                "active_process_alerts": active_process_alerts,
                "total_network_alerts": total_network_alerts,
                "total_event_logs": total_event_logs,
                "safe_count": safe_count,
                "low_count": low_count,
                "high_count": high_count,
                "critical_count": critical_count,
            }

    def clear_all(self) -> None:
        """Clear all records from database (useful for testing and reset)."""
        with self._lock, self.get_connection() as conn:
            conn.execute("DELETE FROM detections")
            conn.execute("DELETE FROM files")
            conn.execute("DELETE FROM quarantine")
            conn.execute("DELETE FROM process_alerts")
            conn.execute("DELETE FROM network_alerts")
            conn.execute("DELETE FROM event_log_records")
            conn.execute("DELETE FROM threat_intel_cache")


# Global default database instance
db = Database()

