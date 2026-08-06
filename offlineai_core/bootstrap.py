import sys
import logging
from pathlib import Path
from .configuration import Configuration, ConfigurationError
from .kernel import Kernel

def setup_initial_logging(level: str = "INFO"):
    """Richtet das grundlegende Logging für den Startvorgang ein."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def boot_system(config_path: str | Path) -> Kernel:
    """Initialisiert das System und startet den Kernel."""
    setup_initial_logging()
    logger = logging.getLogger("Bootstrap")
    
    logger.info("Starte OfflineAI Enterprise Boot-Sequenz...")
    
    try:
        # 1. Konfiguration laden
        config = Configuration.load_from_yaml(config_path)
        
        # Loglevel ggf. anpassen basierend auf Config
        if 'log_level' in config.system:
            logger.setLevel(getattr(logging, config.system['log_level'].upper(), logging.INFO))
            
        # 2. Kernel instanziieren und starten
        kernel = Kernel(config)
        kernel.start()
        
        return kernel
        
    except ConfigurationError as e:
        logger.critical(f"Boot-Abbruch: Konfigurationsfehler - {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unerwarteter kritischer Fehler beim Booten: {e}", exc_info=True)
        sys.exit(1)
