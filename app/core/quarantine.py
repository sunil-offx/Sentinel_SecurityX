"""Secure quarantine management with atomic isolation, safe path handling, and restoration."""

import json
import logging
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path

from app.config.settings import settings
from app.database.database import db
from app.database.models import QuarantineRecord

logger = logging.getLogger(__name__)


class QuarantineError(Exception):
    """Exception raised for quarantine operation failures."""

    pass


class QuarantineManager:
    """Safely isolates suspicious files, preventing accidental execution or path traversal."""

    def __init__(self, quarantine_dir: Path | None = None) -> None:
        self.quarantine_dir = quarantine_dir or settings.quarantine_dir
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_path(self, target_path: Path) -> Path:
        """Validate and resolve target path to prevent traversal and symlink attacks."""
        resolved = Path(target_path).resolve()
        if not resolved.exists():
            raise QuarantineError(f"Target file does not exist: {resolved}")
        if resolved.is_symlink():
            raise QuarantineError("Refusing to quarantine symlink/reparse point for safety.")
        if not resolved.is_file():
            raise QuarantineError(f"Target is not a regular file: {resolved}")
        return resolved

    def quarantine_file(
        self,
        file_path: Path,
        sha256: str,
        reason: str = "Classified as high risk",
        risk_score: int = 0,
    ) -> QuarantineRecord:
        """Atomically isolate a suspicious file into the quarantine repository.

        Args:
            file_path: Absolute path to the original file.
            sha256: SHA-256 hash of the file.
            reason: Primary trigger or threat reason.
            risk_score: Calculated risk score.

        Returns:
            QuarantineRecord describing the isolated entity.
        """
        source = self._sanitize_path(file_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        sanitized_name = f"{sha256[:16]}_{timestamp}.qtn"
        dest_path = self.quarantine_dir / sanitized_name

        try:
            # Atomic move into quarantine
            shutil.move(str(source), str(dest_path))

            # Strip write and execute permissions to neutralize executable launch capability
            try:
                os.chmod(str(dest_path), stat.S_IREAD)
            except Exception as perm_err:
                logger.warning(f"Could not adjust quarantine permissions: {perm_err}")

            # Create sidecar metadata file for disaster recovery
            meta_path = dest_path.with_suffix(".qmeta")
            metadata = {
                "original_path": str(source),
                "quarantine_path": str(dest_path),
                "sha256": sha256,
                "reason": reason,
                "risk_score": risk_score,
                "timestamp": datetime.utcnow().isoformat(),
            }
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(metadata, mf, indent=2)

            record = QuarantineRecord(
                original_path=str(source),
                quarantine_path=str(dest_path),
                sha256=sha256,
                reason=reason,
                risk_score=risk_score,
                created_at=metadata["timestamp"],
                status="QUARANTINED",
            )
            record_id = db.add_quarantine_record(record)
            record.id = record_id

            logger.info(f"Successfully quarantined '{source}' -> '{dest_path}'")
            return record

        except Exception as e:
            logger.error(f"Failed to quarantine '{source}': {e}")
            # If move failed halfway, attempt restore
            if dest_path.exists() and not source.exists():
                shutil.move(str(dest_path), str(source))
            raise QuarantineError(f"Quarantine failed: {e}") from e

    def restore_file(self, quarantine_id: int) -> bool:
        """Safely restore a quarantined file back to its original path."""
        records = db.get_quarantine_records()
        target_record = next((r for r in records if r.id == quarantine_id), None)

        if not target_record:
            raise QuarantineError(f"Quarantine record #{quarantine_id} not found.")

        q_path = Path(target_record.quarantine_path)
        orig_path = Path(target_record.original_path)

        if not q_path.exists():
            raise QuarantineError(f"Quarantined storage file missing: {q_path}")

        orig_dir = orig_path.parent
        orig_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Restore standard read/write permissions prior to move
            try:
                os.chmod(str(q_path), stat.S_IREAD | stat.S_IWRITE)
            except Exception as perm_err:
                logger.debug(f"Could not change permissions before restore: {perm_err}")

            shutil.move(str(q_path), str(orig_path))

            # Clean up sidecar .qmeta
            meta_path = q_path.with_suffix(".qmeta")
            if meta_path.exists():
                meta_path.unlink()

            db.update_quarantine_status(quarantine_id, "RESTORED")
            logger.info(f"Restored file '{orig_path}' from quarantine.")
            return True
        except Exception as e:
            logger.error(f"Failed to restore file #{quarantine_id}: {e}")
            raise QuarantineError(f"Restore failed: {e}") from e

    def permanently_delete(self, quarantine_id: int) -> bool:
        """Securely shred and permanently remove a quarantined file."""
        records = db.get_quarantine_records()
        target_record = next((r for r in records if r.id == quarantine_id), None)

        if not target_record:
            raise QuarantineError(f"Quarantine record #{quarantine_id} not found.")

        q_path = Path(target_record.quarantine_path)

        try:
            if q_path.exists():
                # Allow write so we can overwrite/delete
                try:
                    os.chmod(str(q_path), stat.S_IREAD | stat.S_IWRITE)
                except Exception as perm_err:
                    logger.debug(f"Could not adjust permissions before shredding: {perm_err}")

                # Secure zero-overwrite before unlinking
                file_size = q_path.stat().st_size
                if file_size > 0:
                    with open(q_path, "ba+", buffering=0) as f:
                        f.seek(0)
                        f.write(b"\x00" * min(file_size, 4096 * 10))

                q_path.unlink()

            # Clean up sidecar .qmeta
            meta_path = q_path.with_suffix(".qmeta")
            if meta_path.exists():
                meta_path.unlink()

            db.update_quarantine_status(quarantine_id, "DELETED")
            logger.info(f"Permanently purged quarantine entry #{quarantine_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete quarantine file #{quarantine_id}: {e}")
            raise QuarantineError(f"Deletion failed: {e}") from e

    def list_quarantined(self) -> list[QuarantineRecord]:
        """Fetch active quarantined items from database."""
        return db.get_quarantine_records(status="QUARANTINED")


# Global quarantine manager instance
quarantine_manager = QuarantineManager()
