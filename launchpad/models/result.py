from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QIcon


@dataclass
class ResultItem:
    """A UI‑facing search result.

    The launcher uses `launch_target`, `launch_args` and `launch_cwd`
    to start the application. `key` is a stable identifier used to
    correlate asynchronous icon updates.
    """

    key: str
    display_name: str
    subtitle: str = ""
    launch_target: Optional[Path] = None
    launch_args: str = ""
    launch_cwd: Optional[Path] = None
    icon: Optional[QIcon] = field(default=None, repr=False)
