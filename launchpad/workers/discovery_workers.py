from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from PySide6.QtCore import QThread, Signal

from ..discovery.start_menu import AppEntry, discover_start_menu_entries


class DiscoveryWorker(QThread):
    """Runs Start Menu discovery off the UI thread.

    Emits `entry_ready(AppEntry)` for each entry as it is discovered,
    and `finished()` when the scan is complete.
    """

    entry_ready = Signal(object)   # AppEntry
    failed = Signal(str)

    def __init__(
        self,
        extra_folders: Optional[Iterable[Path]] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._extra = list(extra_folders) if extra_folders else []

    def run(self) -> None:  # noqa: D401 - QThread entry
        try:
            entries: list[AppEntry] = discover_start_menu_entries(self._extra)
        except Exception as e:  # swallow and surface via signal
            self.failed.emit(str(e))
            return
        for entry in entries:
            self.entry_ready.emit(entry)
