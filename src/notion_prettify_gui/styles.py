from __future__ import annotations

# Brand palette
BG = "#0f0a0a"
SURFACE = "#18120f"
SURFACE_ALT = "#1c1511"
BORDER = "#2a2020"
BORDER_ALT = "#3a2e2a"
MUTED = "#a1a1aa"
FG = "#fafafa"
ACCENT = "#9dff00"
ACCENT_HOVER = "#b5ff40"
ACCENT_PRESSED = "#7acc00"
DANGER = "#ff5f5f"
SUCCESS = "#9dff00"
BUTTON_BG = "#27201c"
BUTTON_HOVER = "#332820"
BUTTON_PRESSED = "#1e1814"

STYLESHEET = f"""
/* ── Global ── */
QWidget {{
    background-color: {BG};
    color: {FG};
    font-family: "Inter", "Segoe UI", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}

QMainWindow {{
    background-color: {BG};
}}

/* ── Scroll area ── */
QScrollArea {{
    background-color: {BG};
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: {BG};
}}

QScrollBar:vertical {{
    background: {BG};
    width: 6px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_ALT};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {MUTED};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Group box (section cards) ── */
QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 8px;
    padding: 16px;
    padding-top: 20px;
    font-size: 13px;
    font-weight: 600;
    color: {FG};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 0px;
    padding: 0 6px;
    background-color: {SURFACE};
    color: {FG};
    font-size: 13px;
    font-weight: 600;
}}

/* ── Field cell containers ── */
QWidget[role="field-cell"] {{
    background-color: transparent;
}}

/* ── Labels ── */
QLabel {{
    background-color: transparent;
    color: {FG};
}}

QLabel[role="heading"] {{
    font-size: 20px;
    font-weight: 700;
    color: {FG};
}}

QLabel[role="subtitle"] {{
    color: {MUTED};
    font-size: 12px;
}}

QLabel[role="section-label"] {{
    color: {MUTED};
    font-size: 12px;
    background-color: transparent;
}}

QLabel[role="status-success"] {{
    color: {SUCCESS};
    font-size: 12px;
}}

QLabel[role="status-error"] {{
    color: {DANGER};
    font-size: 12px;
}}

QLabel[role="hint"] {{
    color: {MUTED};
    font-size: 11px;
}}

/* ── Line edit / inputs ── */
QLineEdit {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER_ALT};
    border-radius: 6px;
    padding: 6px 10px;
    color: {FG};
    font-size: 13px;
    selection-background-color: {ACCENT};
    selection-color: {BG};
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}

QLineEdit:hover {{
    border: 1px solid #4a3c38;
}}

QLineEdit::placeholder {{
    color: {MUTED};
}}

/* ── Primary CTA button ── */
QPushButton[role="primary"] {{
    background-color: {ACCENT};
    color: {BG};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.2px;
}}

QPushButton[role="primary"]:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton[role="primary"]:pressed {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton[role="primary"]:disabled {{
    background-color: #3a4a1a;
    color: #5a6a3a;
}}

/* ── Secondary / Browse buttons ── */
QPushButton {{
    background-color: {BUTTON_BG};
    color: {FG};
    border: 1px solid {BORDER_ALT};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {BUTTON_HOVER};
    border-color: #4a3c38;
}}

QPushButton:pressed {{
    background-color: {BUTTON_PRESSED};
}}

QPushButton:disabled {{
    color: {MUTED};
    border-color: {BORDER};
}}

/* ── Tri-state toggle buttons ── */
QPushButton[role="toggle-default"] {{
    background-color: transparent;
    color: {MUTED};
    border: 1px solid {BORDER_ALT};
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 500;
    min-width: 56px;
}}

QPushButton[role="toggle-default"]:hover {{
    border-color: {MUTED};
    color: {FG};
}}

QPushButton[role="toggle-on"] {{
    background-color: {ACCENT};
    color: {BG};
    border: 1px solid {ACCENT};
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 600;
    min-width: 56px;
}}

QPushButton[role="toggle-on"]:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QPushButton[role="toggle-off"] {{
    background-color: rgba(255, 95, 95, 0.12);
    color: {DANGER};
    border: 1px solid rgba(255, 95, 95, 0.4);
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 500;
    min-width: 56px;
}}

QPushButton[role="toggle-off"]:hover {{
    background-color: rgba(255, 95, 95, 0.2);
}}

/* ── Log / output text area ── */
QTextEdit {{
    background-color: #0c0808;
    color: #c8c8c8;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 10px;
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: {BORDER_ALT};
}}

/* ── Divider ── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    background-color: {BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
"""
