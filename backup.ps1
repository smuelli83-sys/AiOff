# ==========================================
# C:\OfflineAI\backup.ps1 (Angepasst an native Architektur)
# ==========================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$InstallDir = "C:\OfflineAI"
$BackupDir = Join-Path $InstallDir "backups"
$LogDir = Join-Path $InstallDir "logs"
$LogFile = Join-Path $LogDir "offlineai_audit.log"

# Log-Verzeichnis sicherstellen
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupFileName = "offlineai_backup_$Timestamp.zip"
$TargetZip = Join-Path $BackupDir $BackupFileName

Write-Host "=== OfflineAI Enterprise Backup ===" -ForegroundColor Cyan

# 1. Sicherstellen, dass das Backup-Verzeichnis existiert
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
}

# 2. Zu sichernde Verzeichnisse definieren (Open WebUI Datenbanken & ChromaDB Vektoren)
# Hinweis: Open WebUI speichert SQLite/Konfigurationen standardmäßig im User-Verzeichnis oder im App-Pfad. 
# Wir sichern hier den Konfigurationsordner sowie relevante lokale Daten.
$SourcesToBackup = @(
    Join-Path $InstallDir "config",
    Join-Path $InstallDir "providers\rag\models"
)

# Temporärer Ordner zum Sammeln
$TempStage = Join-Path $InstallDir "temp_backup_stage"
if (Test-Path $TempStage) { Remove-Item $TempStage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $TempStage | Out-Null

# 3. Relevante Daten in den Temp-Ordner kopieren
foreach ($Source in $SourcesToBackup) {
    if (Test-Path $Source) {
        $DestName = Split-Path $Source -Leaf
        $DestPath = Join-Path $TempStage $DestName
        Write-Host "[*] Kopiere $DestName..."
        Copy-Item -Path $Source -Destination $DestPath -Recurse -Force
    }
}

# 4. ZIP-Archiv erstellen
Write-Host "[*] Erstelle komprimiertes Backup-Archiv..."
Compress-Archive -Path "$TempStage\*" -DestinationPath $TargetZip -CompressionLevel Optimal

# Temp-Ordner aufräumen
Remove-Item $TempStage -Recurse -Force

if (Test-Path $TargetZip) {
    Write-Host "[+] Backup erfolgreich erstellt: $TargetZip" -ForegroundColor Green
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | BackupSystem        | INFO     | Backup erfolgreich erstellt: $BackupFileName"
    Add-Content -Path $LogFile -Value $LogEntry
} else {
    Write-Host "[-] Fehler beim Erstellen des Backups!" -ForegroundColor Red
    exit 1
}

# 5. Retention Policy: Backups älter als 14 Tage automatisch löschen
Write-Host "[*] Bereinige alte Backups (älter als 14 Tage)..."
$RetentionDays = -14
Get-ChildItem -Path $BackupDir -Filter "offlineai_backup_*.zip" | 
    Where-Object { $_.CreationTime -lt (Get-Date).AddDays($RetentionDays) } | 
    ForEach-Object {
        Write-Host "  -> Lösche altes Backup: $_.Name"
        Remove-Item $_.FullName -Force
    }

Write-Host "=== Backup-Prozess abgeschlossen ===" -ForegroundColor Cyan