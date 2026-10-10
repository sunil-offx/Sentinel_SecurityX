"""Settings view for configuring risk score weights, thresholds, and monitoring paths."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import settings
from app.detection.yara_engine import yara_engine
from app.monitoring.download_monitor import download_monitor
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_SAFE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)


class SettingsView(QWidget):
    """Configuration interface for SentinelX."""

    settings_updated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # 1. Detection Thresholds & Weights
        group_thresholds = QGroupBox("Risk Model & Scoring Thresholds")
        group_thresholds.setStyleSheet(
            "QGroupBox { color: #f8fafc; font-weight: bold; border: 1px solid #1e293b; border-radius: 8px; margin-top: 10px; padding: 16px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        t_layout = QVBoxLayout(group_thresholds)
        t_layout.setSpacing(12)

        desc_lbl = QLabel(
            "Configure cutoff thresholds for classifying threat severity levels:\n"
            "• SAFE: 0 to Safe Max\n"
            "• LOW: Safe Max + 1 to Low Max\n"
            "• HIGH: Low Max + 1 to High Max\n"
            "• CRITICAL: High Max + 1 to 100"
        )
        desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        t_layout.addWidget(desc_lbl)

        row_thresh = QHBoxLayout()
        row_thresh.addWidget(QLabel("Safe Max Score:"))
        self.spin_safe = QSpinBox()
        self.spin_safe.setRange(10, 50)
        self.spin_safe.setValue(settings.threshold_safe_max)
        row_thresh.addWidget(self.spin_safe)

        row_thresh.addWidget(QLabel("Low Max Score:"))
        self.spin_low = QSpinBox()
        self.spin_low.setRange(30, 70)
        self.spin_low.setValue(settings.threshold_low_max)
        row_thresh.addWidget(self.spin_low)

        row_thresh.addWidget(QLabel("High Max Score:"))
        self.spin_high = QSpinBox()
        self.spin_high.setRange(60, 95)
        self.spin_high.setValue(settings.threshold_high_max)
        row_thresh.addWidget(self.spin_high)
        row_thresh.addStretch()
        t_layout.addLayout(row_thresh)

        layout.addWidget(group_thresholds)

        # 2. Download Shield & Real-Time Monitoring
        group_mon = QGroupBox("Real-Time Directory Shield")
        group_mon.setStyleSheet(
            "QGroupBox { color: #f8fafc; font-weight: bold; border: 1px solid #1e293b; border-radius: 8px; margin-top: 10px; padding: 16px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        m_layout = QVBoxLayout(group_mon)
        m_layout.setSpacing(12)

        self.chk_monitor_active = QCheckBox("Enable Background Shield on Downloads Directory")
        self.chk_monitor_active.setChecked(download_monitor.is_running)
        self.chk_monitor_active.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        self.chk_monitor_active.toggled.connect(self._toggle_monitor)
        m_layout.addWidget(self.chk_monitor_active)

        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Monitored Folder:"))
        self.txt_watch_dir = QLineEdit(str(download_monitor.watch_dir))
        dir_row.addWidget(self.txt_watch_dir, 1)

        btn_browse_dir = QPushButton("Browse...")
        btn_browse_dir.setProperty("class", "btn-secondary")
        btn_browse_dir.clicked.connect(self._browse_monitor_dir)
        dir_row.addWidget(btn_browse_dir)
        m_layout.addLayout(dir_row)

        layout.addWidget(group_mon)

        # 3. Phase 2: AI & Real-Time Monitoring
        group_p2 = QGroupBox("AI Engine & Real-Time Security (Phase 2)")
        group_p2.setStyleSheet(
            "QGroupBox { color: #f8fafc; font-weight: bold; border: 1px solid #1e293b; border-radius: 8px; margin-top: 10px; padding: 16px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        p2_layout = QVBoxLayout(group_p2)
        p2_layout.setSpacing(10)

        self.chk_ml_active = QCheckBox("Enable AI Machine Learning PE Classifier (EMBER Model)")
        self.chk_ml_active.setChecked(settings.ml_enabled)
        self.chk_ml_active.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        p2_layout.addWidget(self.chk_ml_active)

        ml_row = QHBoxLayout()
        ml_row.addWidget(QLabel("ML Malware Threshold (%):"))
        self.spin_ml_thresh = QSpinBox()
        self.spin_ml_thresh.setRange(40, 95)
        self.spin_ml_thresh.setValue(int(settings.ml_malware_threshold * 100))
        ml_row.addWidget(self.spin_ml_thresh)
        ml_row.addStretch()
        p2_layout.addLayout(ml_row)

        layout.addWidget(group_p2)

        # 4. YARA Engine & Diagnostics
        group_yara = QGroupBox("YARA Engine Status & Rules")
        group_yara.setStyleSheet(
            "QGroupBox { color: #f8fafc; font-weight: bold; border: 1px solid #1e293b; border-radius: 8px; margin-top: 10px; padding: 16px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        y_layout = QHBoxLayout(group_yara)
        self.lbl_yara_status = QLabel(
            "YARA Engine: Compiled & Active" if yara_engine.is_loaded else "YARA Engine: Inactive"
        )
        self.lbl_yara_status.setStyleSheet(
            f"color: {COLOR_SAFE if yara_engine.is_loaded else COLOR_TEXT_MUTED}; font-weight: bold;"
        )
        y_layout.addWidget(self.lbl_yara_status)
        y_layout.addStretch()

        btn_reload_yara = QPushButton("🔄 Reload Rules")
        btn_reload_yara.setProperty("class", "btn-secondary")
        btn_reload_yara.clicked.connect(self._reload_yara)
        y_layout.addWidget(btn_reload_yara)
        layout.addWidget(group_yara)

        # Save Button
        save_row = QHBoxLayout()
        btn_save = QPushButton("💾 Save Preferences")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_settings)
        save_row.addWidget(btn_save)
        save_row.addStretch()
        layout.addLayout(save_row)

        layout.addStretch()

    def _toggle_monitor(self, checked: bool) -> None:
        if checked:
            download_monitor.start()
        else:
            download_monitor.stop()

    def _browse_monitor_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Directory to Monitor", self.txt_watch_dir.text()
        )
        if folder:
            self.txt_watch_dir.setText(folder)
            download_monitor.watch_dir = Path(folder)

    def _reload_yara(self) -> None:
        success = yara_engine.load_rules()
        if success:
            self.lbl_yara_status.setText("YARA Engine: Compiled & Active")
            self.lbl_yara_status.setStyleSheet(f"color: {COLOR_SAFE}; font-weight: bold;")
            QMessageBox.information(self, "YARA Reloaded", "YARA rules recompiled successfully.")
        else:
            self.lbl_yara_status.setText("YARA Engine: Rules Compilation Notice")
            self.lbl_yara_status.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-weight: bold;")
            QMessageBox.warning(self, "YARA Reload", "Could not compile rules from rule directory.")

    def _save_settings(self) -> None:
        settings.threshold_safe_max = self.spin_safe.value()
        settings.threshold_low_max = self.spin_low.value()
        settings.threshold_high_max = self.spin_high.value()
        settings.ml_enabled = self.chk_ml_active.isChecked()
        settings.ml_malware_threshold = float(self.spin_ml_thresh.value() / 100.0)
        download_monitor.watch_dir = Path(self.txt_watch_dir.text())

        QMessageBox.information(self, "Saved", "SentinelX configuration updated.")
        self.settings_updated.emit()

