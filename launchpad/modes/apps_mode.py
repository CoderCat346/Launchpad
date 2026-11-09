from __future__ import annotations

from typing import List

from ..discovery.start_menu import AppEntry
from ..models.result import ResultItem
from .base import SearchMode


class AppsMode(SearchMode):
    """Searches Start Menu entries discovered by the app discovery layer."""

    id = "apps"
    label = "Apps"

    def __init__(self) -> None:
        self._entries: list[AppEntry] = []
        self._ready = False

    # --- data feeding -------------------------------------------------

    def clear(self) -> None:
        self._entries = []
        self._ready = False

    def add_entry(self, entry: AppEntry) -> None:
        self._entries.append(entry)
        self._ready = True

    def snapshot_results(self) -> List[ResultItem]:
        return [e.to_result() for e in self._entries]

    # --- SearchMode ---------------------------------------------------

    def is_available(self) -> bool:
        return True  # always available, even while loading

    def search(self, query: str) -> List[ResultItem]:
        q = query.strip().casefold()
        pool = self._entries

        if not q:
            chosen = pool
        else:
            chosen = [e for e in pool if _matches(e, q)]

        # Stable sort: prefix matches first, then alphabetical.
        def keyfn(e: AppEntry) -> tuple[int, str]:
            name = e.name.casefold()
            return (0 if name.startswith(q) else 1, name)

        chosen = sorted(chosen, key=keyfn)
        return [e.to_result() for e in chosen]


def _matches(entry: AppEntry, q: str) -> bool:
    if q in entry.name.casefold():
        return True
    if q in entry.resolved.target.name.casefold():
        return True
    return False
