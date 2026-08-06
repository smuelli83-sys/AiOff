import logging
from .configuration import Configuration
from .provider_manager import ProviderManager
from .events import EventBus # Angenommen, wir nutzen einen simplen EventBus

logger = logging.getLogger(__name__)

class Kernel:
    def __init__(self, config: Configuration):
        self.config = config
        self.event_bus = EventBus()
        # Der ProviderManager bekommt den EventBus, damit Module kommunizieren können
        self.provider_manager = ProviderManager(self.config, self.event_bus)
        self._is_running = False

    def start(self):
        """Startet den Kernel und alle aktivierten Provider."""
        logger.info("Kernel initialisiert. Lade Provider...")
        
        strict_mode = self.config.kernel.get('strict_mode', True)
        
        try:
            # Lässt den Manager alle in der Config definierten Provider laden
            self.provider_manager.load_providers()
            self._is_running = True
            
            logger.info("Alle Systeme online. OfflineAI Kernel läuft.")
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Provider: {e}")
            if strict_mode:
                logger.critical("Strict Mode ist aktiv. Fahre System herunter.")
                self.stop()
                raise

    def stop(self):
        """Fährt das System kontrolliert herunter."""
        logger.info("Leite Shutdown-Sequenz ein...")
        self.provider_manager.shutdown_providers()
        self._is_running = False
        logger.info("System erfolgreich heruntergefahren.")
