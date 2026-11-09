from __future__ import annotations

from launchpad.modes.apps_mode import AppsMode


def _populate(mode: AppsMode, entries) -> None:
    for e in entries:
        mode.add_entry(e)


def test_empty_query_returns_all(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    results = mode.search("")
    assert {r.display_name for r in results} == {e.name for e in sample_entries}


def test_case_insensitive_substring_match(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    names = [r.display_name for r in mode.search("fire")]
    assert names == ["Firefox", "Firefox (safe)"]


def test_prefix_matches_sort_first(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    names = [r.display_name for r in mode.search("fi")]
    # "Firefox" and "Firefox (safe)" are prefix matches; both come first.
    assert names[:2] == ["Firefox", "Firefox (safe)"]


def test_no_match_returns_empty(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    assert mode.search("zzz-not-a-real-app") == []


def test_matches_against_target_filename(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    names = [r.display_name for r in mode.search("code.exe")]
    assert names == ["Visual Studio Code"]


def test_clear_resets_state(sample_entries):
    mode = AppsMode()
    _populate(mode, sample_entries)
    assert mode.search("note") != []
    mode.clear()
    assert mode.search("note") == []
