"""Real-time process monitor view displaying process tree, suspicious behaviors, and termination controls."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database.models import RiskLevel
from app.monitoring.process_monitor import ProcessInfo, process_monitor
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_HIGH,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    get_risk_badge_style,
)


class ProcessView(QWidget):
    """Interactive real-time process monitoring and threat inspection view."""

    def __init__(self) -> None:
        super().__init__()
        self.processes: list[ProcessInfo] = []
        self.selected_process: ProcessInfo | None = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_processes)

        self._init_ui()
        self.refresh_processes()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 1. Header Toolbar
        header_card = QFrame()
        header_card.setProperty("class", "content-card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title_layout = QVBoxLayout()
        title_lbl = QLabel("Real-Time Process Monitor")
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        sub_lbl = QLabel("Continuous inspection of process hierarchies, LOLBins, and living-off-the-land techniques.")
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        h_layout.addLayout(title_layout)
        h_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name or PID...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self._apply_filter)
        h_layout.addWidget(self.search_input)

        self.chk_suspicious_only = QCheckBox("Suspicious Only")
        self.chk_suspicious_only.setStyleSheet(f"color: {COLOR_HIGH}; font-weight: bold;")
        self.chk_suspicious_only.toggled.connect(self._apply_filter)
        h_layout.addWidget(self.chk_suspicious_only)

        self.chk_auto_refresh = QCheckBox("Auto-Refresh (3s)")
        self.chk_auto_refresh.setStyleSheet(f"color: {COLOR_ACCENT_CYAN};")
        self.chk_auto_refresh.setChecked(True)
        self.chk_auto_refresh.toggled.connect(self._toggle_auto_refresh)
        h_layout.addWidget(self.chk_auto_refresh)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setProperty("class", "secondary-btn")
        btn_refresh.clicked.connect(self.refresh_processes)
        h_layout.addWidget(btn_refresh)

        layout.addWidget(header_card)

        # 2. Main Content Splitter (Table + Inspection Pane)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Process Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "PID", "Process Name", "PPID", "Parent Name", "Memory (MB)", "Risk Level", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_process_selected)
        splitter.addWidget(self.table)

        # Inspection Details Side Panel
        detail_panel = QFrame()
        detail_panel.setProperty("class", "content-card")
        detail_panel.setFixedWidth(340)
        d_layout = QVBoxLayout(detail_panel)
        d_layout.setContentsMargins(14, 14, 14, 14)
        d_layout.setSpacing(10)

        d_title = QLabel("PROCESS DIAGNOSTICS")
        d_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: bold;")
        d_layout.addWidget(d_title)

        self.lbl_proc_name = QLabel("No process selected")
        self.lbl_proc_name.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        d_layout.addWidget(self.lbl_proc_name)

        self.lbl_risk_badge = QLabel("SAFE")
        self.lbl_risk_badge.setStyleSheet(get_risk_badge_style(RiskLevel.SAFE.value))
        self.lbl_risk_badge.setFixedWidth(80)
        d_layout.addWidget(self.lbl_risk_badge)

        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setPlaceholderText("Select a process from the table to view execution path, command line arguments, and behavioral threat analysis.")
        d_layout.addWidget(self.txt_details)

        self.btn_terminate = QPushButton("🛑 Terminate Process")
        self.btn_terminate.setProperty("class", "danger-btn")
        self.btn_terminate.setEnabled(False)
        self.btn_terminate.clicked.connect(self._terminate_selected_process)
        d_layout.addWidget(self.btn_terminate)

        splitter.addWidget(detail_panel)
        splitter.setSizes([750, 350])
        layout.addWidget(splitter)

        if self.chk_auto_refresh.isChecked():
            self.timer.start(3000)

    def _toggle_auto_refresh(self, enabled: bool) -> None:
        if enabled:
            self.timer.start(3000)
        else:
            self.timer.stop()

    def refresh_processes(self) -> None:
        """Fetch fresh process snapshot from process_monitor."""
        self.processes = process_monitor.get_process_snapshot()
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Filter and populate process table."""
        search_text = self.search_input.text().strip().lower()
        suspicious_only = self.chk_suspicious_only.isChecked()

        filtered = []
        for p in self.processes:
            if suspicious_only and not p.is_suspicious:
                continue
            if search_text:
                if search_text not in p.name.lower() and search_text not in str(p.pid):
                    continue
            filtered.append(p)

        # Sort so suspicious and critical processes appear at top
        filtered.sort(
            key=lambda x: (
                0 if x.risk_level == RiskLevel.CRITICAL.value
                else 1 if x.risk_level == RiskLevel.HIGH.value
                else 2 if x.is_suspicious
                else 3,
                x.name.lower(),
            )
        )

        self.table.setRowCount(len(filtered))
        for row, p in enumerate(filtered):
            item_pid = QTableWidgetItem(str(p.pid))
            item_name = QTableWidgetItem(p.name)
            item_ppid = QTableWidgetItem(str(p.ppid))
            item_parent = QTableWidgetItem(p.parent_name or "—")
            item_mem = QTableWidgetItem(f"{p.memory_mb:.1f} MB")
            item_risk = QTableWidgetItem(p.risk_level)
            item_status = QTableWidgetItem(p.status)

            # Store process object in item user role
            item_name.setData(Qt.ItemDataRole.UserRole, p)

            # Highlight suspicious items
            if p.risk_level == RiskLevel.CRITICAL.value:
                item_name.setForeground(Qt.GlobalColor.red)
                item_risk.setForeground(Qt.GlobalColor.red)
            elif p.risk_level == RiskLevel.HIGH.value:
                item_name.setForeground(Qt.GlobalColor.yellow)
                item_risk.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row, 0, item_pid)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_ppid)
            self.table.setItem(row, 3, item_parent)
            self.table.setItem(row, 4, item_mem)
            self.table.setItem(row, 5, item_risk)
            self.table.setItem(row, 6, item_status)

    def _on_process_selected(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            self.selected_process = None
            self.btn_terminate.setEnabled(False)
            return

        row = self.table.currentRow()
        item = self.table.item(row, 1)
        if not item:
            return

        proc: ProcessInfo = item.data(Qt.ItemDataRole.UserRole)
        self.selected_process = proc
        self.lbl_proc_name.setText(f"{proc.name} (PID: {proc.pid})")
        self.lbl_risk_badge.setText(proc.risk_level)
        self.lbl_risk_badge.setStyleSheet(get_risk_badge_style(proc.risk_level))
        self.btn_terminate.setEnabled(True)

        details = []
        details.append(f"PID: {proc.pid}")
        details.append(f"PPID: {proc.ppid} ({proc.parent_name or 'Unknown'})")
        details.append(f"Executable: {proc.exe_path or 'Unavailable'}")
        details.append(f"Command Line:\n{proc.cmdline or 'Unavailable'}\n")
        details.append(f"Memory (RSS): {proc.memory_mb:.2f} MB")
        details.append(f"CPU: {proc.cpu_percent:.1f}%")
        details.append(f"User: {proc.username or 'System'}")

        if proc.reasons:
            details.append("\n⚠️ TRIGGERED THREAT HEURISTICS:")
            for r in proc.reasons:
                details.append(f"• {r}")
        else:
            details.append("\nNo anomalous behavioral traits detected.")

        self.txt_details.setText("\n".join(details))

    def _terminate_selected_process(self) -> None:
        if not self.selected_process:
            return

        proc = self.selected_process
        reply = QMessageBox.question(
            self,
            "Confirm Process Termination",
            f"Are you sure you want to terminate process '{proc.name}' (PID: {proc.pid})?\n\n"
            "This will immediately halt execution.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = process_monitor.terminate_process(proc.pid)
            if success:
                QMessageBox.information(self, "Process Terminated", msg)
                self.refresh_processes()
            else:
                QMessageBox.warning(self, "Termination Failed", msg)
