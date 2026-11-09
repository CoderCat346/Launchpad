from __future__ import annotations

import shlex
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QProcess, QUrl
from PySide6.QtGui import QDesktopServices

from .result import ResultItem


_EXECUTABLE_SUFFIXES = {".exe", ".bat", ".cmd", ".com", ".msc", ".cpl", ".scr"}


class Launcher:
    """Launches ResultItems using the most appropriate mechanism.

    - Executables and scripts are launched with QProcess so we can pass
      arguments and a working directory.
    - URL shortcuts (.url) and other documents fall back to
      QDesktopServices, which honours the user's default handlers.
    """

    def launch(self, item: ResultItem) -> bool:
        if item.launch_target is None:
            return False

        target = item.launch_target
        args = _split_args(item.launch_args)
        cwd = str(item.launch_cwd) if item.launch_cwd else None

        suffix = target.suffix.casefold()

        if suffix == ".url":
            url = _read_url_file(target)
            if url:
                return QDesktopServices.openUrl(QUrl(url))
            return False

        if suffix in _EXECUTABLE_SUFFIXES:
            return self._start_detached(str(target), args, cwd)

        # Anything else: let the shell decide.
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    @staticmethod
    def _start_detached(target: str, args: list[str], cwd: Optional[str]) -> bool:
        proc = QProcess()
        if cwd:
            proc.setWorkingDirectory(cwd)
        ok, _ = proc.startDetached(target, args)
        return bool(ok)


def _split_args(args: str) -> list[str]:
    args = (args or "").strip()
    if not args:
        return []
    try:
        return shlex.split(args, posix=False)
    except ValueError:
        return [args]


def _read_url_file(path: Path) -> Optional[str]:
    """Read a Windows .url file and return its URL= value."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith("url="):
            return s[4:].strip()
    return None
