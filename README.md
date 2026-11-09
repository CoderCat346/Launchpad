# Launchpad

A compact, keyboard‑driven app launcher for Windows 10/11, written in Python and PySide6.

## Features (MVP)

- Frameless, compact search window.
- Searches Windows Start Menu entries (current user + all users).
- Resolves `.lnk` targets, preserves arguments and working directory, extracts shell icons.
- Keyboard‑first: type to filter, ↑/↓ to navigate, Enter to launch, Esc to close, Tab to switch modes.
- Clean mode abstraction ready for Files / Web / Terminal / URL modes.
- Discovery and icon loading run off the UI thread.

## Requirements

- Windows 10 or 11
- Python 3.11+

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The window opens in the center of the primary screen. Type to filter, press Enter to launch, Esc to close.

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

## Configuration

User settings live in `launchpad/config.py`. The global hotkey, "start with Windows", and tray behavior are not implemented in the MVP but are designed to be added there without touching the UI or search logic.

## Windows‑specific notes

- Uses `pywin32` (`WScript.Shell`) to read `.lnk` files and `SHGetFileInfo` to extract shell icons.
- Only Start Menu Programs folders are scanned; the rest of the disk is never touched.
- Broken or inaccessible shortcuts are skipped silently.
- Duplicate shortcuts (same resolved target + arguments) are collapsed.
