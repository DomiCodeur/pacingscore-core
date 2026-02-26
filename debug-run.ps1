# Script de debug pour voir les erreurs de compilation
$MavenPath = "C:\Users\mathi\Downloads\Maven\apache-maven-3.9.6\bin"
$env:Path = "$MavenPath;" + $env:Path

Set-Location "C:\Users\mathi\Documents\Github\pacingscore-clean"

Write-Host "=== Compilation du projet ===" -ForegroundColor Yellow
mvn clean compile -e

Write-Host ""
Write-Host "=== Vérification des dépendances ===" -ForegroundColor Yellow
mvn dependency:tree

Write-Host ""
Write-Host "=== Lancement du serveur ===" -ForegroundColor Green
mvn spring-boot:run