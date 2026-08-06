from offlineai_core.context import ApplicationContext


class Kernel:

    def __init__(self) -> None:
        self.context = ApplicationContext()

    def start(self) -> None:

        self.context.logger.info("Starting OfflineAI Enterprise")

        self.context.logger.info("Loading Configuration")

        self.context.logger.info("Loading Registry")

        self.context.logger.info("Kernel Ready")

self.context.logger.info("Registry initialized")
