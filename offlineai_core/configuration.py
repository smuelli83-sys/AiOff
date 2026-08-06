import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Wird geworfen, wenn die Konfiguration fehlerhaft oder unvollständig ist."""
    pass

@dataclass
class Configuration:
    system: Dict[str, Any] = field(default_factory=dict)
    kernel: Dict[str, Any] = field(default_factory=dict)
    providers: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_from_yaml(cls, file_path: str | Path) -> 'Configuration':
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Konfigurationsdatei nicht gefunden: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            logger.info(f"Konfiguration erfolgreich geladen von: {path}")
            return cls(
                system=data.get('system', {}),
                kernel=data.get('kernel', {}),
                providers=data.get('providers', {})
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Fehler beim Parsen der YAML-Datei: {e}")

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Holt die Konfiguration für einen spezifischen Provider sicher ab."""
        return self.providers.get(provider_name, {})
