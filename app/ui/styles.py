"""Premium cybersecurity dark theme stylesheet and styling tokens for SentinelX UI."""

# Color tokens
COLOR_BG_DARK = "#090d16"
COLOR_BG_SURFACE = "#111827"
COLOR_BG_CARD = "#1a2234"
COLOR_BG_HOVER = "#242e42"
COLOR_BORDER = "#2e3b52"
COLOR_BORDER_FOCUS = "#38bdf8"

COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_SECONDARY = "#94a3b8"
COLOR_TEXT_MUTED = "#64748b"

COLOR_ACCENT = "#0284c7"
COLOR_ACCENT_HOVER = "#0369a1"
COLOR_ACCENT_CYAN = "#38bdf8"

COLOR_SAFE = "#10b981"
COLOR_SAFE_BG = "#064e3b"
COLOR_LOW = "#0284c7"
COLOR_LOW_BG = "#0c4a6e"
COLOR_HIGH = "#f59e0b"
COLOR_HIGH_BG = "#78350f"
COLOR_CRITICAL = "#ef4444"
COLOR_CRITICAL_BG = "#7f1d1d"

MAIN_STYLESHEET = """
QMainWindow, QWidget#CentralWidget {
    background-color: #090d16;
    color: #f8fafc;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar navigation */
QWidget#Sidebar {
    background-color: #0d131f;
    border-right: 1px solid #1e293b;
}

QPushButton.nav-btn {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.nav-btn:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QPushButton.nav-btn:checked {
    background-color: #1e3a5f;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
}

/* Header & Top Bar */
QWidget#TopBar {
    background-color: #0d131f;
    border-bottom: 1px solid #1e293b;
}

/* Cards */
QFrame.stat-card, QFrame.content-card {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px;
}

QFrame.stat-card:hover {
    border-color: #38bdf8;
}

/* Primary Action Buttons */
QPushButton.btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0369a1);
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #075985);
}

QPushButton.btn-primary:pressed {
    background-color: #0c4a6e;
}

QPushButton.btn-danger {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.btn-danger:hover {
    background-color: #b91c1c;
}

QPushButton.btn-secondary {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.btn-secondary:hover {
    background-color: #334155;
}

/* Form controls */
QLineEdit, QSpinBox, QComboBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}

/* Tables */
QTableWidget {
    background-color: #111827;
    color: #f8fafc;
    gridline-color: #1e293b;
    border: 1px solid #1e293b;
    border-radius: 8px;
    selection-background-color: #1e3a5f;
    selection-color: #38bdf8;
}

QTableWidget::item {
    padding: 8px;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #1e293b;
    font-weight: 600;
}

/* Progress bar */
QProgressBar {
    background-color: #1e293b;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #f8fafc;
    font-size: 11px;
    height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 4px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #090d16;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


def get_risk_badge_style(level: str) -> str:
    """Return styling CSS for risk level badges."""
    colors = {
        "SAFE": (COLOR_SAFE, COLOR_SAFE_BG),
        "LOW": (COLOR_LOW, COLOR_LOW_BG),
        "HIGH": (COLOR_HIGH, COLOR_HIGH_BG),
        "CRITICAL": (COLOR_CRITICAL, COLOR_CRITICAL_BG),
    }
    fg, bg = colors.get(level.upper(), (COLOR_TEXT_PRIMARY, COLOR_BG_CARD))
    return f"""
        QLabel {{
            color: {fg};
            background-color: {bg};
            border: 1px solid {fg};
            border-radius: 6px;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 12px;
        }}
    """
