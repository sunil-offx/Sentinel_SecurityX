"""History view showing past scans, detection timelines, and hash audit records."""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import db
from app.database.models import ScannedFileRecord
from app.ui.styles import (
    COLOR_TEXT_PRIMARY,
    get_risk_badge_style,
)


class HistoryView(QWidget):
    """View presenting historical scan logs and detection audit trail."""

    def __init__(self) -> None:
        super().__init__()
        self.all_scans: list[ScannedFileRecord] = []
        self._init_ui()
        self.refresh_history()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Filter bar
        filter_card = QFrame()
        filter_card.setProperty("class", "content-card")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)

        lbl_filter = QLabel("Search:")
        lbl_filter.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")
        filter_layout.addWidget(lbl_filter)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Filter by file name, path, or SHA-256 hash...")
        self.txt_search.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.txt_search, 1)

        lbl_level = QLabel("Risk Level:")
        lbl_level.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")
        filter_layout.addWidget(lbl_level)

        self.combo_risk = QComboBox()
        self.combo_risk.addItems(["All Levels", "CRITICAL", "HIGH", "LOW", "SAFE"])
        self.combo_risk.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.combo_risk)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_history)
        filter_layout.addWidget(btn_refresh)

        btn_clear = QPushButton("Clear History")
        btn_clear.setProperty("class", "btn-danger")
        btn_clear.clicked.connect(self._on_clear_history)
        filter_layout.addWidget(btn_clear)

        layout.addWidget(filter_card)

        # Scans Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "File Name", "Path", "SHA-256 (Prefix)", "Risk Level", "Score"]
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
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh_history(self) -> None:
        """Fetch scan records from database."""
        self.all_scans = db.get_recent_scans(limit=250)
        self._apply_filters()

    def _apply_filters(self) -> None:
        query = self.txt_search.text().lower().strip()
        selected_level = self.combo_risk.currentText()

        filtered = []
        for s in self.all_scans:
            if selected_level != "All Levels" and s.risk_level.upper() != selected_level:
                continue
            if query:
                fname = os.path.basename(s.path).lower()
                if (
                    query not in fname
                    and query not in s.path.lower()
                    and query not in s.sha256.lower()
                ):
                    continue
            filtered.append(s)

        self.table.setRowCount(len(filtered))
        for row_idx, scan in enumerate(filtered):
            ts_short = scan.scanned_at.replace("T", " ")[:19]
            item_ts = QTableWidgetItem(ts_short)
            item_ts.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_ts)

            fname = os.path.basename(scan.path)
            item_name = QTableWidgetItem(fname)
            item_name.setToolTip(scan.path)
            self.table.setItem(row_idx, 1, item_name)

            item_path = QTableWidgetItem(scan.path)
            self.table.setItem(row_idx, 2, item_path)

            sha_short = f"{scan.sha256[:16]}..."
            item_sha = QTableWidgetItem(sha_short)
            item_sha.setToolTip(scan.sha256)
            item_sha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, item_sha)

            badge = QLabel(scan.risk_level)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(get_risk_badge_style(scan.risk_level))
            self.table.setCellWidget(row_idx, 4, badge)

            item_score = QTableWidgetItem(f"{scan.risk_score}")
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, item_score)

    def _on_clear_history(self) -> None:
        confirm = QMessageBox.warning(
            self,
            "Confirm Clear History",
            "Are you sure you want to clear scan logs? (Quarantined files will remain safely isolated)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            db.clear_all()
            self.refresh_history()
