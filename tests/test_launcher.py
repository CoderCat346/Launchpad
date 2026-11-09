from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from launchpad.models.launcher import Launcher, _split_args, _read_url_file
from launchpad.models.result import ResultItem


def test_split_args_empty():
    assert _split_args("") == []
    assert _split_args("   ") == []


def test_split_args_quoted():
    assert _split_args(r'--title="Hello world" --x=1') == [
        "--title=Hello world",
        "--x=1",
    ]


def test_read_url_file_extracts_url(tmp_path: Path):
    p = tmp_path / "site.url"
    p.write_text("[InternetShortcut]\nURL=https://example.com\n", encoding="utf-8")
    assert _read_url_file(p) == "https://example.com"


def test_read_url_file_missing_returns_none(tmp_path: Path):
    assert _read_url_file(tmp_path / "nope.url") is None


def test_launch_executable_uses_qprocess(tmp_path: Path):
    exe = tmp_path / "app.exe"
    exe.write_bytes(b"")
    item = ResultItem(
        key="k",
        display_name="App",
        launch_target=exe,
        launch_args="--foo --bar",
        launch_cwd=tmp_path,
    )
    launcher = Launcher()
    with patch("launchpad.models.launcher.QProcess") as qp:
        instance = qp.return_value
        instance.startDetached.return_value = (True, 0)
        ok = launcher.launch(item)
    assert ok is True
    instance.setWorkingDirectory.assert_called_once_with(str(tmp_path))
    instance.startDetached.assert_called_once_with(str(exe), ["--foo", "--bar"])


def test_launch_url_file_uses_desktop_services(tmp_path: Path):
    url_file = tmp_path / "site.url"
    url_file.write_text("[InternetShortcut]\nURL=https://example.com\n")
    item = ResultItem(
        key="k", display_name="Site", launch_target=url_file
    )
    launcher = Launcher()
    with patch("launchpad.models.launcher.QDesktopServices") as ds:
        ds.openUrl.return_value = True
        ok = launcher.launch(item)
    assert ok is True
    ds.openUrl.assert_called_once()
    assert "example.com" in ds.openUrl.call_args[0][0].toString()


def test_launch_missing_target_returns_false():
    item = ResultItem(key="k", display_name="x", launch_target=None)
    assert Launcher().launch(item) is False
