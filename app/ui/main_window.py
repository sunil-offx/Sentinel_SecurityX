"""Main window application shell with sidebar navigation, view stack, and status controls."""

from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.monitoring.download_monitor import download_monitor
from app.monitoring.event_log_monitor import event_log_monitor
from app.monitoring.network_monitor import network_monitor
from app.monitoring.process_monitor import process_monitor
from app.ui.dashboard import DashboardView
from app.ui.endpoint_view import EndpointView
from app.ui.history_view import HistoryView
from app.ui.process_view import ProcessView
from app.ui.quarantine_view import QuarantineView
from app.ui.scanner_view import ScannerView
from app.ui.settings_view import SettingsView
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_SAFE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    MAIN_STYLESHEET,
)


class MainWindow(QMainWindow):
    """Primary application window for SentinelX."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SentinelX — AI-Powered Local Malware & Intrusion Detection System")
        self.resize(1240, 800)
        self.setMinimumSize(1020, 680)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._init_ui()
        self._connect_signals()

        # Start defense background monitors
        download_monitor.start()
        process_monitor.start()
        network_monitor.start()
        event_log_monitor.start()


    def _init_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Sidebar Navigation
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(8)

        # Brand / Logo Header
        brand_layout = QHBoxLayout()
        logo_icon = QLabel("🛡️")
        logo_icon.setStyleSheet("font-size: 24px;")
        brand_layout.addWidget(logo_icon)

        brand_text_layout = QVBoxLayout()
        brand_title = QLabel("SENTINELX")
        brand_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 16px; font-weight: 800; letter-spacing: 1px;"
        )
        brand_sub = QLabel("LOCAL DEFENSE")
        brand_sub.setStyleSheet(
            f"color: {COLOR_ACCENT_CYAN}; font-size: 9px; font-weight: bold; letter-spacing: 1.5px;"
        )
        brand_text_layout.addWidget(brand_title)
        brand_text_layout.addWidget(brand_sub)
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()
        sidebar_layout.addLayout(brand_layout)

        sidebar_layout.addSpacing(20)

        # Navigation Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_dashboard = QPushButton("📊  Dashboard")
        self.btn_nav_dashboard.setProperty("class", "nav-btn")
        self.btn_nav_dashboard.setCheckable(True)
        self.btn_nav_dashboard.setChecked(True)
        self.nav_group.addButton(self.btn_nav_dashboard, 0)
        sidebar_layout.addWidget(self.btn_nav_dashboard)

        self.btn_nav_scanner = QPushButton("🔍  File Scanner")
        self.btn_nav_scanner.setProperty("class", "nav-btn")
        self.btn_nav_scanner.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_scanner, 1)
        sidebar_layout.addWidget(self.btn_nav_scanner)

        self.btn_nav_process = QPushButton("⚡  Process Monitor")
        self.btn_nav_process.setProperty("class", "nav-btn")
        self.btn_nav_process.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_process, 2)
        sidebar_layout.addWidget(self.btn_nav_process)

        self.btn_nav_endpoint = QPushButton("🌐  Endpoint Telemetry")
        self.btn_nav_endpoint.setProperty("class", "nav-btn")
        self.btn_nav_endpoint.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_endpoint, 3)
        sidebar_layout.addWidget(self.btn_nav_endpoint)

        self.btn_nav_quarantine = QPushButton("📦  Quarantine Vault")
        self.btn_nav_quarantine.setProperty("class", "nav-btn")
        self.btn_nav_quarantine.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_quarantine, 4)
        sidebar_layout.addWidget(self.btn_nav_quarantine)

        self.btn_nav_history = QPushButton("📜  Scan History")
        self.btn_nav_history.setProperty("class", "nav-btn")
        self.btn_nav_history.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_history, 5)
        sidebar_layout.addWidget(self.btn_nav_history)

        self.btn_nav_settings = QPushButton("⚙️  Settings")
        self.btn_nav_settings.setProperty("class", "nav-btn")
        self.btn_nav_settings.setCheckable(True)
        self.nav_group.addButton(self.btn_nav_settings, 6)
        sidebar_layout.addWidget(self.btn_nav_settings)

        sidebar_layout.addStretch()

        # Sidebar Footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet("border-top: 1px solid #1e293b; padding-top: 12px;")
        f_layout = QVBoxLayout(footer_frame)
        f_layout.setContentsMargins(0, 0, 0, 0)
        f_layout.setSpacing(4)

        status_chip = QLabel("🟢  PROTECTION ACTIVE")
        status_chip.setStyleSheet(f"color: {COLOR_SAFE}; font-size: 11px; font-weight: bold;")
        ver_lbl = QLabel("SentinelX v0.3.0 (Phases 1-3)")
        ver_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")

        f_layout.addWidget(status_chip)
        f_layout.addWidget(ver_lbl)
        sidebar_layout.addWidget(footer_frame)

        root_layout.addWidget(sidebar)

        # 2. Main Content Area (Top bar + View Stack)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QWidget()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(54)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(24, 0, 24, 0)

        self.lbl_view_title = QLabel("SYSTEM OVERVIEW")
        self.lbl_view_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: bold; letter-spacing: 0.5px;"
        )
        tb_layout.addWidget(self.lbl_view_title)
        tb_layout.addStretch()

        shield_status = QLabel("🛡️ Local Security Shield: ONLINE")
        shield_status.setStyleSheet(
            f"color: {COLOR_SAFE}; font-size: 12px; font-weight: 600; background-color: #064e3b; padding: 4px 12px; border-radius: 12px; border: 1px solid {COLOR_SAFE};"
        )
        tb_layout.addWidget(shield_status)

        content_layout.addWidget(top_bar)

        # View Stack
        self.stack = QStackedWidget()
        self.view_dashboard = DashboardView()
        self.view_scanner = ScannerView()
        self.view_process = ProcessView()
        self.view_endpoint = EndpointView()
        self.view_quarantine = QuarantineView()
        self.view_history = HistoryView()
        self.view_settings = SettingsView()

        self.stack.addWidget(self.view_dashboard)  # 0
        self.stack.addWidget(self.view_scanner)  # 1
        self.stack.addWidget(self.view_process)  # 2
        self.stack.addWidget(self.view_endpoint)  # 3
        self.stack.addWidget(self.view_quarantine)  # 4
        self.stack.addWidget(self.view_history)  # 5
        self.stack.addWidget(self.view_settings)  # 6

        content_layout.addWidget(self.stack, 1)
        root_layout.addWidget(content_container, 1)

    def _connect_signals(self) -> None:
        self.nav_group.idClicked.connect(self._on_nav_clicked)

        # Dashboard quick actions
        self.view_dashboard.navigate_to_scanner.connect(self._switch_to_scanner_with_mode)
        self.view_dashboard.navigate_to_quarantine.connect(lambda: self._switch_to_index(4))

        # Scan notifications
        self.view_scanner.scan_completed_notify.connect(self.view_dashboard.refresh_data)
        self.view_scanner.scan_completed_notify.connect(self.view_history.refresh_history)
        self.view_scanner.scan_completed_notify.connect(self.view_quarantine.refresh_quarantine)

        # Quarantine events
        self.view_quarantine.quarantine_changed.connect(self.view_dashboard.refresh_data)
        self.view_quarantine.quarantine_changed.connect(self.view_history.refresh_history)

    def _on_nav_clicked(self, view_id: int) -> None:
        self._switch_to_index(view_id)

    def _switch_to_index(self, index: int) -> None:
        titles = {
            0: "SYSTEM OVERVIEW",
            1: "THREAT SCANNER",
            2: "REAL-TIME PROCESS MONITOR",
            3: "ENDPOINT & NETWORK TELEMETRY",
            4: "QUARANTINE VAULT",
            5: "SCAN & DETECTION AUDIT LOG",
            6: "SYSTEM PREFERENCES",
        }
        self.stack.setCurrentIndex(index)
        self.lbl_view_title.setText(titles.get(index, "SENTINELX"))

        btn = self.nav_group.button(index)
        if btn:
            btn.setChecked(True)

        # Refresh target view
        if index == 0:
            self.view_dashboard.refresh_data()
        elif index == 2:
            self.view_process.refresh_processes()
        elif index == 3:
            self.view_endpoint.refresh_network_connections()
            self.view_endpoint.refresh_event_logs()
        elif index == 4:
            self.view_quarantine.refresh_quarantine()
        elif index == 5:
            self.view_history.refresh_history()

    def _switch_to_scanner_with_mode(self, mode: str) -> None:
        self._switch_to_index(1)
        self.view_scanner.select_mode(mode)

    def closeEvent(self, event) -> None:
        """Handle clean application shutdown."""
        download_monitor.stop()
        process_monitor.stop()
        network_monitor.stop()
        event_log_monitor.stop()
        super().closeEvent(event)

