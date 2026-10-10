"""Scanner view providing file/folder selection, background worker execution, and inspection."""

import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.quarantine import quarantine_manager
from app.core.scanner import FileScanner, ScanResult
from app.threat_intel.threat_client import ThreatReport, threat_client
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    get_risk_badge_style,
)


class ScanWorker(QThread):
    """Background worker executing file and directory scans without blocking the GUI."""

    progress_updated = Signal(int, int, str, object)  # current, total, path, ScanResult
    scan_finished = Signal(list)  # list of ScanResult
    scan_error = Signal(str)

    def __init__(self, target_path: Path, is_directory: bool) -> None:
        super().__init__()
        self.target_path = target_path
        self.is_directory = is_directory
        self.scanner = FileScanner()

    def run(self) -> None:
        try:
            if not self.is_directory:
                self.progress_updated.emit(0, 1, str(self.target_path), None)
                result = self.scanner.scan_file(self.target_path)
                self.progress_updated.emit(1, 1, str(self.target_path), result)
                self.scan_finished.emit([result])
            else:

                def on_progress(cur: int, tot: int, p: str, res: ScanResult | None) -> None:
                    self.progress_updated.emit(cur, tot, p, res)

                results = self.scanner.scan_directory(self.target_path, progress_cb=on_progress)
                self.scan_finished.emit(results)
        except Exception as e:
            self.scan_error.emit(str(e))

    def cancel(self) -> None:
        self.scanner.request_cancel()


class ScannerView(QWidget):
    """Interactive scanner interface supporting single file and bulk directory inspections."""

    scan_completed_notify = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.worker: ScanWorker | None = None
        self.current_results: list[ScanResult] = []
        self.selected_result: ScanResult | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # 1. Target Selection Bar
        selector_card = QFrame()
        selector_card.setProperty("class", "content-card")
        sel_layout = QVBoxLayout(selector_card)
        sel_layout.setSpacing(12)

        header_lbl = QLabel("Scan Target Configuration")
        header_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
        )
        sel_layout.addWidget(header_lbl)

        mode_layout = QHBoxLayout()
        self.rb_file = QRadioButton("Single File")
        self.rb_file.setChecked(True)
        self.rb_file.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        self.rb_dir = QRadioButton("Entire Directory / Folder")
        self.rb_dir.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        mode_layout.addWidget(self.rb_file)
        mode_layout.addWidget(self.rb_dir)
        mode_layout.addStretch()
        sel_layout.addLayout(mode_layout)

        input_row = QHBoxLayout()
        self.lbl_chosen_path = QLabel("No file or directory selected.")
        self.lbl_chosen_path.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; background-color: #1e293b; padding: 10px 14px; border-radius: 6px; border: 1px solid #334155;"
        )
        input_row.addWidget(self.lbl_chosen_path, 1)

        self.btn_browse = QPushButton("📁 Browse...")
        self.btn_browse.setProperty("class", "btn-secondary")
        self.btn_browse.clicked.connect(self._on_browse)
        input_row.addWidget(self.btn_browse)

        self.btn_start_scan = QPushButton("⚡ Start Scan")
        self.btn_start_scan.setProperty("class", "btn-primary")
        self.btn_start_scan.setEnabled(False)
        self.btn_start_scan.clicked.connect(self._on_start_scan)
        input_row.addWidget(self.btn_start_scan)

        self.btn_cancel = QPushButton("Stop")
        self.btn_cancel.setProperty("class", "btn-danger")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._on_cancel_scan)
        input_row.addWidget(self.btn_cancel)

        sel_layout.addLayout(input_row)

        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        sel_layout.addWidget(self.progress_bar)

        self.lbl_scan_status = QLabel("")
        self.lbl_scan_status.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 11px;")
        self.lbl_scan_status.setVisible(False)
        sel_layout.addWidget(self.lbl_scan_status)

        main_layout.addWidget(selector_card)

        # 2. Results Area: Splitter with File List on left & Detailed Inspection Pane on right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Results Table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl_table_title = QLabel("Inspection Results")
        lbl_table_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        left_layout.addWidget(lbl_table_title)

        self.table_results = QTableWidget()
        self.table_results.setColumnCount(4)
        self.table_results.setHorizontalHeaderLabels(["File Name", "Size", "Risk", "Score"])
        self.table_results.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table_results.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_results.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_results.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_results.verticalHeader().setVisible(False)
        self.table_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_results.itemSelectionChanged.connect(self._on_result_row_selected)
        left_layout.addWidget(self.table_results)
        splitter.addWidget(left_widget)

        # Right side: Detail Inspection Card
        right_widget = QFrame()
        right_widget.setProperty("class", "content-card")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(16, 16, 16, 16)

        lbl_detail_title = QLabel("Threat & Metadata Analysis")
        lbl_detail_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        right_layout.addWidget(lbl_detail_title)

        self.lbl_detail_name = QLabel("Select a file to inspect details")
        self.lbl_detail_name.setWordWrap(True)
        self.lbl_detail_name.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: 600;"
        )
        right_layout.addWidget(self.lbl_detail_name)

        # Risk Badge and Score Display
        badge_row = QHBoxLayout()
        self.lbl_detail_badge = QLabel("WAITING")
        self.lbl_detail_badge.setStyleSheet(get_risk_badge_style("SAFE"))
        badge_row.addWidget(self.lbl_detail_badge)

        self.lbl_detail_score = QLabel("Score: --/100")
        self.lbl_detail_score.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;"
        )
        badge_row.addWidget(self.lbl_detail_score)
        badge_row.addStretch()
        right_layout.addLayout(badge_row)

        # Metadata Details (Hashes, timestamps)
        self.txt_metadata = QTextEdit()
        self.txt_metadata.setReadOnly(True)
        self.txt_metadata.setMaximumHeight(140)
        self.txt_metadata.setStyleSheet(
            "background-color: #0f172a; border: 1px solid #1e293b; color: #cbd5e1; font-family: monospace; font-size: 11px;"
        )
        right_layout.addWidget(self.txt_metadata)

        # Reasons list
        lbl_reasons_header = QLabel("Detections & Reasons:")
        lbl_reasons_header.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-weight: bold; font-size: 12px;"
        )
        right_layout.addWidget(lbl_reasons_header)

        self.txt_reasons = QTextEdit()
        self.txt_reasons.setReadOnly(True)
        self.txt_reasons.setStyleSheet(
            "background-color: #0f172a; border: 1px solid #1e293b; color: #f8fafc; font-size: 12px;"
        )
        right_layout.addWidget(self.txt_reasons)

        # Action Buttons Row
        action_btn_row = QHBoxLayout()

        self.btn_threat_intel = QPushButton("🌐 Check VirusTotal")
        self.btn_threat_intel.setProperty("class", "btn-secondary")
        self.btn_threat_intel.setEnabled(False)
        self.btn_threat_intel.clicked.connect(self._on_check_threat_intel)
        action_btn_row.addWidget(self.btn_threat_intel)

        self.btn_quarantine = QPushButton("🛑 Isolate to Quarantine Vault")
        self.btn_quarantine.setProperty("class", "btn-danger")
        self.btn_quarantine.setEnabled(False)
        self.btn_quarantine.clicked.connect(self._on_quarantine_selected)
        action_btn_row.addWidget(self.btn_quarantine)

        right_layout.addLayout(action_btn_row)


        splitter.addWidget(right_widget)
        splitter.setSizes([450, 450])
        main_layout.addWidget(splitter, 1)

    def select_mode(self, mode: str) -> None:
        """Programmatically switch between 'file' and 'folder' mode."""
        if mode == "file":
            self.rb_file.setChecked(True)
        else:
            self.rb_dir.setChecked(True)
        self._on_browse()

    def _on_browse(self) -> None:
        if self.rb_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Select File to Scan with SentinelX",
                "",
                "Supported Executables and Scripts (*.exe *.dll *.msi *.bat *.cmd *.ps1 *.vbs *.js *.scr);;All Files (*.*)",
            )
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan with SentinelX")

        if path:
            self.lbl_chosen_path.setText(path)
            self.lbl_chosen_path.setToolTip(path)
            self.btn_start_scan.setEnabled(True)

    def _on_start_scan(self) -> None:
        target_str = self.lbl_chosen_path.text()
        target_path = Path(target_str)
        if not target_path.exists():
            QMessageBox.warning(self, "Invalid Path", "Selected target does not exist.")
            return

        is_directory = target_path.is_dir()

        self.current_results.clear()
        self.table_results.setRowCount(0)
        self._clear_detail_panel()

        self.btn_browse.setEnabled(False)
        self.btn_start_scan.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_scan_status.setVisible(True)
        self.lbl_scan_status.setText("Initializing detection engine...")

        self.worker = ScanWorker(target_path, is_directory)
        self.worker.progress_updated.connect(self._on_worker_progress)
        self.worker.scan_finished.connect(self._on_worker_finished)
        self.worker.scan_error.connect(self._on_worker_error)
        self.worker.start()

    def _on_worker_progress(
        self, current: int, total: int, path: str, res: ScanResult | None
    ) -> None:
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            self.lbl_scan_status.setText(f"Scanning [{current}/{total}]: {os.path.basename(path)}")

        if res:
            self.current_results.append(res)
            row = self.table_results.rowCount()
            self.table_results.insertRow(row)

            # Name
            item_name = QTableWidgetItem(res.metadata.file_name)
            item_name.setToolTip(str(res.metadata.path))
            self.table_results.setItem(row, 0, item_name)

            # Size
            item_size = QTableWidgetItem(res.metadata.size_formatted)
            item_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_results.setItem(row, 1, item_size)

            # Risk Badge
            badge = QLabel(res.assessment.risk_level.value)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(get_risk_badge_style(res.assessment.risk_level.value))
            self.table_results.setCellWidget(row, 2, badge)

            # Score
            item_score = QTableWidgetItem(f"{res.assessment.risk_score}")
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_results.setItem(row, 3, item_score)

            if len(self.current_results) == 1:
                self.table_results.selectRow(0)

    def _on_worker_finished(self, results: list[ScanResult]) -> None:
        self.btn_browse.setEnabled(True)
        self.btn_start_scan.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setValue(100)
        self.lbl_scan_status.setText(f"Scan complete. Inspected {len(results)} files.")
        self.scan_completed_notify.emit()

    def _on_worker_error(self, err: str) -> None:
        self.btn_browse.setEnabled(True)
        self.btn_start_scan.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.lbl_scan_status.setText("Scan failed.")
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning: {err}")

    def _on_cancel_scan(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.lbl_scan_status.setText("Scan cancellation requested...")

    def _on_result_row_selected(self) -> None:
        selected_rows = self.table_results.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        if 0 <= row < len(self.current_results):
            self.selected_result = self.current_results[row]
            self._display_result_detail(self.selected_result)

    def _display_result_detail(self, res: ScanResult) -> None:
        self.lbl_detail_name.setText(f"{res.metadata.file_name}\n({res.metadata.path})")
        self.lbl_detail_badge.setText(res.assessment.risk_level.value)
        self.lbl_detail_badge.setStyleSheet(get_risk_badge_style(res.assessment.risk_level.value))
        self.lbl_detail_score.setText(f"Risk Score: {res.assessment.risk_score} / 100")

        # Metadata Text
        meta_lines = [
            f"SHA-256 : {res.metadata.sha256}",
            f"MD5     : {res.metadata.md5}",
            f"SHA-1   : {res.metadata.sha1}",
            f"Size    : {res.metadata.size_formatted} ({res.metadata.size:,} bytes)",
            f"Type    : {res.metadata.file_type}",
            f"Entropy : {res.static_analysis.entropy:.2f} / 8.00 ({res.static_analysis.entropy_level})",
            f"Created : {res.metadata.created_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Modified: {res.metadata.modified_time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if res.ml_prediction and getattr(res.ml_prediction, "is_pe", False):
            meta_lines.append("───────────────────────────────────")
            meta_lines.append(f"AI Model: {res.ml_prediction.model_version}")
            meta_lines.append(
                f"AI Malware Prob: {res.ml_prediction.malware_probability:.1%} ({res.ml_prediction.classification})"
            )
            meta_lines.append(f"AI Confidence: {res.ml_prediction.confidence:.1%}")
            if res.ml_prediction.top_features:
                top_indicators = ", ".join([name for name, _ in res.ml_prediction.top_features[:3]])
                meta_lines.append(f"AI Top Indicators: {top_indicators}")

        self.txt_metadata.setPlainText("\n".join(meta_lines))

        # Reasons
        reasons_formatted = []
        for r in res.assessment.reasons:
            icon = (
                "⚠️"
                if ("Suspicious" in r or "High entropy" in r or "YARA" in r or "Script" in r or "AI" in r)
                else "✓"
            )
            reasons_formatted.append(f"{icon}  {r}")

        self.txt_reasons.setPlainText("\n".join(reasons_formatted))

        # Quarantine and Threat Intel buttons
        file_exists = Path(res.metadata.path).exists()
        self.btn_quarantine.setEnabled(file_exists)
        self.btn_threat_intel.setEnabled(True)

    def _clear_detail_panel(self) -> None:
        self.lbl_detail_name.setText("Select a file to inspect details")
        self.lbl_detail_badge.setText("WAITING")
        self.lbl_detail_badge.setStyleSheet(get_risk_badge_style("SAFE"))
        self.lbl_detail_score.setText("Score: --/100")
        self.txt_metadata.clear()
        self.txt_reasons.clear()
        self.btn_quarantine.setEnabled(False)
        self.btn_threat_intel.setEnabled(False)

    def _on_check_threat_intel(self) -> None:
        if not self.selected_result:
            return

        sha256 = self.selected_result.metadata.sha256
        report: ThreatReport = threat_client.lookup_file_hash(sha256)

        msg = (
            f"Indicator: {report.indicator}\n"
            f"Status: {report.status}\n"
            f"Threat Score: {report.score}/100\n"
            f"Engines Flagged: {report.malicious_count}/{report.total_engines}\n"
            f"Label: {report.threat_label or 'None'}\n"
            f"Summary: {report.message}\n"
            f"Cached: {'Yes' if report.is_cached else 'No'}"
        )
        QMessageBox.information(self, "VirusTotal Reputation Report", msg)


    def _on_quarantine_selected(self) -> None:
        if not self.selected_result:
            return

        target_file = Path(self.selected_result.metadata.path)
        if not target_file.exists():
            QMessageBox.warning(self, "File Not Found", "File is already moved or does not exist.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Isolation",
            f"Are you sure you want to isolate and quarantine:\n\n{target_file.name}\n\n"
            f"This will move the file to SentinelX's secure quarantine vault and remove execute permissions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            quarantine_manager.quarantine_file(
                file_path=target_file,
                sha256=self.selected_result.metadata.sha256,
                reason="; ".join(self.selected_result.assessment.reasons[:2]),
                risk_score=self.selected_result.assessment.risk_score,
            )
            QMessageBox.information(
                self,
                "Quarantine Successful",
                f"Successfully isolated '{target_file.name}' into quarantine vault.",
            )
            self.btn_quarantine.setEnabled(False)
            self.scan_completed_notify.emit()
        except Exception as e:
            QMessageBox.critical(self, "Quarantine Error", f"Failed to isolate file: {e}")
