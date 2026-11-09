from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget


class SearchBar(QWidget):
    """Search input + mode pill + small hint strip.

    The input owns keyboard navigation (Up/Down/Enter/Tab/Escape) and
    re‑emits dedicated signals so the window doesn't have to install
    event filters.
    """

    query_changed = Signal(str)
    navigate = Signal(str)       # "up" | "down"
    activate = Signal()          # Enter
    dismiss = Signal()           # Escape
    switch_mode = Signal()       # Tab

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._edit = QLineEdit()
        self._edit.setObjectName("search")
        self._edit.setPlaceholderText("Search apps…")
        self._edit.setClearButtonEnabled(True)
        self._edit.setFocusPolicy(Qt.StrongFocus)
        self._edit.installEventFilter(self)
        self._edit.textChanged.connect(self.query_changed.emit)

        self._mode_pill = QLabel("APPS")
        self._mode_pill.setObjectName("modePill")
        self._mode_pill.setAlignment(Qt.AlignCenter)

        self._hint = QLabel("Tab: mode · ↑↓: navigate · Enter: open · Esc: close")
        self._hint.setObjectName("hint")

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 12, 6)
        row.setSpacing(10)
        row.addWidget(self._mode_pill)
        row.addWidget(self._edit, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(14, 0, 14, 6)
        bottom.addStretch(1)
        bottom.addWidget(self._hint)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addLayout(row)
        v.addLayout(bottom)

    # --- public -------------------------------------------------------

    def set_mode_label(self, label: str) -> None:
        self._mode_pill.setText(label.upper())

    def focus_input(self) -> None:
        self._edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def query(self) -> str:
        return self._edit.text()

    def set_query(self, text: str) -> None:
        # Preserve cursor at end without firing spurious signals beyond
        # what the user would expect.
        self._edit.setText(text)

    # --- key handling -------------------------------------------------

    def eventFilter(self, obj, event):  # noqa: ANN001 - Qt event types
        if obj is self._edit and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            if key == Qt.Key_Up:
                self.navigate.emit("up"); return True
            if key == Qt.Key_Down:
                self.navigate.emit("down"); return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.activate.emit(); return True
            if key == Qt.Key_Escape:
                self.dismiss.emit(); return True
            if key == Qt.Key_Tab and modifiers == Qt.NoModifier:
                self.switch_mode.emit(); return True
            if key == Qt.Key_Backtab:
                self.switch_mode.emit(); return True
        return super().eventFilter(obj, event)
