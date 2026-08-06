import os
import subprocess
import urllib.request
import urllib.error
import time
from typing import Any, Dict
from pathlib import Path

from offlineai_core.provider import Provider

class OpenWebUIProvider(Provider):
    def __init__(self, name: str, config: Dict[str, Any], event_bus: Any):
        super().__init__(name, config, event_bus)
        
        # Netzwerkkonfiguration für den LAN-Zugriff
        self.host = self.config.get("host", "0.0.0.0") # 0.0.0.0 macht es im LAN verfügbar
        self.port = self.config.get("port", 8080)
        
        base_dir = Path(self.config.get("base_dir", "C:\\OfflineAI"))
        self.provider_dir = base_dir / "providers" / "open_webui"
        
        # Der Pfad zur isolierten Python-Umgebung (venv) für das WebUI
        self.python_exe = self.provider_dir / "venv" / "Scripts" / "python.exe"
        self.data_dir = self.provider_dir / "data" # Hier speichert WebUI seine SQLite/Nutzerdaten
        
        self.process: subprocess.Popen | None = None
        self.ollama_url = "http://127.0.0.1:11434" # Standard-Fallback

        # Event-Listener registrieren: WebUI muss wissen, wo Ollama läuft
        self.event_bus.subscribe("ollama_started", self._on_ollama_started)

    def _on_ollama_started(self, payload: Dict[str, Any]) -> None:
        """Wird aufgerufen, sobald der Kernel meldet, dass Ollama online ist."""
        host = payload.get("host", "127.0.0.1")
        port = payload.get("port", 11434)
        self.ollama_url = f"http://{host}:{port}"
        self.logger.info(f"Ollama-URL für WebUI aktualisiert: {self.ollama_url}")

    def initialize(self) -> bool:
        self.logger.info(f"Initialisiere Open WebUI (Netzwerk-Host: {self.host}:{self.port})")
        
        if not self.python_exe.exists():
            self.logger.error(f"Kritischer Fehler: Python-Umgebung für WebUI fehlt unter {self.python_exe}")
            return False
            
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Konnte WebUI-Datenverzeichnis nicht erstellen: {e}")
            return False
            
        return True

    def start(self) -> bool:
        self.logger.info("Starte Open WebUI Dienst...")
        
        # Umgebungsvariablen für das Frontend konfigurieren
        env = os.environ.copy()
        
        # 1. Netzwerk & Basis
        env["HOST"] = self.host
        env["PORT"] = str(self.port)
        env["DATA_DIR"] = str(self.data_dir)
        env["OLLAMA_BASE_URL"] = self.ollama_url
        
        # 2. Nutzerverwaltung & Sicherheit
        env["WEBUI_AUTH"] = "True"           # Erzwingt Login
        env["DEFAULT_USER_ROLE"] = "user"    # Neue Nutzer sind standardmäßig keine Admins
        
        # 3. Active Directory / LDAP Anbindung (falls in yaml konfiguriert)
        ad_config = self.config.get("active_directory", {})
        if ad_config.get("enabled", False):
            self.logger.info("Konfiguriere LDAP/Active Directory Anbindung...")
            env["ENABLE_LDAP"] = "True"
            env["LDAP_SERVER"] = ad_config.get("server", "ldap://localhost")
            env["LDAP_BASE_DN"] = ad_config.get("base_dn", "")
            env["LDAP_BIND_DN"] = ad_config.get("bind_dn", "")
            env["LDAP_BIND_PASSWORD"] = ad_config.get("bind_password", "")
            env["LDAP_USER_SEARCH_BASE"] = ad_config.get("user_search_base", "")
            env["LDAP_SEARCH_FILTER"] = ad_config.get("search_filter", "(sAMAccountName={0})")

        try:
            # Wir rufen das open-webui Modul über die isolierte Python-Umgebung auf
            self.process = subprocess.Popen(
                [str(self.python_exe), "-m", "open_webui.main"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(3) # Kurz warten, um Crash beim Start abzufangen
            if self.process.poll() is not None:
                _, err = self.process.communicate()
                self.logger.error(f"Open WebUI abgestürzt. stderr: {err}")
                return False
            
            self.logger.info(f"Open WebUI ist unter http://{self.host}:{self.port} im Netzwerk erreichbar.")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Starten von Open WebUI: {e}")
            return False

    def stop(self) -> bool:
        self.logger.info("Beende Open WebUI Dienst...")
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        self.process = None
        return True

    def health_check(self) -> bool:
        # Prüft, ob das Webinterface im Netzwerk erreichbar ist
        url = f"http://127.0.0.1:{self.port}/health" # Local Check reicht für den Kernel
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status == 200
        except Exception:
            return False
