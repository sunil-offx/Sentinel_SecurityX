"""Quarantine view for managing isolated suspicious files, safe restorations, and permanent deletions."""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.quarantine import QuarantineError, quarantine_manager
from app.database.models import QuarantineRecord
from app.ui.styles import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)


class QuarantineView(QWidget):
    """View managing isolated threats and safe operations."""

    quarantine_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.records: list[QuarantineRecord] = []
        self._init_ui()
        self.refresh_quarantine()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header Info Banner
        info_frame = QFrame()
        info_frame.setProperty("class", "content-card")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 14, 16, 14)

        icon_lbl = QLabel("📦")
        icon_lbl.setStyleSheet("font-size: 28px;")
        info_layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        title_lbl = QLabel("Quarantine Vault — Isolated Threat Storage")
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        desc_lbl = QLabel(
            "Files placed here have their executable privileges neutralized and are segregated from your operating system."
        )
        desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(desc_lbl)
        info_layout.addLayout(text_layout)
        info_layout.addStretch()

        btn_refresh = QPushButton("Refresh Vault")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_quarantine)
        info_layout.addWidget(btn_refresh)

        layout.addWidget(info_frame)

        # Quarantine Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Original File", "Original Location", "Isolated At", "Risk Score", "Reason"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        layout.addWidget(self.table)

        # Action Buttons Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.btn_restore = QPushButton("♻️ Restore File to Original Location")
        self.btn_restore.setProperty("class", "btn-secondary")
        self.btn_restore.setEnabled(False)
        self.btn_restore.clicked.connect(self._on_restore)
        actions_row.addWidget(self.btn_restore)

        self.btn_delete = QPushButton("🗑️ Permanently Delete (Shred)")
        self.btn_delete.setProperty("class", "btn-danger")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._on_delete)
        actions_row.addWidget(self.btn_delete)

        actions_row.addStretch()
        layout.addLayout(actions_row)

    def refresh_quarantine(self) -> None:
        """Reload quarantined entries from database."""
        self.records = quarantine_manager.list_quarantined()
        self.table.setRowCount(len(self.records))

        for row_idx, rec in enumerate(self.records):
            item_id = QTableWidgetItem(str(rec.id))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_id)

            fname = os.path.basename(rec.original_path)
            item_fname = QTableWidgetItem(fname)
            item_fname.setToolTip(rec.original_path)
            self.table.setItem(row_idx, 1, item_fname)

            item_orig = QTableWidgetItem(rec.original_path)
            self.table.setItem(row_idx, 2, item_orig)

            ts_short = (
                rec.created_at.split("T")[-1][:8] if "T" in rec.created_at else rec.created_at
            )
            item_ts = QTableWidgetItem(ts_short)
            item_ts.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, item_ts)

            item_score = QTableWidgetItem(f"{rec.risk_score}")
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, item_score)

            item_reason = QTableWidgetItem(rec.reason)
            self.table.setItem(row_idx, 5, item_reason)

        self.btn_restore.setEnabled(False)
        self.btn_delete.setEnabled(False)

    def _on_row_selected(self) -> None:
        has_sel = len(self.table.selectionModel().selectedRows()) > 0
        self.btn_restore.setEnabled(has_sel)
        self.btn_delete.setEnabled(has_sel)

    def _get_selected_record(self) -> QuarantineRecord | None:
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        row = selected[0].row()
        if 0 <= row < len(self.records):
            return self.records[row]
        return None

    def _on_restore(self) -> None:
        rec = self._get_selected_record()
        if not rec or not rec.id:
            return

        confirm = QMessageBox.question(
            self,
            "Confirm File Restoration",
            f"Are you sure you want to restore:\n\n{rec.original_path}\n\n"
            f"If this file is malicious, restoring it will make it available on your system again.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            quarantine_manager.restore_file(rec.id)
            QMessageBox.information(
                self, "Restored", "File successfully restored to original location."
            )
            self.refresh_quarantine()
            self.quarantine_changed.emit()
        except QuarantineError as e:
            QMessageBox.critical(self, "Restore Error", str(e))

    def _on_delete(self) -> None:
        rec = self._get_selected_record()
        if not rec or not rec.id:
            return

        confirm = QMessageBox.warning(
            self,
            "Confirm Permanent Shredding",
            f"Are you sure you want to permanently delete:\n\n{rec.original_path}?\n\n"
            f"This action CANNOT be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            quarantine_manager.permanently_delete(rec.id)
            QMessageBox.information(
                self, "Deleted", "Quarantined file permanently shredded and removed."
            )
            self.refresh_quarantine()
            self.quarantine_changed.emit()
        except QuarantineError as e:
            QMessageBox.critical(self, "Deletion Error", str(e))
