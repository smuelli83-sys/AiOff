from offlineai_core.configuration import Configuration
from offlineai_core.logger import Logger
from offlineai_core.registry import Registry


class ApplicationContext:
    def __init__(self) -> None:
        self.logger = Logger()
        self.configuration = Configuration()
        self.registry = Registry()

from offlineai_core.provider_manager import ProviderManager
self.provider_manager = ProviderManager()
