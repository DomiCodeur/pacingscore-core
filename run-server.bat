@echo off
cd /d "C:\Users\mathi\Documents\Github\pacingscore-clean"

set MAVEN_HOME=C:\Users\mathi\Downloads\Maven\apache-maven-3.9.6
set PATH=%MAVEN_HOME%\bin;%PATH%

echo === Compilation du projet ===
mvn clean compile

echo.
echo === Lancement du serveur Spring Boot ===
echo.
echo Le serveur sera accessible sur http://localhost:8080
echo Pour arrêter: Ctrl+C
echo.

mvn spring-boot:run

pause