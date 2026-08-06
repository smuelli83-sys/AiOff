import os
import hashlib
import urllib.request
import subprocess
import sys
import yaml

class OfflineBuilder:
    def __init__(self, yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.payload_dir = "payload"
        os.makedirs(self.payload_dir, exist_ok=True)
        self.manifest = {}

    def download_file(self, url, target_path):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
            print(f"  [CACHE] Überspringe (bereits vorhanden): {target_path}")
            return
        print(f"  -> Lade herunter: {target_path}")
        urllib.request.urlretrieve(url, target_path)

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def run(self):
        print("[*] Starte Offline-Builder...")
        downloads = self.config.get("downloads", {})

        # 1. Ollama
        if "ollama" in downloads:
            item = downloads["ollama"]
            self.download_file(item["url"], os.path.join(self.payload_dir, item["target_path"]))
            self.manifest[item["target_path"]] = self.calculate_sha256(os.path.join(self.payload_dir, item["target_path"]))

        # 2. WinSW
        if "winsw" in downloads:
            item = downloads["winsw"]
            self.download_file(item["url"], os.path.join(self.payload_dir, item["target_path"]))
            self.manifest[item["target_path"]] = self.calculate_sha256(os.path.join(self.payload_dir, item["target_path"]))

        # 3. LLM Modelle
        for model in downloads.get("models", []):
            self.download_file(model["url"], os.path.join(self.payload_dir, model["target_path"]))
            self.manifest[model["target_path"]] = self.calculate_sha256(os.path.join(self.payload_dir, model["target_path"]))

        # 4. Embedding & Reranker
        for key in ["embedding_model", "reranker_model"]:
            if key in downloads:
                item = downloads[key]
                self.download_file(item["url"], os.path.join(self.payload_dir, item["target_path"]))
                self.manifest[item["target_path"]] = self.calculate_sha256(os.path.join(self.payload_dir, item["target_path"]))

        # 5. Python Wheels (ChromaDB, Open WebUI etc.) für Python 3.11 cachen
        packages = downloads.get("pip_packages", [])
        if packages:
            wheel_dir = os.path.join(self.payload_dir, "providers/rag/wheels")
            os.makedirs(wheel_dir, exist_ok=True)
            print("  -> Lade Python-Pakete für Python 3.11 herunter...")
            subprocess.run([
                sys.executable, "-m", "pip", "download", 
                *packages, 
                "-d", wheel_dir, 
                "--no-deps",
                "--python-version", "3.11",
                "--platform", "win_amd64",
                "--abi", "cp311"
            ], check=True)

        # 6. Open WebUI Docker Image als Tarball exportieren
        webui = downloads.get("webui_image")
        if webui:
            img_name = webui["image_name"]
            tar_rel_path = webui["target_path"]
            tar_abs_path = os.path.join(self.payload_dir, tar_rel_path)
            os.makedirs(os.path.dirname(tar_abs_path), exist_ok=True)
            
            print(f"  -> Ziehe Open WebUI Docker-Image ({img_name})...")
            subprocess.run(["docker", "pull", img_name], check=True)
            
            print(f"  -> Exportiere Docker-Image nach {tar_abs_path}...")
            subprocess.run(["docker", "save", img_name, "-o", tar_abs_path], check=True)
            
            self.manifest[tar_rel_path] = self.calculate_sha256(tar_abs_path)

        # Manifest schreiben
        with open("manifest.sha256", "w", encoding="utf-8") as f:
            for path, checksum in self.manifest.items():
                f.write(f"{checksum}  {path}\n")

        print("\n[*] Build komplett! Alle Dateien (inkl. Open WebUI Image) liegen im 'payload'-Ordner.")

if __name__ == "__main__":
    builder = OfflineBuilder("build.yaml")
    builder.run()