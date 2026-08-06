import logging
import importlib
from typing import Dict, Any, Optional
from .provider import Provider
from .configuration import Configuration

logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self, config: Configuration, event_bus: Any):
        self.config = config
        self.event_bus = event_bus
        self.active_providers: Dict[str, Provider] = {}
        
        # In der Praxis könnte man dies in eine registry.py auslagern oder 
        # Plugins dynamisch im Dateisystem suchen.
        self._registry = {
            "ollama": "providers.ollama.OllamaProvider",
            "active_directory": "providers.ad.ActiveDirectoryProvider",
            "open_webui": "providers.webui.OpenWebUIProvider"
        }

    def load_providers(self) -> None:
        """Lädt, initialisiert und startet alle aktivierten Provider aus der Config."""
        provider_configs = self.config.providers
        
        for name, p_config in provider_configs.items():
            if not p_config.get("enabled", False):
                logger.debug(f"Provider '{name}' ist in der Config deaktiviert. Überspringe.")
                continue
                
            logger.info(f"Lade Provider-Modul: {name}")
            provider_instance = self._instantiate_provider(name, p_config)
            
            if not provider_instance:
                continue

            if provider_instance.initialize():
                if provider_instance.start():
                    self.active_providers[name] = provider_instance
                    provider_instance.is_running = True
                    logger.info(f"Provider '{name}' erfolgreich gestartet und registriert.")
                else:
                    logger.error(f"Fehler beim Starten (start) des Providers '{name}'.")
            else:
                logger.error(f"Fehler bei der Initialisierung (initialize) von '{name}'.")

    def _instantiate_provider(self, name: str, config: Dict[str, Any]) -> Optional[Provider]:
        """Lädt die Provider-Klasse dynamisch anhand des Namens aus der Registry."""
        module_path = self._registry.get(name)
        if not module_path:
            logger.warning(f"Kein Modulpfad für Provider '{name}' in der Registry gefunden.")
            return None

        try:
            # Splittet z.B. "providers.ollama.OllamaProvider" in Modul und Klasse
            module_name, class_name = module_path.rsplit(".", 1)
            
            # Lädt das Python-Modul zur Laufzeit
            module = importlib.import_module(module_name)
            
            # Holt sich die Klasse aus dem Modul
            provider_class = getattr(module, class_name)
            
            # Instanziiert die Klasse mit den Basis-Parametern
            return provider_class(name, config, self.event_bus)
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Abbruch: Konnte Provider-Klasse für '{name}' ({module_path}) nicht laden. Fehler: {e}")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Instanziieren von '{name}': {e}")
            return None

    def check_health(self) -> Dict[str, bool]:
        """Führt einen Health-Check über alle aktiven Provider aus."""
        health_status = {}
        for name, provider in self.active_providers.items():
            try:
                status = provider.health_check()
                health_status[name] = status
                if not status:
                    logger.warning(f"Health-Check für Provider '{name}' fehlgeschlagen!")
            except Exception as e:
                logger.error(f"Exception beim Health-Check von '{name}': {e}")
                health_status[name] = False
        return health_status

    def shutdown_providers(self) -> None:
        """Fährt alle aktiven Provider sicher herunter."""
        for name, provider in self.active_providers.items():
            logger.info(f"Sende Shutdown-Signal an Provider: {name}")
            try:
                if provider.is_running:
                    provider.stop()
                    provider.is_running = False
            except Exception as e:
                logger.error(f"Fehler beim Herunterfahren des Providers '{name}': {e}")
        
        self.active_providers.clear()
        logger.info("Alle Provider wurden beendet.")
