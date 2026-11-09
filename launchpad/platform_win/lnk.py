from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ResolvedShortcut:
    target: Path
    arguments: str
    working_dir: Optional[Path]
    icon_path: Optional[Path]
    icon_index: int = 0


def resolve_lnk(lnk_path: Path) -> Optional[ResolvedShortcut]:
    """Resolve a Windows .lnk shortcut.

    Uses `WScript.Shell` (pywin32) to read the shortcut's target,
    arguments, working directory and icon location. Returns None if the
    shortcut has no usable target.
    """
    import win32com.client  # lazy import: only needed on Windows

    lnk_path = Path(lnk_path)
    if not lnk_path.exists():
        return None

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(lnk_path))  # loads existing .lnk

    target_raw = (shortcut.Targetpath or "").strip()
    if not target_raw:
        return None
    target = _coerce_path(target_raw)
    if target is None:
        return None

    arguments = (shortcut.Arguments or "").strip()

    wd_raw = (shortcut.WorkingDirectory or "").strip()
    working_dir = _coerce_path(wd_raw) if wd_raw else None

    icon_path: Optional[Path] = None
    icon_index = 0
    icon_loc = (shortcut.IconLocation or "").strip()
    if icon_loc:
        icon_path, icon_index = _parse_icon_location(icon_loc)

    return ResolvedShortcut(
        target=target,
        arguments=arguments,
        working_dir=working_dir,
        icon_path=icon_path,
        icon_index=icon_index,
    )


def _coerce_path(raw: str) -> Optional[Path]:
    raw = raw.strip().strip('"')
    if not raw:
        return None
    # Handle "C:\prog.exe" -flag style strings defensively.
    if " " in raw and not Path(raw).exists():
        head = raw.split(" ", 1)[0]
        if Path(head).exists():
            return Path(head)
    try:
        return Path(raw)
    except (TypeError, ValueError):
        return None


_ICON_RE = re.compile(r"^(?P<path>.+?)(?:,(?P<idx>-?\d+))?\s*$")


def _parse_icon_location(icon_loc: str) -> tuple[Optional[Path], int]:
    m = _ICON_RE.match(icon_loc.strip().strip('"'))
    if not m:
        return None, 0
    path = _coerce_path(m.group("path") or "")
    idx = int(m.group("idx")) if m.group("idx") else 0
    return path, idx
