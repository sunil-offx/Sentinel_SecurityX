import sys
from pathlib import Path

from pydantic import BaseModel, Field


def _get_app_root() -> Path:
    """Return root directory for application resources, supporting PyInstaller bundles."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "app"
    return Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """Central configuration for SentinelX."""

    app_name: str = "SentinelX"
    version: str = "0.3.0"
    environment: str = "development"
    debug: bool = True

    # Base paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx")
    quarantine_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "quarantine")
    logs_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "logs")
    db_path: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "sentinelx.db")
    yara_rules_dir: Path = Field(
        default_factory=lambda: _get_app_root() / "detection" / "rules"
    )


    # Monitored directory
    downloads_dir: Path = Field(default_factory=lambda: Path.home() / "Downloads")

    # Monitored extensions for Phase 1 MVP
    monitored_extensions: set[str] = {
        ".exe",
        ".dll",
        ".msi",
        ".bat",
        ".cmd",
        ".ps1",
        ".vbs",
        ".js",
        ".scr",
    }

    # Thresholds
    threshold_safe_max: int = 29
    threshold_low_max: int = 59
    threshold_high_max: int = 79
    # 80-100 is CRITICAL

    # Risk Weights
    weight_entropy: int = 25
    weight_suspicious_api: int = 35
    weight_yara: int = 40
    weight_extension: int = 15
    weight_ml: int = 30

    # Analyzer configuration
    entropy_threshold_high: float = 7.1
    entropy_threshold_medium: float = 6.4
    max_scan_size_bytes: int = 250 * 1024 * 1024  # 250 MB max per single file

    # Phase 2: Machine Learning PE Classifier
    ml_models_dir: Path = Field(
        default_factory=lambda: _get_app_root() / "ml" / "models"
    )
    ml_model_path: Path = Field(
        default_factory=lambda: _get_app_root() / "ml" / "models" / "pe_classifier.joblib"
    )

    ml_malware_threshold: float = 0.65
    ml_enabled: bool = True

    # Phase 2: Real-Time Process Monitor
    process_monitor_enabled: bool = True
    process_poll_interval_sec: float = 3.0

    # Phase 3: Outbound Network Telemetry
    network_monitor_enabled: bool = True
    network_poll_interval_sec: float = 4.0

    # Phase 3: Threat Intelligence
    threat_intel_credentials_path: Path = Field(
        default_factory=lambda: Path.home() / ".sentinelx" / "credentials.json"
    )
    threat_intel_cache_ttl_hours: int = 24

    # Phase 3: Windows Event Log Telemetry
    event_log_monitor_enabled: bool = True
    event_log_poll_interval_sec: float = 10.0

    def ensure_directories(self) -> None:
        """Create necessary application directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.ml_models_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

