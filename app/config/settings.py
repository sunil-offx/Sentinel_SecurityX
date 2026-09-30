"""Application configuration and settings for SentinelX."""

from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Central configuration for SentinelX."""

    app_name: str = "SentinelX"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # Base paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx")
    quarantine_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "quarantine")
    logs_dir: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "logs")
    db_path: Path = Field(default_factory=lambda: Path.home() / ".sentinelx" / "sentinelx.db")
    yara_rules_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "detection" / "rules"
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

    # Analyzer configuration
    entropy_threshold_high: float = 7.1
    entropy_threshold_medium: float = 6.4
    max_scan_size_bytes: int = 250 * 1024 * 1024  # 250 MB max per single file

    def ensure_directories(self) -> None:
        """Create necessary application directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
