"""UI package for SentinelX."""

from app.ui.dashboard import DashboardView
from app.ui.history_view import HistoryView
from app.ui.main_window import MainWindow
from app.ui.quarantine_view import QuarantineView
from app.ui.scanner_view import ScannerView
from app.ui.settings_view import SettingsView

__all__ = [
    "MainWindow",
    "DashboardView",
    "ScannerView",
    "QuarantineView",
    "HistoryView",
    "SettingsView",
]
