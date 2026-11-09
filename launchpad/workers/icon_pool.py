from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtGui import QIcon

from ..platform_win.shell import shell_icon


class _IconTask(QRunnable):
    def __init__(self, pool: "IconPool", key: str, icon_path: Optional[Path], fallback: Optional[Path]) -> None:
        super().__init__()
        self.setAutoDelete(True)
        self._pool = pool
        self._key = key
        self._icon_path = icon_path
        self._fallback = fallback

    def run(self) -> None:
        icon: Optional[QIcon] = None
        if self._icon_path is not None:
            icon = shell_icon(self._icon_path, small=True)
        if icon is None and self._fallback is not None:
            icon = shell_icon(self._fallback, small=True)
        # Emit via the pool (QRunnable can't hold a Signal directly).
        self._pool._deliver(self._key, icon)


class IconPool(QObject):
    """Loads shell icons off the UI thread.

    Delivers results via the `icon_ready(key, QIcon)` signal. Duplicate
    in‑flight requests for the same key are coalesced.
    """

    icon_ready = Signal(str, object)

    def __init__(self, max_workers: int = 4, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(max(1, max_workers))
        self._in_flight: set[str] = set()

    def request(self, key: str, icon_path: Optional[Path], fallback_path: Optional[Path]) -> None:
        if key in self._in_flight:
            return
        self._in_flight.add(key)
        task = _IconTask(self, key, icon_path, fallback_path)
        self._pool.start(task)

    @Slot(str, object)
    def _deliver(self, key: str, icon: Optional[QIcon]) -> None:
        self._in_flight.discard(key)
        if icon is not None:
            self.icon_ready.emit(key, icon)
