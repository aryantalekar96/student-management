@echo off
title Jenkins Server (Port 8080)
echo =========================================================
echo   Starting Jenkins CI/CD Server on http://localhost:8080
echo   User: admin
echo   Pass: admin123
echo =========================================================
java -jar "C:\Users\Admin\.gemini\antigravity-ide\scratch\tools\jenkins.war" --httpPort=8080
pause
