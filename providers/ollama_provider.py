import os
import subprocess
import urllib.request
import urllib.error
import json
import time
from typing import Any, Dict
from pathlib import Path

from offlineai_core.provider import Provider

class OllamaProvider(Provider):
    def __init__(self, name: str, config: Dict[str, Any], event_bus: Any):
        super().__init__(name, config, event_bus)
        
        # Netzwerk-Konfiguration aus der YAML laden (Fallbacks auf localhost/11434)
        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 11434)
        
        # Wir gehen davon aus, dass base_dir global in der System-Config steht
        base_dir = Path(self.config.get("base_dir", "C:\\OfflineAI"))
        
        # Strikte Pfade für das Air-Gap-System definieren
        self.provider_dir = base_dir / "providers" / "ollama"
        self.exe_path = self.provider_dir / "ollama.exe"
        self.models_dir = self.provider_dir / "models"
        
        self.process: subprocess.Popen | None = None

    def initialize(self) -> bool:
        self.logger.info(f"Initialisiere Ollama Provider (Host: {self.host}:{self.port})")
        
        # 1. Existiert die Binary auf dem Server? (Wurde sie vom Installer kopiert?)
        if not self.exe_path.exists():
            self.logger.error(f"Kritischer Fehler: Ollama Executable fehlt unter {self.exe_path}")
            return False
            
        # 2. Modell-Ordner sicherstellen, damit Ollama Schreibrechte hat
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Konnte Modell-Verzeichnis {self.models_dir} nicht erstellen: {e}")
            return False
            
        return True

    def start(self) -> bool:
        self.logger.info("Starte Ollama-Dienst...")
        
        # Umgebungsvariablen anpassen, um Ollama in unser Offline-Konzept zu zwingen
        env = os.environ.copy()
        env["OLLAMA_HOST"] = f"{self.host}:{self.port}"
        
        # Zwingt Ollama, die isolierten GGUF-Modelle aus unserem Ordner zu laden
        env["OLLAMA_MODELS"] = str(self.models_dir)
        
        # Telemetrie und History deaktivieren (Best Practice für Enterprise/Air-Gap)
        env["OLLAMA_NOHISTORY"] = "1" 

        try:
            # Subprozess unter Windows starten
            self.process = subprocess.Popen(
                [str(self.exe_path), "serve"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                # Verhindert, dass auf dem Windows-Server ein Terminal-Fenster aufpoppt
                creationflags=subprocess.CREATE_NO_WINDOW 
            )
            
            # Kurze Wartezeit (Boot-Delay), um zu prüfen, ob der Prozess sofort abstürzt
            time.sleep(2)
            if self.process.poll() is not None:
                _, err = self.process.communicate()
                self.logger.error(f"Ollama ist direkt nach dem Start abgestürzt. stderr: {err}")
                return False
            
            self.logger.info("Ollama-Prozess läuft im Hintergrund.")
            
            # Event feuern: Andere Provider (wie Open WebUI) können jetzt reagieren
            self.event_bus.publish("ollama_started", {"host": self.host, "port": self.port})
            return True
            
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler beim Starten des Ollama-Prozesses: {e}")
            return False

    def stop(self) -> bool:
        self.logger.info("Beende Ollama-Dienst...")
        if self.process and self.process.poll() is None:
            try:
                # Graceful Shutdown versuchen
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("Ollama erfolgreich beendet.")
            except subprocess.TimeoutExpired:
                self.logger.warning("Ollama reagiert nicht auf terminate(). Erzwinge kill()...")
                self.process.kill()
        
        self.process = None
        self.event_bus.publish("ollama_stopped")
        return True

    def health_check(self) -> bool:
        """Prüft über die REST-API, ob der Dienst noch antwortet."""
        url = f"http://{self.host}:{self.port}/api/version"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    self.logger.debug(f"Health Check OK. Version: {data.get('version')}")
                    return True
        except urllib.error.URLError as e:
            self.logger.warning(f"Health Check fehlgeschlagen (Verbindung): {e.reason}")
        except Exception as e:
            self.logger.warning(f"Health Check fehlgeschlagen (Unerwartet): {e}")
            
        return False
