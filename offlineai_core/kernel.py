from pathlib import Path

from offlineai_core.configuration import Configuration
from offlineai_core.context import ApplicationContext


class Kernel:

    def __init__(self) -> None:
        self.context = ApplicationContext()

    def start(self) -> None:

        self.context.logger.info("Starting OfflineAI Enterprise")

        self.context.configuration = Configuration.load(
            Path("config/default.yaml")
        )

        self.context.logger.info("Configuration loaded")

        self.context.logger.info("Registry initialized")

        self.context.logger.info("Starting providers")

        self.context.provider_manager.startup()

        self.context.logger.info("Providers started")

        self.context.logger.info("Kernel ready")
