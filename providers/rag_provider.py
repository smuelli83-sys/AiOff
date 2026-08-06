import os
import subprocess
import urllib.request
import urllib.error
import time
from typing import Any, Dict
from pathlib import Path

from offlineai_core.provider import Provider

class RAGProvider(Provider):
    def __init__(self, name: str, config: Dict[str, Any], event_bus: Any):
        super().__init__(name, config, event_bus)
        
        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 8000)
        
        base_dir = Path(self.config.get("base_dir", "C:\\OfflineAI"))
        self.provider_dir = base_dir / "providers" / "rag"
        
        self.exe_path = self.provider_dir / "chroma.exe"
        self.db_path = self.provider_dir / "vectordb"
        self.models_dir = self.provider_dir / "models"
        
        self.process: subprocess.Popen | None = None

    def initialize(self) -> bool:
        self.logger.info("Initialisiere RAG/ChromaDB Provider...")
        
        if not self.exe_path.exists():
            self.logger.error(f"Kritischer Fehler: ChromaDB Executable fehlt: {self.exe_path}")
            return False
            
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            self.models_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Konnte RAG-Verzeichnisse nicht erstellen: {e}")
            return False
            
        return True

    def start(self) -> bool:
        self.logger.info("Starte Vektordatenbank für Dokumenten-KI...")
        
        env = os.environ.copy()
        # ChromaDB Konfiguration für den Offline-Betrieb
        env["CHROMA_SERVER_HOST"] = self.host
        env["CHROMA_SERVER_HTTP_PORT"] = str(self.port)
        env["PERSIST_DIRECTORY"] = str(self.db_path)
        env["ANONYMIZED_TELEMETRY"] = "False" # Wichtig für Enterprise/Air-Gap

        try:
            self.process = subprocess.Popen(
                [str(self.exe_path), "run"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(2)
            if self.process.poll() is not None:
                _, err = self.process.communicate()
                self.logger.error(f"ChromaDB abgestürzt. stderr: {err}")
                return False
            
            self.logger.info(f"Vektordatenbank läuft auf Port {self.port}.")
            
            # Teile dem Netzwerk mit, dass die Dokumenten-KI bereit ist und wo die Modelle liegen
            self.event_bus.publish("rag_started", {
                "url": f"http://{self.host}:{self.port}",
                "models_path": str(self.models_dir)
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Starten von ChromaDB: {e}")
            return False

    def stop(self) -> bool:
        self.logger.info("Beende RAG-Dienst...")
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        return True

    def health_check(self) -> bool:
        url = f"http://{self.host}:{self.port}/api/v1/heartbeat"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status == 200
        except Exception:
            return False
