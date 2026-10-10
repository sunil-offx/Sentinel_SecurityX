"""Endpoint & Network Telemetry view combining Outbound Sockets, Threat Intel, and Event Logs."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database.database import db
from app.database.models import RiskLevel
from app.monitoring.event_log_monitor import event_log_monitor
from app.monitoring.network_monitor import NetworkConnectionInfo, network_monitor
from app.threat_intel.key_store import key_store
from app.threat_intel.threat_client import ThreatReport, threat_client
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_HIGH,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)


class EndpointView(QWidget):
    """Integrated view for Outbound Network Telemetry, Threat Intel, and Windows Event Logs."""

    def __init__(self) -> None:
        super().__init__()
        self.connections: list[NetworkConnectionInfo] = []

        self.net_timer = QTimer(self)
        self.net_timer.timeout.connect(self.refresh_network_connections)

        self._init_ui()
        self.refresh_network_connections()
        self.refresh_event_logs()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Tab Container
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #111827;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #0f172a;
                color: #94a3b8;
                padding: 10px 20px;
                font-weight: 600;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #111827;
                color: #38bdf8;
                border-bottom: 2px solid #38bdf8;
            }
            """
        )

        # Tab 1: Network Telemetry
        self.tab_network = self._create_network_tab()
        self.tabs.addTab(self.tab_network, "🌐  Network Telemetry")

        # Tab 2: Threat Intelligence
        self.tab_intel = self._create_threat_intel_tab()
        self.tabs.addTab(self.tab_intel, "🛡️  Threat Intelligence Center")

        # Tab 3: Windows Event Logs
        self.tab_events = self._create_event_log_tab()
        self.tabs.addTab(self.tab_events, "📜  Windows Event Logs")

        layout.addWidget(self.tabs)

        if self.chk_net_auto.isChecked():
            self.net_timer.start(4000)

    # --- TAB 1: NETWORK TELEMETRY ---

    def _create_network_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Toolbar
        tb_layout = QHBoxLayout()
        title_lbl = QLabel("Outbound Connection Inspection")
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        tb_layout.addWidget(title_lbl)
        tb_layout.addStretch()

        self.net_search = QLineEdit()
        self.net_search.setPlaceholderText("Filter IP or process...")
        self.net_search.setFixedWidth(180)
        self.net_search.textChanged.connect(self._apply_net_filter)
        tb_layout.addWidget(self.net_search)

        self.chk_net_suspicious = QCheckBox("Suspicious Only")
        self.chk_net_suspicious.setStyleSheet(f"color: {COLOR_HIGH}; font-weight: bold;")
        self.chk_net_suspicious.toggled.connect(self._apply_net_filter)
        tb_layout.addWidget(self.chk_net_suspicious)

        self.chk_net_auto = QCheckBox("Auto-Refresh (4s)")
        self.chk_net_auto.setStyleSheet(f"color: {COLOR_ACCENT_CYAN};")
        self.chk_net_auto.setChecked(True)
        self.chk_net_auto.toggled.connect(self._toggle_net_auto)
        tb_layout.addWidget(self.chk_net_auto)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setProperty("class", "secondary-btn")
        btn_refresh.clicked.connect(self.refresh_network_connections)
        tb_layout.addWidget(btn_refresh)

        layout.addLayout(tb_layout)

        # Network Table
        self.net_table = QTableWidget()
        self.net_table.setColumnCount(7)
        self.net_table.setHorizontalHeaderLabels([
            "PID", "Process Name", "Proto", "Local Address", "Remote Address:Port", "Status", "Risk Level"
        ])
        self.net_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.net_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.net_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.net_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.net_table)

        return widget

    def _toggle_net_auto(self, enabled: bool) -> None:
        if enabled:
            self.net_timer.start(4000)
        else:
            self.net_timer.stop()

    def refresh_network_connections(self) -> None:
        self.connections = network_monitor.get_active_connections()
        self._apply_net_filter()

    def _apply_net_filter(self) -> None:
        search = self.net_search.text().strip().lower()
        suspicious_only = self.chk_net_suspicious.isChecked()

        filtered = []
        for c in self.connections:
            if suspicious_only and not c.is_suspicious:
                continue
            if search:
                if (
                    search not in c.process_name.lower()
                    and search not in c.remote_address
                    and search not in str(c.pid)
                ):
                    continue
            filtered.append(c)

        self.net_table.setRowCount(len(filtered))
        for row, c in enumerate(filtered):
            item_pid = QTableWidgetItem(str(c.pid))
            item_proc = QTableWidgetItem(c.process_name)
            item_proto = QTableWidgetItem(c.protocol)
            item_local = QTableWidgetItem(c.local_address or "—")
            remote_str = f"{c.remote_address}:{c.remote_port}" if c.remote_address else "—"
            item_remote = QTableWidgetItem(remote_str)
            item_status = QTableWidgetItem(c.status)
            item_risk = QTableWidgetItem(c.risk_level)

            if c.risk_level == RiskLevel.CRITICAL.value:
                item_remote.setForeground(Qt.GlobalColor.red)
                item_risk.setForeground(Qt.GlobalColor.red)
            elif c.risk_level == RiskLevel.HIGH.value:
                item_remote.setForeground(Qt.GlobalColor.yellow)
                item_risk.setForeground(Qt.GlobalColor.yellow)

            self.net_table.setItem(row, 0, item_pid)
            self.net_table.setItem(row, 1, item_proc)
            self.net_table.setItem(row, 2, item_proto)
            self.net_table.setItem(row, 3, item_local)
            self.net_table.setItem(row, 4, item_remote)
            self.net_table.setItem(row, 5, item_status)
            self.net_table.setItem(row, 6, item_risk)

    # --- TAB 2: THREAT INTELLIGENCE ---

    def _create_threat_intel_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Search Card
        search_card = QFrame()
        search_card.setProperty("class", "content-card")
        sc_layout = QVBoxLayout(search_card)
        sc_layout.setSpacing(12)

        sc_title = QLabel("Indicator Reputation Lookup (VirusTotal & AbuseIPDB)")
        sc_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        sc_layout.addWidget(sc_title)

        row_in = QHBoxLayout()
        self.txt_indicator = QLineEdit()
        self.txt_indicator.setPlaceholderText("Enter SHA-256 file hash or IPv4 address (e.g., e3b0c442... or 8.8.8.8)")
        row_in.addWidget(self.txt_indicator)

        btn_vt_hash = QPushButton("🔍 Query File Hash")
        btn_vt_hash.setProperty("class", "primary-btn")
        btn_vt_hash.clicked.connect(self._query_hash)
        row_in.addWidget(btn_vt_hash)

        btn_ip = QPushButton("🌐 Query IP Address")
        btn_ip.setProperty("class", "secondary-btn")
        btn_ip.clicked.connect(self._query_ip)
        row_in.addWidget(btn_ip)

        sc_layout.addLayout(row_in)
        layout.addWidget(search_card)

        # Results Display Card
        self.results_card = QFrame()
        self.results_card.setProperty("class", "content-card")
        rc_layout = QVBoxLayout(self.results_card)
        rc_layout.setSpacing(10)

        self.lbl_ti_status = QLabel("Ready for lookup. Enter an indicator above.")
        self.lbl_ti_status.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
        rc_layout.addWidget(self.lbl_ti_status)

        self.txt_ti_output = QTextEdit()
        self.txt_ti_output.setReadOnly(True)
        self.txt_ti_output.setMinimumHeight(140)
        rc_layout.addWidget(self.txt_ti_output)
        layout.addWidget(self.results_card)

        # API Keys Quick Configuration Box
        key_group = QGroupBox("API Keys Configuration")
        key_group.setStyleSheet(
            "QGroupBox { color: #f8fafc; font-weight: bold; border: 1px solid #1e293b; border-radius: 8px; margin-top: 10px; padding: 16px; }"
        )
        k_layout = QVBoxLayout(key_group)
        k_layout.setSpacing(10)

        # VT Key row
        row_vt = QHBoxLayout()
        row_vt.addWidget(QLabel("VirusTotal API Key:"))
        self.txt_vt_key = QLineEdit()
        self.txt_vt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_vt_key.setPlaceholderText("Enter 64-character VirusTotal v3 API key")
        current_vt = key_store.get_api_key("virustotal")
        if current_vt:
            self.txt_vt_key.setText(current_vt)
        row_vt.addWidget(self.txt_vt_key)

        btn_save_vt = QPushButton("Save Key")
        btn_save_vt.clicked.connect(self._save_vt_key)
        row_vt.addWidget(btn_save_vt)
        k_layout.addLayout(row_vt)

        # AbuseIPDB Key row
        row_abuse = QHBoxLayout()
        row_abuse.addWidget(QLabel("AbuseIPDB API Key:"))
        self.txt_abuse_key = QLineEdit()
        self.txt_abuse_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_abuse_key.setPlaceholderText("Enter AbuseIPDB API key")
        current_abuse = key_store.get_api_key("abuseipdb")
        if current_abuse:
            self.txt_abuse_key.setText(current_abuse)
        row_abuse.addWidget(self.txt_abuse_key)

        btn_save_abuse = QPushButton("Save Key")
        btn_save_abuse.clicked.connect(self._save_abuse_key)
        row_abuse.addWidget(btn_save_abuse)
        k_layout.addLayout(row_abuse)

        layout.addWidget(key_group)

        return widget

    def _save_vt_key(self) -> None:
        key = self.txt_vt_key.text().strip()
        key_store.set_api_key("virustotal", key)
        QMessageBox.information(self, "API Key Saved", "VirusTotal API key successfully saved to secure vault.")

    def _save_abuse_key(self) -> None:
        key = self.txt_abuse_key.text().strip()
        key_store.set_api_key("abuseipdb", key)
        QMessageBox.information(self, "API Key Saved", "AbuseIPDB API key successfully saved to secure vault.")

    def _query_hash(self) -> None:
        indicator = self.txt_indicator.text().strip()
        if not indicator:
            QMessageBox.warning(self, "Input Required", "Please enter a SHA-256 hash.")
            return

        report: ThreatReport = threat_client.lookup_file_hash(indicator)
        self._display_threat_report(report)

    def _query_ip(self) -> None:
        indicator = self.txt_indicator.text().strip()
        if not indicator:
            QMessageBox.warning(self, "Input Required", "Please enter an IPv4 address.")
            return

        report: ThreatReport = threat_client.lookup_ip_address(indicator)
        self._display_threat_report(report)

    def _display_threat_report(self, report: ThreatReport) -> None:
        self.lbl_ti_status.setText(f"Status: {report.status} | Indicator: {report.indicator} | Cached: {'Yes' if report.is_cached else 'No'}")

        lines = []
        lines.append(f"Threat Score: {report.score}/100")
        lines.append(f"Security Engines Flagged: {report.malicious_count} / {report.total_engines}")
        if report.suspicious_count:
            lines.append(f"Suspicious Engines: {report.suspicious_count}")
        if report.threat_label:
            lines.append(f"Classification Label: {report.threat_label}")
        lines.append(f"Summary: {report.message}")

        if report.details:
            lines.append("\nAdditional Intelligence Details:")
            for k, v in report.details.items():
                if v:
                    lines.append(f"• {k}: {v}")

        self.txt_ti_output.setText("\n".join(lines))

    # --- TAB 3: WINDOWS EVENT LOGS ---

    def _create_event_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        tb_layout = QHBoxLayout()
        title_lbl = QLabel("Windows Security & Execution Event Logs")
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        tb_layout.addWidget(title_lbl)
        tb_layout.addStretch()

        btn_fetch = QPushButton("🔄 Ingest Recent Logs")
        btn_fetch.setProperty("class", "primary-btn")
        btn_fetch.clicked.connect(self.fetch_live_event_logs)
        tb_layout.addWidget(btn_fetch)

        layout.addLayout(tb_layout)

        self.ev_table = QTableWidget()
        self.ev_table.setColumnCount(5)
        self.ev_table.setHorizontalHeaderLabels([
            "Event ID", "Channel", "Severity", "Detected At", "Message Summary"
        ])
        self.ev_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.ev_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ev_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ev_table.itemSelectionChanged.connect(self._on_event_selected)
        layout.addWidget(self.ev_table)

        # Message Preview
        self.txt_ev_detail = QTextEdit()
        self.txt_ev_detail.setReadOnly(True)
        self.txt_ev_detail.setMaximumHeight(100)
        self.txt_ev_detail.setPlaceholderText("Select an event log above to view full message content.")
        layout.addWidget(self.txt_ev_detail)

        return widget

    def fetch_live_event_logs(self) -> None:
        """Query live Windows event logs via event_log_monitor and update view."""
        events = event_log_monitor.fetch_recent_events(max_events=15)
        for ev in events:
            try:
                db.add_event_log_record(ev)
            except Exception:  # nosec B110
                pass

        self.refresh_event_logs()

    def refresh_event_logs(self) -> None:
        records = db.get_event_log_records(limit=100)
        self.ev_table.setRowCount(len(records))
        for row, r in enumerate(records):
            item_id = QTableWidgetItem(str(r.event_id))
            item_ch = QTableWidgetItem(r.channel)
            item_sev = QTableWidgetItem(r.severity)
            item_time = QTableWidgetItem(r.detected_at[:19].replace("T", " "))
            item_msg = QTableWidgetItem(r.message)

            item_msg.setData(Qt.ItemDataRole.UserRole, r.message)

            if r.severity == RiskLevel.HIGH.value:
                item_sev.setForeground(Qt.GlobalColor.yellow)
            elif r.severity == RiskLevel.CRITICAL.value:
                item_sev.setForeground(Qt.GlobalColor.red)

            self.ev_table.setItem(row, 0, item_id)
            self.ev_table.setItem(row, 1, item_ch)
            self.ev_table.setItem(row, 2, item_sev)
            self.ev_table.setItem(row, 3, item_time)
            self.ev_table.setItem(row, 4, item_msg)

    def _on_event_selected(self) -> None:
        row = self.ev_table.currentRow()
        if row < 0:
            return
        item = self.ev_table.item(row, 4)
        if item:
            full_msg = item.data(Qt.ItemDataRole.UserRole)
            self.txt_ev_detail.setText(str(full_msg))
