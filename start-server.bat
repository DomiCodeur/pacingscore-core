@echo off
cd /d "C:\Users\mathi\Documents\Github\pacingscore-clean"

set MAVEN_HOME=C:\Users\mathi\Downloads\Maven\apache-maven-3.9.6
set PATH=%MAVEN_HOME%\bin;%PATH%

echo.
echo ========================================
echo   Démarrage du Serveur PacingScore
echo ========================================
echo.
echo Le serveur sera accessible sur:
echo   http://localhost:8080
echo.
echo Pour arrêter le serveur:
echo   Appuyez sur Ctrl+C
echo.
echo Démarrage en cours...
echo.

mvn spring-boot:run

pause