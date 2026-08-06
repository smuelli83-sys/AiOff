# offlineai-builder/build.py
import os
import yaml
import hashlib
import urllib.request
from pathlib import Path

class OfflineBuilder:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.payload_dir = Path(self.config.get("build_target", "payload"))
        self.manifest_path = Path("manifest.sha256")
        self.file_hashes = {}

    def run(self):
        print("=== OfflineAI Enterprise Builder ===")
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Downloads ausführen
        self._process_downloads()
        
        # 2. Manifest (SHA-256) generieren
        self._generate_manifest()
        
        print("\n=== Build erfolgreich abgeschlossen! ===")
        print(f"Kopiere den Ordner '{self.payload_dir}' und das 'manifest.sha256' auf den USB-Stick.")

    def _process_downloads(self):
        print("\n[*] Starte Downloads...")
        downloads = self.config.get("downloads", {})
        
        # Ollama Binary
        if "ollama" in downloads:
            self._download_file(downloads["ollama"]["url"], downloads["ollama"]["target_path"])
            
        # WinSW Wrapper
        if "winsw" in downloads:
            self._download_file(downloads["winsw"]["url"], downloads["winsw"]["target_path"])
            
        # KI-Modelle
        if "models" in downloads:
            for model in downloads["models"]:
                self._download_file(model["url"], model["target_path"])

    def _download_file(self, url: str, relative_target: str):
        target_path = self.payload_dir / relative_target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if target_path.exists():
            print(f"  -> Überspringe (bereits vorhanden): {relative_target}")
            return

        print(f"  -> Lade herunter: {relative_target}")
        try:
            # Lade die Datei in Chunks herunter (wichtig für große KI-Modelle)
            req = urllib.request.urlopen(url)
            with open(target_path, 'wb') as f:
                while True:
                    chunk = req.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:
            print(f"     FEHLER beim Download von {url}: {e}")

    def _generate_manifest(self):
        print("\n[*] Generiere SHA-256 Integritäts-Manifest...")
        
        # Geht durch alle Dateien im Payload-Ordner
        for root, _, files in os.walk(self.payload_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.payload_dir)
                
                # Berechne Hash
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                
                self.file_hashes[str(rel_path)] = sha256_hash.hexdigest()
        
        # Schreibe Manifest-Datei
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            for path, file_hash in self.file_hashes.items():
                f.write(f"{file_hash} *{path}\n")
                
        print(f"  -> {len(self.file_hashes)} Dateien in {self.manifest_path} signiert.")

if __name__ == "__main__":
    builder = OfflineBuilder("build.yaml")
    builder.run()
