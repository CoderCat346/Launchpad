from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models.result import ResultItem


class SearchMode(ABC):
    """Abstract search mode.

    A mode owns its own data source and knows how to turn a query into
    an ordered list of results. Modes are intentionally synchronous in
    the MVP; the signature is designed so that a future async variant
    can be added (e.g. `search_async`) without changing the UI or the
    ModeManager.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        ...

    @abstractmethod
    def search(self, query: str) -> List[ResultItem]:
        ...

    def is_available(self) -> bool:
        """Modes may disable themselves until data is ready."""
        return True
