from __future__ import annotations

"""Tests for shortcut resolution and discovery error handling.

These tests are written to run on any platform. Where we need to
exercise Windows-only code paths, we patch the resolver so the rest
of the discovery logic is covered without requiring pywin32.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from launchpad.discovery.start_menu import discover_start_menu_entries
from launchpad.platform_win.lnk import ResolvedShortcut, _parse_icon_location


def test_parse_icon_location_with_index():
    path, idx = _parse_icon_location(r"C:\Program Files\App\app.exe,2")
    assert path == Path(r"C:\Program Files\App\app.exe")
    assert idx == 2


def test_parse_icon_location_without_index():
    path, idx = _parse_icon_location(r"C:\icons\app.ico")
    assert path == Path(r"C:\icons\app.ico")
    assert idx == 0


def test_parse_icon_location_quoted():
    path, idx = _parse_icon_location(r'"C:\Program Files\App\app.exe",0')
    assert path == Path(r"C:\Program Files\App\app.exe")
    assert idx == 0


def test_discovery_skips_broken_shortcuts(tmp_path: Path):
    # Build a fake Start Menu tree with two .lnk files.
    menu = tmp_path / "Programs"
    menu.mkdir()
    (menu / "Good.lnk").write_bytes(b"")
    (menu / "Broken.lnk").write_bytes(b"")

    target_existing = tmp_path / "real.exe"
    target_existing.write_bytes(b"")
    target_missing = tmp_path / "missing.exe"

    def fake_resolve(lnk_path: Path):
        name = lnk_path.stem
        if name == "Good":
            return ResolvedShortcut(
                target=target_existing,
                arguments="",
                working_dir=None,
                icon_path=None,
            )
        if name == "Broken":
            # Pretend we resolved it, but the target is missing.
            return ResolvedShortcut(
                target=target_missing,
                arguments="",
                working_dir=None,
                icon_path=None,
            )
        return None

    with patch(
        "launchpad.discovery.start_menu.resolve_lnk", side_effect=fake_resolve
    ), patch(
        "launchpad.discovery.start_menu._default_start_menu_folders",
        return_value=[menu],
    ):
        entries = discover_start_menu_entries()

    names = [e.name for e in entries]
    assert "Good" in names
    assert "Broken" not in names


def test_discovery_dedupes_same_target_and_args(tmp_path: Path):
    menu_a = tmp_path / "user"
    menu_b = tmp_path / "allusers"
    menu_a.mkdir(); menu_b.mkdir()
    (menu_a / "App.lnk").write_bytes(b"")
    (menu_b / "App.lnk").write_bytes(b"")

    target = tmp_path / "app.exe"
    target.write_bytes(b"")

    def fake_resolve(lnk_path: Path):
        return ResolvedShortcut(
            target=target, arguments="", working_dir=None, icon_path=None
        )

    with patch(
        "launchpad.discovery.start_menu.resolve_lnk", side_effect=fake_resolve
    ), patch(
        "launchpad.discovery.start_menu._default_start_menu_folders",
        return_value=[menu_a, menu_b],
    ):
        entries = discover_start_menu_entries()

    assert len(entries) == 1


def test_discovery_distinguishes_same_target_different_args(tmp_path: Path):
    menu = tmp_path / "user"
    menu.mkdir()
    (menu / "App.lnk").write_bytes(b"")
    (menu / "App (other).lnk").write_bytes(b"")

    target = tmp_path / "app.exe"
    target.write_bytes(b"")

    calls = iter(["", "--profile=work"])

    def fake_resolve(lnk_path: Path):
        return ResolvedShortcut(
            target=target,
            arguments=next(calls),
            working_dir=None,
            icon_path=None,
        )

    with patch(
        "launchpad.discovery.start_menu.resolve_lnk", side_effect=fake_resolve
    ), patch(
        "launchpad.discovery.start_menu._default_start_menu_folders",
        return_value=[menu],
    ):
        entries = discover_start_menu_entries()

    assert len(entries) == 2


def test_discovery_handles_resolver_exception(tmp_path: Path):
    menu = tmp_path / "user"
    menu.mkdir()
    (menu / "Weird.lnk").write_bytes(b"")

    def fake_resolve(lnk_path: Path):
        raise RuntimeError("malformed lnk")

    with patch(
        "launchpad.discovery.start_menu.resolve_lnk", side_effect=fake_resolve
    ), patch(
        "launchpad.discovery.start_menu._default_start_menu_folders",
        return_value=[menu],
    ):
        # Must not raise.
        entries = discover_start_menu_entries()

    assert entries == []
