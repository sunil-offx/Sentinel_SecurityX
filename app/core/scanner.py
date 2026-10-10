"""Core scanner orchestrating hashing, static analysis, YARA detection, and database storage."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.config.settings import settings
from app.core.analyzer import StaticAnalysisResult, static_analyzer
from app.core.hasher import FileMetadata, calculate_hashes_and_metadata
from app.core.risk_engine import RiskAssessmentResult, risk_engine
from app.database.database import db
from app.database.models import ScannedFileRecord
from app.detection.yara_engine import YaraMatch, yara_engine
from app.ml.classifier import MLPredictionResult, pe_classifier

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Full consolidated scan output for a single file."""

    metadata: FileMetadata
    static_analysis: StaticAnalysisResult
    yara_matches: list[YaraMatch]
    assessment: RiskAssessmentResult
    ml_prediction: MLPredictionResult | None = None
    db_record_id: int | None = None
    error: str | None = None


ProgressCallback = Callable[[int, int, str, ScanResult | None], None]


class FileScanner:
    """Orchestrates file scanning, analysis pipelines, and scan results persistence."""

    def __init__(
        self,
        monitored_extensions: set[str] | None = None,
        save_to_db: bool = True,
    ) -> None:
        self.monitored_extensions = monitored_extensions or settings.monitored_extensions
        self.save_to_db = save_to_db
        self._cancel_requested = False

    def request_cancel(self) -> None:
        """Signal ongoing scan to stop at the next file."""
        self._cancel_requested = True

    def scan_file(self, file_path: Path) -> ScanResult:
        """Scan a single file through the entire SentinelX detection pipeline."""
        resolved = Path(file_path).resolve()
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError(f"File not found: {resolved}")

        # 1. Hashing & basic metadata
        metadata = calculate_hashes_and_metadata(resolved)

        # 2. Static inspection (entropy, PE structures, script patterns)
        analysis = static_analyzer.analyze(resolved)

        # 3. YARA rule matching
        yara_matches = yara_engine.scan_file(resolved)

        # 4. Phase 2: Machine Learning PE classification
        ml_prediction: MLPredictionResult | None = None
        if settings.ml_enabled and (
            analysis.is_pe or resolved.suffix.lower() in {".exe", ".dll", ".sys", ".scr"}
        ):
            try:
                ml_prediction = pe_classifier.predict(resolved)
            except Exception as e:
                logger.warning(f"ML evaluation failed for {resolved}: {e}")

        # 5. Multi-factor Risk scoring
        assessment = risk_engine.evaluate(
            metadata, analysis, yara_matches, ml_prediction=ml_prediction
        )

        # 6. Persist record to SQLite
        db_id = None
        if self.save_to_db:
            record = ScannedFileRecord(
                path=str(metadata.path),
                sha256=metadata.sha256,
                md5=metadata.md5,
                sha1=metadata.sha1,
                size=metadata.size,
                risk_score=assessment.risk_score,
                risk_level=assessment.risk_level.value,
                file_type=metadata.file_type,
                detections=assessment.detections,
            )
            db_id = db.add_scan_result(record)

        return ScanResult(
            metadata=metadata,
            static_analysis=analysis,
            yara_matches=yara_matches,
            assessment=assessment,
            ml_prediction=ml_prediction,
            db_record_id=db_id,
        )


    def scan_directory(
        self,
        dir_path: Path,
        filter_extensions: bool = True,
        progress_cb: ProgressCallback | None = None,
    ) -> list[ScanResult]:
        """Recursively scan an entire directory.

        Args:
            dir_path: Target directory path.
            filter_extensions: If True, only scan monitored extensions.
            progress_cb: Callback function(current_count, total_count, current_file, scan_result).

        Returns:
            List of ScanResult objects.
        """
        self._cancel_requested = False
        target_dir = Path(dir_path).resolve()
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: {target_dir}")

        # Gather target files
        candidate_files: list[Path] = []
        for p in target_dir.rglob("*"):
            if self._cancel_requested:
                break
            if p.is_file():
                if not filter_extensions or p.suffix.lower() in self.monitored_extensions:
                    candidate_files.append(p)

        total_files = len(candidate_files)
        results: list[ScanResult] = []

        for idx, file_path in enumerate(candidate_files, start=1):
            if self._cancel_requested:
                logger.info("Scan cancelled by user.")
                break

            try:
                res = self.scan_file(file_path)
                results.append(res)
                if progress_cb:
                    progress_cb(idx, total_files, str(file_path), res)
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")
                if progress_cb:
                    progress_cb(idx, total_files, str(file_path), None)

        return results


# Global file scanner instance
file_scanner = FileScanner()
