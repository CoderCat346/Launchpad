from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the project importable when running pytest from the repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_entries():
    """A small, deterministic list of AppEntry-like objects for tests.

    We build minimal stand-ins that satisfy what the filtering/mode
    code uses, so these tests don't require Windows.
    """
    from launchpad.discovery.start_menu import AppEntry
    from launchpad.platform_win.lnk import ResolvedShortcut

    def make(name: str, target: str, args: str = "") -> AppEntry:
        return AppEntry(
            name=name,
            lnk_path=Path(f"C:/Menu/{name}.lnk"),
            resolved=ResolvedShortcut(
                target=Path(target),
                arguments=args,
                working_dir=None,
                icon_path=None,
            ),
            source_folder=Path("C:/Menu"),
        )

    return [
        make("Firefox",           r"C:\Program Files\Mozilla Firefox\firefox.exe"),
        make("Firefox (safe)",    r"C:\Program Files\Mozilla Firefox\firefox.exe", "-safe-mode"),
        make("Visual Studio Code", r"C:\Users\me\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
        make("Notepad",           r"C:\Windows\System32\notepad.exe"),
        make("Calculator",        r"C:\Windows\System32\calc.exe"),
        make("Edge",              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
