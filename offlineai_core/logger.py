import logging
import logging.handlers
from pathlib import Path

def setup_enterprise_logging(base_dir: str, level: str = "INFO") -> None:
    """
    Konfiguriert das systemweite Logging mit Dateirotation für den Offline-Betrieb.
    """
    log_dir = Path(base_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "offlineai_audit.log"
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Der Root-Logger wird konfiguriert
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Alte Handler entfernen (z.B. aus dem Bootstrap), um doppelte Logs zu vermeiden
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Formatter: Zeit, Modul, Loglevel und die eigentliche Nachricht
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (für die Live-Sicht)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler (für das Audit-Log auf dem Windows-Server)
    # Max 10 MB pro Datei, behalte die letzten 5 Dateien
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    logging.getLogger(__name__).info("Enterprise Audit-Logging initialisiert.")
