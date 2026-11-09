from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QIcon, QPixmap


shell32 = ctypes.windll.shell32  # type: ignore[attr-defined]
user32 = ctypes.windll.user32    # type: ignore[attr-defined]

SHGFI_ICON         = 0x000000100
SHGFI_LARGEICON    = 0x000000000
SHGFI_SMALLICON    = 0x000000001
SHGFI_USEFILEATTRIBUTES = 0x000000010


class _SHFILEINFOW(ctypes.Structure):
    _fields_ = [
        ("hIcon",         wintypes.HICON),
        ("iIcon",         ctypes.c_int),
        ("dwAttributes",  wintypes.DWORD),
        ("szDisplayName", ctypes.c_wchar * 260),
        ("szTypeName",    ctypes.c_wchar * 80),
    ]


def shell_icon(path: Optional[Path], small: bool = True) -> Optional[QIcon]:
    """Return the shell icon for a file path.

    Uses SHGetFileInfoW to obtain an HICON and converts it to a QPixmap
    via Qt's Windows helper. The HICON is destroyed afterwards.
    Returns None if no icon could be obtained.
    """
    if path is None:
        return None
    try:
        path_str = str(path)
    except Exception:
        return None

    flags = SHGFI_ICON | (SHGFI_SMALLICON if small else SHGFI_LARGEICON)
    # If the file does not exist, ask the shell to use file attributes
    # so we still get a reasonable generic icon.
    if not path.exists():
        flags |= SHGFI_USEFILEATTRIBUTES

    info = _SHFILEINFOW()
    ret = shell32.SHGetFileInfoW(
        path_str, 0, ctypes.byref(info), ctypes.sizeof(info), flags
    )
    if not ret or not info.hIcon:
        return None
    try:
        pixmap = QPixmap.fromWinHICON(info.hIcon)
        if pixmap.isNull():
            return None
        return QIcon(pixmap)
    finally:
        user32.DestroyIcon(info.hIcon)
