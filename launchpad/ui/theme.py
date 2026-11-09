from __future__ import annotations

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


# A restrained dark palette. Easy to swap later.
_PALETTE = {
    "bg":          "#1f2128",
    "bg_elev":     "#272a33",
    "border":      "#343845",
    "fg":          "#e6e8ee",
    "fg_muted":    "#9aa0ad",
    "accent":      "#7c9cff",
    "selection":   "#2f3647",
    "hover":       "#2a3040",
}


def palette() -> dict[str, str]:
    return dict(_PALETTE)


def apply_theme(app: QApplication) -> None:
    p = _PALETTE
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(p["bg"]))
    pal.setColor(QPalette.WindowText,      QColor(p["fg"]))
    pal.setColor(QPalette.Base,            QColor(p["bg_elev"]))
    pal.setColor(QPalette.AlternateBase,   QColor(p["bg_elev"]))
    pal.setColor(QPalette.ToolTipBase,     QColor(p["bg_elev"]))
    pal.setColor(QPalette.ToolTipText,     QColor(p["fg"]))
    pal.setColor(QPalette.Text,            QColor(p["fg"]))
    pal.setColor(QPalette.Button,          QColor(p["bg_elev"]))
    pal.setColor(QPalette.ButtonText,      QColor(p["fg"]))
    pal.setColor(QPalette.BrightText,      QColor(p["accent"]))
    pal.setColor(QPalette.Link,            QColor(p["accent"]))
    pal.setColor(QPalette.Highlight,       QColor(p["selection"]))
    pal.setColor(QPalette.HighlightedText, QColor(p["fg"]))
    pal.setColor(QPalette.PlaceholderText, QColor(p["fg_muted"]))
    app.setPalette(pal)

    app.setStyleSheet(_STYLESHEET.format(**p))


_STYLESHEET = """
QMainWindow, QWidget#central {
    background: {bg};
}
QFrame#card {
    background: {bg_elev};
    border: 1px solid {border};
    border-radius: 12px;
}
QLineEdit#search {
    background: transparent;
    border: none;
    color: {fg};
    font-size: 18px;
    padding: 10px 8px;
}
QLineEdit#search:focus {{ border: none; }}
QLabel#modePill {{
    background: {bg};
    color: {fg_muted};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
QLabel#hint {{
    color: {fg_muted};
    font-size: 11px;
}}
QListWidget#results {{
    background: transparent;
    border: none;
    outline: none;
    color: {fg};
}}
QListWidget#results::item {{
    padding: 8px 10px;
    border-radius: 8px;
    margin: 1px 4px;
}}
QListWidget#results::item:hover {{
    background: {hover};
}}
QListWidget#results::item:selected {{
    background: {selection};
}}
"""
