# Script pour lancer le serveur Spring Boot
# Ce script doit être exécuté dans un terminal PowerShell

# Chemin de Maven
$MavenPath = "C:\Users\mathi\Downloads\Maven\apache-maven-3.9.6\bin"

# Ajouter au PATH
$env:Path = "$MavenPath;" + $env:Path

# Aller dans le dossier du projet
Set-Location "C:\Users\mathi\Documents\Github\pacingscore-clean"

# Vérifier Maven
Write-Host "=== Vérification Maven ===" -ForegroundColor Green
mvn --version

Write-Host ""
Write-Host "=== Démarrage du serveur Spring Boot ===" -ForegroundColor Green
Write-Host "Le serveur sera accessible sur http://localhost:8080" -ForegroundColor Yellow
Write-Host "Pour arrêter: Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur
mvn spring-boot:run