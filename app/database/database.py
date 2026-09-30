"""SQLite database management and persistence layer for SentinelX."""

import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from app.config.settings import settings
from app.database.models import DetectionRecord, QuarantineRecord, RiskLevel, ScannedFileRecord


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


# Global default database instance
db = Database()
