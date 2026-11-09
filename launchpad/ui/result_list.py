from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PySide6.QtGui import QIcon, QListWidgetItem
from PySide6.QtGui import QIcon, QListWidgetItem
from PySide6.QtWidgets import QListWidget, QListWidgetItem as _QListWidgetItem


@dataclass
class _Row:
    key: str
    text: str
    sub: str
    icon: QIcon | None


class ResultList(QListWidget):
    """Non‑focusable result list.

    Selection is driven by the controller; the list never accepts focus
    so typing focus stays in the search box.
    """

    def __init__(self, icon_px: int = 28, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("results")
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setIconSize(QSize(icon_px, icon_px))
        self.setSpacing(2)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setSelectionBehavior(QListWidget.SelectItems)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self._rows: list[_Row] = []

    # --- population ---------------------------------------------------

    def set_rows(self, rows: Iterable[_Row]) -> None:
        self.clear()
        self._rows = list(rows)
        for r in self._rows:
            item = _QListWidgetItem(r.text)
            if r.sub:
                item.setToolTip(r.sub)
            if r.icon is not None:
                item.setIcon(r.icon)
            item.setData(Qt.UserRole, r.key)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.addItem(item)
        if self._rows:
            self.setCurrentRow(0)

    def update_icon(self, key: str, icon: QIcon) -> None:
        for i, r in enumerate(self._rows):
            if r.key == key:
                r.icon = icon
                item = self.item(i)
                if item is not None:
                    item.setIcon(icon)
                return

    # --- selection ----------------------------------------------------

    def selected_key(self) -> str | None:
        row = self.currentRow()
        if 0 <= row < len(self._rows):
            return self._rows[row].key
        return None

    def move_selection(self, delta: int) -> None:
        if not self._rows:
            return
        row = self.currentRow()
        if row < 0:
            row = 0
        row = max(0, min(len(self._rows) - 1, row + delta))
        self.setCurrentRow(row)

    def preferred_height(self) -> int:
        if not self._rows:
            return 0
        # Size to content up to a reasonable cap; the window decides.
        hint = self.sizeHintForRow(0) if self.count() else 0
        return min(420, self.count() * (hint + self.spacing() + 2) + 8)
