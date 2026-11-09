from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication

from .config import Settings
from .discovery.start_menu import AppEntry
from .modes.apps_mode import AppsMode
from .modes.manager import ModeManager
from .models.launcher import Launcher
from .models.result import ResultItem
from .ui.theme import apply_theme
from .ui.window import LaunchpadWindow
from .workers.discovery_workers import DiscoveryWorker
from .workers.icon_pool import IconPool


class AppController(QObject):
    """Glue between the UI, modes, discovery and launching.

    Owns the ModeManager and the Launcher. The window signals into this
    controller; the controller signals back to the window. This keeps
    the UI free of business logic.
    """

    entries_ready = Signal(list)      # list[ResultItem]
    entry_icon_ready = Signal(str, object)  # key, QIcon

    def __init__(self, settings: Settings, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.settings = settings

        self.apps_mode = AppsMode()
        self.mode_manager = ModeManager([self.apps_mode])

        self.launcher = Launcher()
        self.icon_pool = IconPool(max_workers=4)
        self.icon_pool.icon_ready.connect(self._on_icon_ready)

        self._worker: Optional[DiscoveryWorker] = None

    # --- lifecycle ----------------------------------------------------

    def start_discovery(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self.apps_mode.clear()
        self.entries_ready.emit([])
        self._worker = DiscoveryWorker(extra_folders=self.settings.start_menu_extra_folders)
        self._worker.entry_ready.connect(self._on_entry_ready)
        self._worker.finished.connect(self._on_discovery_finished)
        self._worker.start()

    def refresh(self) -> None:
        self.start_discovery()

    # --- mode / search ------------------------------------------------

    def current_mode_id(self) -> str:
        return self.mode_manager.current.id

    def current_mode_label(self) -> str:
        return self.mode_manager.current.label

    def advance_mode(self) -> str:
        # Safe no-op when only one mode is registered.
        self.mode_manager.next()
        return self.mode_manager.current.id

    def search(self, query: str) -> list[ResultItem]:
        return self.mode_manager.current.search(query)[: self.settings.max_results_returned]

    # --- launching ----------------------------------------------------

    def launch(self, result: ResultItem) -> bool:
        return self.launcher.launch(result)

    # --- internal slots ----------------------------------------------

    @Slot(object)
    def _on_entry_ready(self, entry: AppEntry) -> None:
        self.apps_mode.add_entry(entry)
        # Schedule icon loading off the UI thread.
        icon_path = entry.resolved.icon_path
        key = entry.result_key()
        fallback = entry.resolved.target if entry.resolved.target.exists() else None
        self.icon_pool.request(key, icon_path=icon_path, fallback_path=fallback)

    @Slot()
    def _on_discovery_finished(self) -> None:
        self.entries_ready.emit(self.apps_mode.snapshot_results())

    @Slot(str, object)
    def _on_icon_ready(self, key: str, icon) -> None:
        self.entry_icon_ready.emit(key, icon)


class LaunchpadApp:
    """Top-level application object.

    Owns QApplication, the controller, and the window. Designed so that
    tray integration, startup registration and a global hotkey can be
    added here later without touching the window or modes.
    """

    def __init__(self, argv: list[str]) -> None:
        self.app = QApplication(argv)
        self.app.setQuitOnLastWindowClosed(True)
        self.app.setApplicationName("Launchpad")
        self.app.setApplicationVersion("0.1.0")

        apply_theme(self.app)

        self.settings = Settings()
        self.settings.clamp()

        self.controller = AppController(self.settings)
        self.window = LaunchpadWindow(self.controller)

        self.controller.entries_ready.connect(self.window.set_results)
        self.controller.entry_icon_ready.connect(self.window.update_entry_icon)

    def run(self) -> int:
        self.window.show()
        self.controller.start_discovery()
        return self.app.exec()
