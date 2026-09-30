"""Background directory monitor observing Downloads folder for incoming suspicious files."""

import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path

from app.config.settings import settings
from app.core.scanner import ScanResult, file_scanner

logger = logging.getLogger(__name__)

ThreatCallback = Callable[[ScanResult], None]


class DownloadMonitor:
    """Monitors downloads or designated directories for newly added files."""

    def __init__(
        self,
        watch_dir: Path | None = None,
        monitored_extensions: set[str] | None = None,
        poll_interval_seconds: float = 2.0,
        on_threat_detected: ThreatCallback | None = None,
        on_file_scanned: Callable[[ScanResult], None] | None = None,
    ) -> None:
        self.watch_dir = Path(watch_dir or settings.downloads_dir).resolve()
        self.monitored_extensions = monitored_extensions or settings.monitored_extensions
        self.poll_interval = poll_interval_seconds
        self.on_threat_detected = on_threat_detected
        self.on_file_scanned = on_file_scanned

        self._is_running = False
        self._thread: threading.Thread | None = None
        self._seen_files: set[str] = set()
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Check if monitor is currently active."""
        return self._is_running

    def start(self) -> bool:
        """Start the background monitoring thread."""
        with self._lock:
            if self._is_running:
                return True

            if not self.watch_dir.exists():
                try:
                    self.watch_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"Cannot create monitor directory {self.watch_dir}: {e}")
                    return False

            # Snapshot existing files so we don't spam-alert on files already there
            self._seen_files = {str(p.resolve()) for p in self.watch_dir.iterdir() if p.is_file()}

            self._is_running = True
            self._thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="SentinelX-DownloadMonitor",
            )
            self._thread.start()
            logger.info(f"Download monitor started watching: {self.watch_dir}")
            return True

    def stop(self) -> None:
        """Stop the background monitor thread."""
        with self._lock:
            self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
            logger.info("Download monitor stopped.")

    def _monitor_loop(self) -> None:
        """Polling loop observing new files."""
        while self._is_running:
            try:
                if self.watch_dir.exists():
                    current_items = list(self.watch_dir.iterdir())
                    for item in current_items:
                        if not self._is_running:
                            break

                        str_path = str(item.resolve())
                        if str_path not in self._seen_files:
                            self._seen_files.add(str_path)

                            # Skip directories or active download temp files
                            if not item.is_file():
                                continue
                            if item.suffix.lower() in {".tmp", ".crdownload", ".part"}:
                                continue

                            if item.suffix.lower() in self.monitored_extensions:
                                self._handle_new_file(item)

            except Exception as e:
                logger.error(f"Error in download monitor loop: {e}")

            time.sleep(self.poll_interval)

    def _handle_new_file(self, file_path: Path) -> None:
        """Process and scan a newly discovered file."""
        # Wait briefly in case file is still being flushed to disk by browser
        time.sleep(0.5)
        try:
            logger.info(f"Monitor caught new file for inspection: {file_path.name}")
            result = file_scanner.scan_file(file_path)

            if self.on_file_scanned:
                self.on_file_scanned(result)

            if result.assessment.risk_level.value in ("HIGH", "CRITICAL"):
                logger.warning(
                    f"Threat detected by monitor in '{file_path.name}': {result.assessment.risk_level.value}"
                )
                if self.on_threat_detected:
                    self.on_threat_detected(result)

        except Exception as e:
            logger.error(f"Failed to analyze newly discovered file {file_path}: {e}")


# Global monitor instance
download_monitor = DownloadMonitor()
