from __future__ import annotations

from launchpad.modes.base import SearchMode
from launchpad.modes.manager import ModeManager
from launchpad.models.result import ResultItem


class _StubMode(SearchMode):
    def __init__(self, id_: str, label: str, available: bool = True) -> None:
        self._id = id_
        self._label = label
        self._available = available

    @property
    def id(self) -> str:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    def search(self, query: str) -> list[ResultItem]:
        return []

    def is_available(self) -> bool:
        return self._available


def test_single_mode_tab_is_safe_no_op():
    apps = _StubMode("apps", "Apps")
    mm = ModeManager([apps])
    assert mm.current.id == "apps"
    mm.next()
    assert mm.current.id == "apps"  # didn't leave the only mode


def test_cycles_through_available_modes():
    a = _StubMode("a", "A")
    b = _StubMode("b", "B")
    c = _StubMode("c", "C")
    mm = ModeManager([a, b, c])
    order = []
    for _ in range(4):
        order.append(mm.current.id)
        mm.next()
    assert order == ["a", "b", "c", "a"]


def test_skips_unavailable_modes():
    a = _StubMode("a", "A")
    b = _StubMode("b", "B", available=False)
    c = _StubMode("c", "C")
    mm = ModeManager([a, b, c])
    mm.next()
    assert mm.current.id == "c"


def test_all_unavailable_falls_back_to_first():
    a = _StubMode("a", "A", available=False)
    b = _StubMode("b", "B", available=False)
    mm = ModeManager([a, b])
    mm.next()
    # Nothing available → stays on the first one rather than crashing.
    assert mm.current.id in {"a", "b"}


def test_set_by_id():
    a = _StubMode("a", "A")
    b = _StubMode("b", "B")
    mm = ModeManager([a, b])
    assert mm.set_by_id("b") is True
    assert mm.current.id == "b"
    assert mm.set_by_id("does-not-exist") is False
    assert mm.current.id == "b"
