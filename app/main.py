"""Entry point for SentinelX Application."""

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.config.settings import settings
from app.ui.main_window import MainWindow


def setup_logging() -> None:
    """Initialize structured logging to file and standard output."""
    settings.ensure_directories()
    log_file = settings.logs_dir / "sentinelx.log"

    logging.basicConfig(
        level=logging.INFO if not settings.debug else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8"),
        ],
    )


def main() -> int:
    """Launch SentinelX GUI Application."""
    setup_logging()
    logger = logging.getLogger("SentinelX")
    logger.info("Initializing SentinelX — AI-Powered Local Malware & Intrusion Detection System")

    # High DPI scaling configuration
    app = QApplication(sys.argv)
    app.setApplicationName("SentinelX")
    app.setApplicationVersion(settings.version)
    app.setOrganizationName("SentinelX Security")

    window = MainWindow()
    window.show()

    logger.info("SentinelX GUI launched successfully.")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
