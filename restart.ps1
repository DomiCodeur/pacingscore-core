# Nettoyage
Write-Host "🧹 Nettoyage..." -ForegroundColor Green
docker-compose down

# Suppression des conteneurs et volumes
Write-Host "🗑 Suppression des conteneurs et volumes..." -ForegroundColor Yellow
docker system prune -f
docker volume prune -f

# Redémarrage des services
Write-Host "🚀 Redémarrage des services..." -ForegroundColor Cyan
docker-compose up -d

# Attente
Write-Host "⏳ Attente des services..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Population de la base
Write-Host "📥 Population de la base de données..." -ForegroundColor Magenta
Set-Location video-analyzer-service
python populate_clean_v2.py

Write-Host "✨ C'est prêt ! Va sur http://localhost:9000" -ForegroundColor Green