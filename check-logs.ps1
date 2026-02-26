# Script pour récupérer les logs du terminal
Write-Host "=== Logs du serveur Spring Boot ===" -ForegroundColor Cyan
Write-Host ""

# Chercher les fenêtres de commandes
$cmdProcesses = Get-Process -Name cmd -ErrorAction SilentlyContinue

foreach ($process in $cmdProcesses) {
    Write-Host "Fenêtre ID: $($process.Id)" -ForegroundColor Yellow
    Write-Host "Titre: $($process.MainWindowTitle)" -ForegroundColor Gray
    Write-Host ""
}

# Vérifier si le serveur est en cours
Write-Host "=== Vérification du serveur ===" -ForegroundColor Cyan
$portTest = Test-NetConnection -ComputerName localhost -Port 8080 -InformationLevel Quiet

if ($portTest) {
    Write-Host "✅ Serveur Spring Boot démarré sur http://localhost:8080" -ForegroundColor Green
} else {
    Write-Host "❌ Serveur non démarré sur le port 8080" -ForegroundColor Red
}

# Vérifier les processus Java
Write-Host ""
Write-Host "=== Processus Java ===" -ForegroundColor Cyan
java -version 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }

# Vérifier les logs
Write-Host ""
Write-Host "=== Fichiers de log ===" -ForegroundColor Cyan
$logs = Get-ChildItem -Path "C:\Users\mathi\Documents\Github\pacingscore-clean" -Filter "*.log" -ErrorAction SilentlyContinue

if ($logs) {
    foreach ($log in $logs) {
        Write-Host "  $($log.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "  Aucun fichier log trouvé" -ForegroundColor Yellow
}