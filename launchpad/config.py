from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """User configuration.

    Future settings (global hotkey, start-with-Windows, tray behaviour)
    belong here. The rest of the app reads from this object so those
    features can be added without rewriting the UI or search logic.
    """

    window_width: int = 560
    window_max_results: int = 8
    result_icon_px: int = 28
    max_results_returned: int = 64
    start_menu_extra_folders: list[Path] = field(default_factory=list)
    # Reserved for future use:
    # global_hotkey: str = "Alt+Space"
    # start_with_windows: bool = True
    # run_in_tray: bool = False

    def clamp(self) -> None:
        self.window_width = max(360, min(1200, self.window_width))
        self.window_max_results = max(1, min(20, self.window_max_results))
        self.max_results_returned = max(1, min(500, self.max_results_returned))
