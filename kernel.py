from pathlib import Path

from offlineai_core.configuration import Configuration
from offlineai_core.context import ApplicationContext


class Kernel:

    def __init__(self):

        self.context = ApplicationContext()

    def start(self):

        self.context.logger.info("Starting OfflineAI Enterprise")

        self.context.configuration = Configuration.load(
            Path("config/default.yaml")
        )

        self.context.logger.info("Configuration loaded")

        self.context.logger.info(
            f"Workspace: {self.context.configuration.paths.workspace}"
        )

        self.context.logger.info("Kernel Ready")
