from typing import TYPE_CHECKING
from __future__ import annotations

from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from offlineai_core.context import ApplicationContext


class ProviderBase(ABC):
    """
    Basisklasse für alle OfflineAI Provider.

    Jeder Provider (Ollama, Docker, AD, OpenWebUI, ...)
    muss von dieser Klasse erben.
    """

    def __init__(self, context: "ApplicationContext") -> None:
        self._context = context

    @property
    @abstractmethod
    def id(self) -> str:
        """Eindeutige Provider-ID."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Anzeigename."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """Providerversion."""
        raise NotImplementedError

    @property
    def enabled(self) -> bool:
        return True

    @property
    def healthy(self) -> bool:
        return True

    @abstractmethod
    def install(self) -> None:
        """Provider installieren."""

    @abstractmethod
    def uninstall(self) -> None:
        """Provider entfernen."""

    @abstractmethod
    def configure(self) -> None:
        """Provider konfigurieren."""

    @abstractmethod
    def verify(self) -> bool:
        """Installation prüfen."""

    @abstractmethod
    def health(self) -> bool:
        """Gesundheitsprüfung."""

    def startup(self) -> None:
        """Optional beim Kernelstart."""
        pass

    def shutdown(self) -> None:
        """Optional beim Kernelstop."""
        pass
