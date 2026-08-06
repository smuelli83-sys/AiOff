class OfflineAIError(Exception):
    """Basisklasse aller OfflineAI-Ausnahmen."""


class ConfigurationError(OfflineAIError):
    """Fehler beim Laden oder Validieren der Konfiguration."""


class RegistryError(OfflineAIError):
    """Fehler innerhalb der Registry."""


class ProviderError(OfflineAIError):
    """Fehler eines Providers."""


class BuildError(OfflineAIError):
    """Fehler während des Build-Prozesses."""
