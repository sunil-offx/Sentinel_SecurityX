"""Dashboard view displaying system protection status, scan metrics, and quick actions."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.database import db
from app.ui.styles import (
    COLOR_ACCENT_CYAN,
    COLOR_CRITICAL,
    COLOR_HIGH,
    COLOR_SAFE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    get_risk_badge_style,
)


class StatCard(QFrame):
    """Reusable metric card with glowing accent."""

    def __init__(self, title: str, initial_value: str, subtitle: str, color_accent: str) -> None:
        super().__init__()
        self.setObjectName("stat-card")
        self.setProperty("class", "stat-card")
        self.setStyleSheet(
            f"""
            QFrame#stat-card {{
                background-color: #111827;
                border: 1px solid #1e293b;
                border-top: 3px solid {color_accent};
                border-radius: 8px;
                padding: 14px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;"
        )

        self.lbl_value = QLabel(initial_value)
        self.lbl_value.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 26px; font-weight: bold;"
        )

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(lbl_sub)

    def set_value(self, value: str) -> None:
        self.lbl_value.setText(value)


class DashboardView(QWidget):
    """Main dashboard displaying security overview and recent detections."""

    navigate_to_scanner = Signal(str)  # "file" or "folder"
    navigate_to_quarantine = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()
        self.refresh_data()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # 1. Protection Status Banner
        banner = QFrame()
        banner.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f2b3c, stop:1 #111827);
                border: 1px solid #0284c7;
                border-radius: 8px;
                padding: 16px;
            }
            """
        )
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(16, 12, 16, 12)

        shield_icon = QLabel("🛡️")
        shield_icon.setStyleSheet("font-size: 32px;")
        banner_layout.addWidget(shield_icon)

        banner_text_layout = QVBoxLayout()
        banner_title = QLabel("System Shield Active — Local Defense In-Depth")
        banner_title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 17px; font-weight: bold;"
        )
        banner_subtitle = QLabel(
            "YARA Rule Engine • Static PE & Script Heuristics • Real-Time Downloads Watcher • Zero Cloud Dependency"
        )
        banner_subtitle.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 12px;")
        banner_text_layout.addWidget(banner_title)
        banner_text_layout.addWidget(banner_subtitle)
        banner_layout.addLayout(banner_text_layout)
        banner_layout.addStretch()

        btn_refresh = QPushButton("Refresh Status")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_data)
        banner_layout.addWidget(btn_refresh)

        layout.addWidget(banner)

        # 2. Key Metrics Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_scanned = StatCard(
            "Files Scanned", "0", "Total inspected files", COLOR_ACCENT_CYAN
        )
        self.card_threats = StatCard(
            "Threats Detected", "0", "High & critical alerts", COLOR_CRITICAL
        )
        self.card_quarantine = StatCard("Quarantined", "0", "Isolated in safe vault", COLOR_HIGH)
        self.card_monitor = StatCard(
            "Download Shield", "ACTIVE", "Monitoring ~/Downloads", COLOR_SAFE
        )

        cards_layout.addWidget(self.card_scanned)
        cards_layout.addWidget(self.card_threats)
        cards_layout.addWidget(self.card_quarantine)
        cards_layout.addWidget(self.card_monitor)
        layout.addLayout(cards_layout)

        # 3. Quick Action Row
        actions_frame = QFrame()
        actions_frame.setProperty("class", "content-card")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(16, 14, 16, 14)

        lbl_quick = QLabel("Quick Actions:")
        lbl_quick.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        actions_layout.addWidget(lbl_quick)

        btn_scan_file = QPushButton("🔍 Scan Single File")
        btn_scan_file.setProperty("class", "btn-primary")
        btn_scan_file.clicked.connect(lambda: self.navigate_to_scanner.emit("file"))
        actions_layout.addWidget(btn_scan_file)

        btn_scan_folder = QPushButton("📁 Scan Directory")
        btn_scan_folder.setProperty("class", "btn-secondary")
        btn_scan_folder.clicked.connect(lambda: self.navigate_to_scanner.emit("folder"))
        actions_layout.addWidget(btn_scan_folder)

        btn_view_qtn = QPushButton("📦 Open Quarantine Vault")
        btn_view_qtn.setProperty("class", "btn-secondary")
        btn_view_qtn.clicked.connect(lambda: self.navigate_to_quarantine.emit())
        actions_layout.addWidget(btn_view_qtn)

        actions_layout.addStretch()
        layout.addWidget(actions_frame)

        # 4. Recent Scan Activity Section
        lbl_recent = QLabel("Recent Security Inspections")
        lbl_recent.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
        )
        layout.addWidget(lbl_recent)

        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(5)
        self.table_recent.setHorizontalHeaderLabels(
            ["Timestamp", "File Name", "Size", "Risk Level", "Score"]
        )
        self.table_recent.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recent.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_recent.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recent.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recent.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recent.verticalHeader().setVisible(False)
        self.table_recent.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_recent.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_recent.setAlternatingRowColors(True)
        self.table_recent.setMinimumHeight(240)
        layout.addWidget(self.table_recent)

    def refresh_data(self) -> None:
        """Query database and update cards and tables."""
        stats = db.get_stats()
        self.card_scanned.set_value(f"{stats['total_scanned']:,}")
        self.card_threats.set_value(f"{stats['threats_detected']:,}")
        self.card_quarantine.set_value(f"{stats['active_quarantined']:,}")

        recent_scans = db.get_recent_scans(limit=10)
        self.table_recent.setRowCount(len(recent_scans))

        for row_idx, scan in enumerate(recent_scans):
            # Timestamp
            ts_short = (
                scan.scanned_at.split("T")[-1][:8] if "T" in scan.scanned_at else scan.scanned_at
            )
            item_ts = QTableWidgetItem(ts_short)
            item_ts.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_recent.setItem(row_idx, 0, item_ts)

            # File name
            import os

            fname = os.path.basename(scan.path)
            item_name = QTableWidgetItem(fname)
            item_name.setToolTip(scan.path)
            self.table_recent.setItem(row_idx, 1, item_name)

            # Size
            size_kb = (
                f"{scan.size / 1024:.1f} KB"
                if scan.size < 1024 * 1024
                else f"{scan.size / (1024 * 1024):.1f} MB"
            )
            item_size = QTableWidgetItem(size_kb)
            item_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_recent.setItem(row_idx, 2, item_size)

            # Risk Badge
            badge_widget = QLabel(scan.risk_level)
            badge_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_widget.setStyleSheet(get_risk_badge_style(scan.risk_level))
            self.table_recent.setCellWidget(row_idx, 3, badge_widget)

            # Score
            item_score = QTableWidgetItem(f"{scan.risk_score}/100")
            item_score.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_recent.setItem(row_idx, 4, item_score)
