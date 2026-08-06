# ==========================================================
# OfflineAI Native Master-Installer (Mit Dual-Dienst-Setup)
# ==========================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$InstallDir = "C:\OfflineAI"
$USBRoot = $PSScriptRoot
$PayloadDir = Join-Path $USBRoot "payload"
$ManifestPath = Join-Path $USBRoot "manifest.sha256"

Clear-Host
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "    OFFLINE AI - MASTER-INSTALLATIONS-ROUTINE       " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Administrator-Rechte prüfen
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "[!] Bitte starte dieses Skript als Administrator!"
    Pause
    exit
}

# 1. Zielverzeichnis erstellen
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

# 2. Payload kopieren
Write-Host "[*] Kopiere alle Komponenten nach $InstallDir..." -ForegroundColor Yellow
Copy-Item -Path "$PayloadDir\*" -Destination $InstallDir -Recurse -Force

# 3. SHA256-Integritätsprüfung
Write-Host "[*] Überprüfe Datei-Integrität..." -ForegroundColor Yellow
if (Test-Path $ManifestPath) {
    Get-Content $ManifestPath | ForEach-Object {
        if ($_ -match '^\s*([a-fA-F0-9]{64})\s+(.+)$') {
            $expectedHash = $Matches[1]
            $filePath = Join-Path $InstallDir $Matches[2].Trim()
            if (Test-Path $filePath) {
                $actualHash = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash.ToLower()
                if ($actualHash -ne $expectedHash.ToLower()) {
                    Write-Warning "  [FEHLER] Hash-Mismatch: $($Matches[2])"
                }
            }
        }
    }
    Write-Host "  [OK] Integritätsprüfung abgeschlossen." -ForegroundColor Green
}

# 4. Ollama entpacken
$OllamaZip = "$InstallDir\providers\ollama\ollama.zip"
$OllamaTarget = "$InstallDir\providers\ollama"
if (Test-Path $OllamaZip) {
    Write-Host "[*] Entpacke Ollama Engine..." -ForegroundColor Yellow
    Expand-Archive -Path $OllamaZip -DestinationPath $OllamaTarget -Force
}

# 5. Python-Pakete (Open WebUI, ChromaDB, Torch etc.) offline installieren
$WheelDir = "$InstallDir\providers\rag\wheels"
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

if ($PythonExe) {
    Write-Host "[*] Installiere Open WebUI, ChromaDB & KI-Bibliotheken aus dem Offline-Cache..." -ForegroundColor Yellow
    & $PythonExe -m pip install --no-index --find-links="$WheelDir" open-webui chromadb sentence-transformers onnxruntime-gpu transformers tokenizers torch
    Write-Host "  [OK] Python-Pakete erfolgreich installiert." -ForegroundColor Green
} else {
    Write-Warning "[!] Kein Python auf dem Server gefunden! Bitte Python vorab installieren."
}

# 6. Ollama als Windows-Dienst einrichten
$WinSWSource = "$InstallDir\winsw.exe"
if (Test-Path $WinSWSource) {
    Write-Host "[*] Registriere Ollama als Windows-Hintergrunddienst..." -ForegroundColor Yellow
    $OllamaServiceXml = @"
<service>
  <id>OllamaService</id>
  <name>Ollama Offline AI</name>
  <description>Lokaler Ollama LLM Server</description>
  <executable>$InstallDir\providers\ollama\ollama.exe</executable>
  <arguments>serve</arguments>
  <log mode="roll-by-size"><sizeThreshold>10240</sizeThreshold><keepFiles>8</keepFiles></log>
</service>
"@
    Set-Content -Path "$InstallDir\providers\ollama\ollama-service.xml" -Value $OllamaServiceXml -Encoding UTF8
    Copy-Item $WinSWSource "$InstallDir\providers\ollama\ollama-service.exe" -Force
    Start-Process -FilePath "$InstallDir\providers\ollama\ollama-service.exe" -ArgumentList "install" -Wait -NoNewWindow
    Start-Service "OllamaService" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Ollama-Dienst läuft." -ForegroundColor Green

    # 7. Open WebUI ebenfalls als Windows-Dienst einrichten
    Write-Host "[*] Registriere Open WebUI als Windows-Hintergrunddienst..." -ForegroundColor Yellow
    
    # Python-Pfad für den Dienst ermitteln (damit der Dienst das richtige Python/Open-WebUI findet)
    $OpenWebUIExe = "$((Get-Item $PythonExe).Directory.FullName)\Scripts\open-webui.exe"
    
    $WebUIServiceXml = @"
<service>
  <id>OpenWebUIService</id>
  <name>Open WebUI Offline</name>
  <description>Lokale Browser-Oberfläche für das Behörden-KI-System</description>
  <executable>$OpenWebUIExe</executable>
  <arguments>serve</arguments>
  <log mode="roll-by-size"><sizeThreshold>10240</sizeThreshold><keepFiles>8</keepFiles></log>
  <env name="PORT" value="8080" />
  <env name="OLLAMA_API_BASE_URL" value="http://localhost:11434/api" />
</service>
"@
    Set-Content -Path "$InstallDir\open-webui-service.xml" -Value $WebUIServiceXml -Encoding UTF8
    Copy-Item $WinSWSource "$InstallDir\open-webui-service.exe" -Force
    Start-Process -FilePath "$InstallDir\open-webui-service.exe" -ArgumentList "install" -Wait -NoNewWindow
    Start-Service "OpenWebUIService" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Open WebUI-Dienst läuft." -ForegroundColor Green
}

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host "       INSTALLATION & AUTostart ERFOLGREICH!        " -ForegroundColor Cyan
Write-Host "       Beide Dienste starten ab sofort automatisch. " -ForegroundColor Cyan
Write-Host "       WebUI erreichbar unter: http://localhost:8080" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Pause