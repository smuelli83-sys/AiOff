Technische Projektdokumentation & IT-Sicherheitskonzept: AiOff Enterprise (Air-Gap)
Projektname: AiOff Enterprise
Architektur: Offline-First, Containerisiert / Modulare Microservices, Lokale Inferenz via Ollama, Vektordatenbank (ChromaDB) und Open WebUI.
Zielhardware: Windows-11-Server (Intel Core Ultra, 64 GB DDR5-RAM, NVIDIA RTX A1000 mit 8 GB VRAM).

1. Systemarchitektur & Komponenten
  Das System ist vollständig von externen Netzen getrennt (Air-Gapped) und läuft als autarker Windows-Dienst im lokalen Netzwerk.
  •	Inferenz-Engine (Ollama): Verwaltet die lokalen Sprachmodelle und steuert die GPU-/RAM-Lastverteilung (VRAM-Auslagerung + Hybrid-RAM).
  •	Frontend (Open WebUI): Bietet die Web-Oberfläche für Anwender. Beinhaltet eine Active-Directory-Anbindung (LDAP) für die Benutzerauthentifizierung.
  •	Wissensdatenbank (ChromaDB & Embedding): Ein lokaler RAG-Dienst (Retrieval-Augmented Generation) mit einem ONNX-Embedding-Modell (all-MiniLM-L6-v2) für die semantische Suche in lokalen Dokumenten (PDF, Word, Excel).
  •	Prozessüberwachung (WinSW): Wickelt die im Hintergrund laufenden Provider als standardmäßige Windows-Dienste ab.
Das 5-Modell-Portfolio (Hardware-optimiert)
  1.	qwen3-fast (Qwen3 7B Instruct): 100% im VRAM der RTX A1000 für blitzschnelle Alltags-Chats.
  2.	qwen3.6-27b (Qwen 3.6 27B): Hybrid-Modus (8 GB VRAM + 64 GB DDR5-RAM) als High-End-Allrounder für komplexe Logik.
  3.	qwen3.6-35b (Qwen 3.6 35B-A3B MoE): Mixture-of-Experts im Hybrid-Modus für maximale RAG- und Textanalyse-Tiefe.
  4.	deepseek-coder (DeepSeek-Coder-V2-Lite-Instruct): Speziell optimierter Code-Spezialist für Softwareentwicklung und Skripterstellung.
  5.	llama3-8b (Meta Llama 3 8B): Stabiles Backup-Modell, das vollständig im VRAM läuft.

2. Installations- und Deployment-Prozess
Das Deployment erfolgt zweistufig: Über einen internetfähigen Builder (Sammeln & Packen) und einen Offline-Installer (Ausrollen auf dem Zielserver).
Schritt A: Der Builder (Internet-PC)
  Der Builder liest die build.yaml, lädt alle Binärdateien, Python-Pakete und GGUF-Modelle herunter, prüft die Integrität und erstellt ein Manifest (manifest.sha256).
  •	Befehl: python offlineai-builder/build.py
Schritt B: Der Installer (Offline-Server)
  Der Administrator kopiert den payload-Ordner, die manifest.sha256 und das Skript install.ps1 per USB-Stick auf den Server (C:\OfflineAI).
  •	Befehl (als Administrator in PowerShell): .\install.ps1
  •	Das Skript validiert die SHA-256-Prüfsummen, installiert die Python-Abhängigkeiten für den RAG-Parser offline, registriert die 5 Ollama-Modelle über definierte Modelfiles und richtet die Windows-Dienste über WinSW ein.
3. IT-Sicherheitskonzept
  Da das System in einer geschützten Umgebung betrieben wird, fokussiert sich das Sicherheitskonzept auf Netzwerksicherheit, Datenisolierung, Zugriffskontrolle und Integritätsschutz.
  3.1. Netzwerksicherheit & Air-Gap-Prinzip
    •	Keine Cloud-Anbindung: Sämtliche Modellinferenzen, Berechnungen und Vektorisierungen finden zu 100% lokal auf dem Server statt. Es werden keine Daten an externe APIs (OpenAI, Anthropic etc.) übertragen.
    •	Firewall-Kapselung: Der Ollama-Dienst lauscht standardmäßig nur lokal (127.0.0.1:11434), um direkten Zugriff von außen zu unterbinden. Nur das Open-WebUI-Frontend ist für autorisierte Clients im internen Firmennetzwerk erreichbar.
  3.2. Identitäts- und Zugriffsmanagement (IAM)
    •	Active Directory (LDAP): Die Benutzeranmeldung an der Web-Oberfläche ist an das unternehmensinterne Active Directory gekoppelt. Es existieren keine lokalen Hardcoded-Admin-Passwörter im Klartext.
    •	Rollenbasierte Zugriffskontrolle (RBAC): Über Open WebUI können Berechtigungen vergeben werden, welche Nutzer oder Gruppen Zugriff auf bestimmte Modelle (z. B. den DeepSeek-Coder oder die großen 35B-Modelle) haben.
  3.3. Datenschutz & Vertraulichkeit (Data Privacy)
    •	In-Memory & Lokaler Speicher: Chat-Verläufe und hochgeladene Dokumente für die RAG-Suche werden ausschließlich in der lokalen ChromaDB und der lokalen SQLite-Datenbank des Frontends gespeichert.
    •	DSGVO-Konformität: Da keine personenbezogenen Daten das geschlossene System verlassen, eignet sich die Plattform hervorragend für die Verarbeitung sensibler interner Dokumente.
  3.4. Integritätsschutz & Supply-Chain-Sicherheit
    •	Kryptografische Prüfsummen: Jede Komponente (Modelldateien, Binaries, Executables), die über den USB-Stick auf das System gelangt, wird vor der Installation im Installer (install.ps1) via manifest.sha256 verifiziert. Manipulierte oder beschädigte Dateien werden automatisch abgewiesen.
    •	Signed Binaries & WinSW: Die Windows-Dienste werden über deterministische Wrapper gesteuert, was unautorisierte Prozess-Injektionen erschwert.
  3.5. Backup- und Notfallkonzept (Disaster Recovery)
    •	Für die regelmäßige Sicherung der Systemstände (Chat-Historien, Vektordatenbank und Konfigurationen) ist das automatisierte Backup-Skript (backup.ps1) im Projekt hinterlegt, welches inkrementelle Sicherungen auf ein separates Speichermedium ermöglicht.

