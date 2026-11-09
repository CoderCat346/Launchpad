from __future__ import annotations

from typing import List, Sequence

from .base import SearchMode


class ModeManager:
    """Holds the registered modes and the currently active one.

    `next()` cycles to the next available mode. With a single mode it
    is a safe no‑op, which keeps Tab from moving focus out of the
    search field in the MVP.
    """

    def __init__(self, modes: Sequence[SearchMode]) -> None:
        if not modes:
            raise ValueError("ModeManager requires at least one mode")
        self._modes: List[SearchMode] = list(modes)
        self._index = 0

    @property
    def current(self) -> SearchMode:
        return self._modes[self._index]

    @property
    def all(self) -> List[SearchMode]:
        return list(self._modes)

    def next(self) -> SearchMode:
        if len(self._modes) <= 1:
            return self.current
        start = self._index
        while True:
            self._index = (self._index + 1) % len(self._modes)
            if self._modes[self._index].is_available():
                return self._modes[self._index]
            if self._index == start:
                return self.current

    def set_by_id(self, mode_id: str) -> bool:
        for i, m in enumerate(self._modes):
            if m.id == mode_id and m.is_available():
                self._index = i
                return True
        return False
