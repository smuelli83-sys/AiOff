import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    """
    Zentraler Nachrichtenverteiler (Pub/Sub) für die asynchrone 
    Kommunikation zwischen dem Kernel und den Providern.
    """
    def __init__(self):
        # Speichert Event-Namen (z.B. "provider_started") und die Liste der Funktionen, 
        # die darauf reagieren wollen (Callbacks).
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Registriert eine Funktion, die auf ein bestimmtes Event hört."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Neuer Subscriber für Event '{event_type}' registriert.")

    def publish(self, event_type: str, payload: Any = None) -> None:
        """Verteilt ein Event an alle registrierten Abonnenten."""
        if event_type not in self._subscribers:
            return
            
        logger.debug(f"Event '{event_type}' ausgelöst. Benachrichtige {len(self._subscribers[event_type])} Subscriber.")
        
        for callback in self._subscribers[event_type]:
            try:
                callback(payload)
            except Exception as e:
                logger.error(f"Fehler bei der Ausführung eines Event-Callbacks für '{event_type}': {e}", exc_info=True)
