from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from ..models.result import ResultItem
from ..platform_win.lnk import ResolvedShortcut, resolve_lnk


@dataclass
class AppEntry:
    """A discovered Start Menu entry.

    `name` is the shortcut's display name (file stem). `resolved` holds
    the target, arguments, working directory and icon location.
    """

    name: str
    lnk_path: Path
    resolved: ResolvedShortcut
    source_folder: Path = field(repr=False, default_factory=Path)

    def result_key(self) -> str:
        # Dedupe key: target + arguments (case‑insensitive).
        return f"{self.resolved.target.resolve().casefold()}|{self.resolved.arguments.casefold()}"

    def to_result(self) -> ResultItem:
        return ResultItem(
            key=self.result_key(),
            display_name=self.name,
            subtitle=str(self.resolved.target),
            launch_target=self.resolved.target,
            launch_args=self.resolved.arguments,
            launch_cwd=self.resolved.working_dir,
            icon=None,  # filled in asynchronously by IconPool
        )


def _default_start_menu_folders() -> list[Path]:
    folders: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        folders.append(Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    program_data = os.environ.get("ProgramData", r"C:\ProgramData")
    folders.append(Path(program_data) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    return folders


def discover_start_menu_entries(
    extra_folders: Optional[Iterable[Path]] = None,
) -> List[AppEntry]:
    """Enumerate Start Menu shortcuts and resolve them.

    - Scans both the current user's and the all‑users' Start Menu
      Programs folders, plus any `extra_folders`.
    - Skips unreadable or broken shortcuts silently.
    - Dedupes by (resolved target, arguments).
    """
    folders = _default_start_menu_folders()
    if extra_folders:
        folders.extend(Path(p) for p in extra_folders)

    seen: set[str] = set()
    results: list[AppEntry] = []

    for folder in folders:
        if not folder.exists():
            continue
        try:
            lnk_files: list[Path] = sorted(folder.rglob("*.lnk"))
        except OSError:
            continue
        for lnk_path in lnk_files:
            try:
                resolved = resolve_lnk(lnk_path)
            except Exception:
                # Malformed / unreadable .lnk — skip silently.
                continue
            if resolved is None:
                continue
            if not resolved.target.exists():
                # Broken shortcut (target missing). Skip.
                continue
            key = f"{resolved.target.resolve().casefold()}|{resolved.arguments.casefold()}"
            if key in seen:
                continue
            seen.add(key)
            results.append(
                AppEntry(
                    name=lnk_path.stem,
                    lnk_path=lnk_path,
                    resolved=resolved,
                    source_folder=folder,
                )
            )
    return results
