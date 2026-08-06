from __future__ import annotations

from offlineai_core.configuration import Configuration
from offlineai_core.logger import Logger
from offlineai_core.provider_manager import ProviderManager
from offlineai_core.registry import Registry


class ApplicationContext:
    """
    Zentraler Anwendungskontext.

    Alle Kernkomponenten werden hier einmal erzeugt und
    anschließend über den Context an den Rest des Systems
    weitergereicht.
    """

    def __init__(self) -> None:
        self.logger = Logger()
        self.configuration = Configuration()
        self.registry = Registry()
        self.provider_manager = ProviderManager()
