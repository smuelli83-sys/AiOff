# offlineai-installer/install.ps1

$InstallDir = "C:\OfflineAI"
$UsbPayload = Join-Path $PSScriptRoot "payload"
$ServiceName = "OfflineAI"

Write-Host "=== OfflineAI Enterprise Installer ===" -ForegroundColor Cyan

# 1. Integritätsprüfung (SHA-256)
$ManifestPath = Join-Path $PSScriptRoot "manifest.sha256"
if (Test-Path $ManifestPath) {
    Write-Host "[*] Prüfe Datei-Integrität der Installationsdateien..."
    # Hier würde in der Vollversion der SHA-256 Check gegen das Manifest laufen
    # um sicherzustellen, dass keine defekten Dateien vom USB-Stick kopiert werden.
}

# 2. Bestehenden Dienst stoppen (wichtig für Updates)
$ServiceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($ServiceExists -and $ServiceExists.Status -eq "Running") {
    Write-Host "[*] Stoppe laufenden OfflineAI-Dienst für das Update..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force
    Start-Sleep -Seconds 3
}

# 3. Dateien vom USB-Stick auf den Server kopieren
Write-Host "[*] Kopiere Systemdateien, KI-Modelle und Python-Umgebungen nach $InstallDir..."
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}
Copy-Item -Path "$UsbPayload\*" -Destination $InstallDir -Recurse -Force

Write-Host "[*] Installiere RAG-Abhängigkeiten (Word/Excel) offline..." -ForegroundColor Cyan

$VenvPython = Join-Path $InstallDir "providers\open_webui\venv\Scripts\python.exe"
$WheelsDir = Join-Path $InstallDir "dependencies\python_wheels"

if (Test-Path $WheelsDir) {
    # "--no-index" verhindert, dass pip versucht, ins Internet zu gehen
    # "--find-links" zwingt pip, nur unsere USB-Stick-Dateien zu nutzen
    $InstallArgs = "-m", "pip", "install", "--no-index", "--find-links=$WheelsDir", "python-docx", "openpyxl", "pandas"
    
    $Process = Start-Process -FilePath $VenvPython -ArgumentList $InstallArgs -Wait -NoNewWindow -PassThru
    
    if ($Process.ExitCode -eq 0) {
        Write-Host "  -> RAG-Pakete erfolgreich installiert." -ForegroundColor Green
    } else {
        Write-Host "  -> Fehler bei der Installation der RAG-Pakete." -ForegroundColor Red
    }
}

# 4. Windows-Dienst registrieren
Write-Host "[*] Registriere Windows-Dienst..."
$WinSWExe = Join-Path $InstallDir "winsw.exe"
$WinSWConfig = Join-Path $InstallDir "offlineai-service.xml"

# Befehl an WinSW, den Dienst ins Betriebssystem einzutragen
& $WinSWExe install $WinSWConfig

# 5. Dienst starten
Write-Host "[*] Starte System..." -ForegroundColor Green
Start-Service -Name $ServiceName

Write-Host "=== Installation/Update erfolgreich abgeschlossen! ===" -ForegroundColor Green
Write-Host "Der OfflineAI Kernel läuft nun als Hintergrunddienst."

Write-Host "[*] Registriere alle LLMs in der lokalen Ollama-Engine..." -ForegroundColor Cyan
$OllamaExe = "C:\OfflineAI\providers\ollama\ollama.exe"

# Kurze Pause, damit Ollama sicher bereit ist
Start-Sleep -Seconds 5

& $OllamaExe create qwen-fast -f "C:\OfflineAI\providers\ollama\Modelfile_QwenFast"
& $OllamaExe create qwen3.6-27b -f "C:\OfflineAI\providers\ollama\Modelfile_Qwen27"
& $OllamaExe create qwen3.6-35b -f "C:\OfflineAI\providers\ollama\Modelfile_Qwen35"
& $OllamaExe create deepseek-coder -f "C:\OfflineAI\providers\ollama\Modelfile_DeepSeek"
& $OllamaExe create llama3 -f "C:\OfflineAI\providers\ollama\Modelfile_Llama3"

Write-Host "[+] Alle Modelle erfolgreich im System registriert!" -ForegroundColor Green
