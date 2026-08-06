import abc
import logging
from typing import Any, Dict

class Provider(abc.ABC):
    """
    Abstrakte Basisklasse für alle OfflineAI Provider.
    Jeder Provider muss diese Schnittstelle implementieren.
    """
    
    def __init__(self, name: str, config: Dict[str, Any], event_bus: Any):
        self.name = name
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"Provider.{self.name}")
        self.is_running = False

    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        Bereitet den Provider vor (z.B. Exe-Pfade prüfen, Ports validieren,
        Verzeichnisse auf der C:\-Platte anlegen).
        Gibt True zurück, wenn erfolgreich.
        """
        pass

    @abc.abstractmethod
    def start(self) -> bool:
        """Startet den eigentlichen Dienst des Providers als Subprozess oder Thread."""
        pass

    @abc.abstractmethod
    def stop(self) -> bool:
        """Beendet den Dienst sicher und gibt Ressourcen frei (Graceful Shutdown)."""
        pass
        
    @abc.abstractmethod
    def health_check(self) -> bool:
        """
        Prüft den Gesundheitszustand des Providers.
        Wichtig für den automatischen Restart und das Audit-Logging auf dem Air-Gap-Server.
        """
        pass
