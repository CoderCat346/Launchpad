from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QResizeEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from .result_list import ResultList, _Row
from .search_bar import SearchBar

if TYPE_CHECKING:
    from ..app import AppController
    from ..models.result import ResultItem


class LaunchpadWindow(QMainWindow):
    def __init__(self, controller: "AppController", parent=None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._results: list["ResultItem"] = []

        self.setWindowTitle("Launchpad")
        # Frameless + popup: no taskbar entry, click‑outside closes.
        self.setWindowFlags(
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.Popup
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setMouseTracking(True)

        self._build_ui()
        self._center_on_screen()
        self._sync_mode_label()

        # Wire signals.
        sb = self._search_bar
        sb.query_changed.connect(self._on_query_changed)
        sb.navigate.connect(self._on_navigate)
        sb.activate.connect(self._on_activate)
        sb.dismiss.connect(self.close)
        sb.switch_mode.connect(self._on_switch_mode)

    # --- UI construction ---------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(4, 4, 4, 4)
        card_layout.setSpacing(0)

        self._search_bar = SearchBar()
        self._results_list = ResultList(
            icon_px=self._controller.settings.result_icon_px
        )

        card_layout.addWidget(self._search_bar)
        card_layout.addWidget(self._results_list)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        width = self._controller.settings.window_width
        self.setFixedWidth(width)
        self._apply_height()

    def _apply_height(self) -> None:
        list_h = self._results_list.preferred_height()
        bar_h = self._search_bar.sizeHint().height()
        chrome = 12 * 2 + 8  # outer margins + card padding
        self.setFixedHeight(bar_h + list_h + chrome)

    def _center_on_screen(self) -> None:
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            max(80, screen.height() // 4),
        )

    # --- public API used by AppController ----------------------------

    @Slot(list)
    def set_results(self, results: list["ResultItem"]) -> None:
        self._results = results
        self._render_results(self._search_bar.query())
        self._apply_height()

    @Slot(str, object)
    def update_entry_icon(self, key: str, icon: QIcon) -> None:
        self._results_list.update_icon(key, icon)

    def show(self) -> None:  # type: ignore[override]
        super().show()
        self._search_bar.focus_input()
        self.raise_()

    # --- internal -----------------------------------------------------

    def _render_results(self, query: str) -> None:
        results = self._controller.search(query)
        self._results = results
        rows = [
            _Row(key=r.key, text=r.display_name, sub=r.subtitle or "", icon=r.icon)
            for r in results
        ]
        self._results_list.set_rows(rows)

    def _sync_mode_label(self) -> None:
        self._search_bar.set_mode_label(self._controller.current_mode_label())

    # --- slots --------------------------------------------------------

    @Slot(str)
    def _on_query_changed(self, text: str) -> None:
        self._render_results(text)

    @Slot(str)
    def _on_navigate(self, direction: str) -> None:
        delta = -1 if direction == "up" else 1
        self._results_list.move_selection(delta)

    @Slot()
    def _on_activate(self) -> None:
        key = self._results_list.selected_key()
        if not key:
            return
        for r in self._results:
            if r.key == key:
                if self._controller.launch(r):
                    self.close()
                return

    @Slot()
    def _on_switch_mode(self) -> None:
        # Preserve query across mode switches.
        q = self._search_bar.query()
        self._controller.advance_mode()
        self._sync_mode_label()
        self._render_results(q)
        # Keep typing focus on the search box.
        self._search_bar.focus_input()

    # --- click outside closes (Qt.Popup already does this, but be safe)

    def mousePressEvent(self, event):  # noqa: ANN001
        # If the click is outside the card, close.
        pos = event.position().toPoint()
        card = self.centralWidget().findChild(QFrame, "card")
        if card is not None and not card.geometry().contains(pos):
            self.close()
            return
        super().mousePressEvent(event)
