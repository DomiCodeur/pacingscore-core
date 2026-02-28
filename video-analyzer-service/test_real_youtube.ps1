# Test API avec une vraie vidéo YouTube
$baseUrl = "http://localhost:5000"

Write-Host "============================================================"
Write-Host "TEST API PacingScore"
Write-Host "============================================================"

# Test 1: Health check
Write-Host ""
Write-Host "1. Test du serveur (health check)..."
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 10
    Write-Host "   Status: OK"
    Write-Host "   Response: $($health.status)"
} catch {
    Write-Host "   ERREUR: $_"
}

# Test 2: Analyse d'une courte vidéo YouTube
Write-Host ""
Write-Host "2. Analyse d'une vidéo YouTube courte..."
$payload = @{
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    max_duration = 60
    analyze_motion = $false
    analyze_flashes = $true
} | ConvertTo-Json

Write-Host "   Envoi de la requête a l'API..."
Write-Host "   (Cela peut prendre 1-2 minutes)..."

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/analyze" `
        -Method Post `
        -ContentType "application/json" `
        -Body $payload `
        -TimeoutSec 300
    
    if ($result.success) {
        Write-Host ""
        Write-Host "   ANALYSE REUSSIE"
        Write-Host "   Durée vidéo: $($result.video_duration)s"
        Write-Host "   Scènes détectées: $($result.num_scenes)"
        Write-Host "   ASL (sec/plan): $($result.average_shot_length)"
        Write-Host "   Score composite: $($result.composite_score)"
        Write-Host "   Évaluation: $($result.composite_evaluation.label)"
        Write-Host "   Description: $($result.composite_evaluation.description)"
        
        if ($result.motion_analysis) {
            Write-Host "   Mouvement: $($result.motion_analysis.motion_intensity)/100 ($($result.motion_analysis.level))"
        }
        
        if ($result.flash_analysis) {
            Write-Host "   Flashs détectés: $($result.flash_analysis.flashes)"
            Write-Host "   Frames noirs: $($result.flash_analysis.black_frames)"
        }
    } else {
        Write-Host "   ERREUR: $($result.error)"
    }
} catch {
    Write-Host "   ERREUR API: $_"
}

# Test 3: Interface web
Write-Host ""
Write-Host "3. Test de l'interface web..."
try {
    $web = Invoke-WebRequest -Uri "$baseUrl/" -Method Get -TimeoutSec 10
    if ($web.Content -match "PacingScore") {
        Write-Host "   Interface web accessible"
        Write-Host "   URL: $baseUrl/"
    }
} catch {
    Write-Host "   Interface web non accessible: $_"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "TEST TERMINÉ"
Write-Host "============================================================"
Write-Host "Ouvrez votre navigateur sur: http://localhost:5000"
Write-Host "Appuyez sur Entrée pour quitter"