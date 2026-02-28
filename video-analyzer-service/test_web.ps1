# Test de l'interface web et API
Write-Host "============================================================"
Write-Host "TEST INTERFACE WEB PacingScore"
Write-Host "============================================================"

# Test 1: Interface web
Write-Host ""
Write-Host "1. Test de l'interface web..."
try {
    $web = Invoke-WebRequest -Uri "http://localhost:5000/" -Method Get -TimeoutSec 10
    if ($web.Content -match "PacingScore") {
        Write-Host "   [SUCCES] Interface web accessible"
        Write-Host "   URL: http://localhost:5000"
        
        # Sauvegarder le HTML pour vérification
        $web.Content | Out-File -FilePath "temp_interface.html" -Encoding utf8
        Write-Host "   HTML sauvegardé dans: temp_interface.html"
    } else {
        Write-Host "   [ERREUR] Interface web non détectée"
    }
} catch {
    Write-Host "   [ERREUR] Impossible d'accéder à l'interface: $_"
}

# Test 2: Health check
Write-Host ""
Write-Host "2. Test de l'API (health check)..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 10
    Write-Host "   [SUCCES] API fonctionne"
    Write-Host "   Status: $($health.status)"
    Write-Host "   Service: $($health.service)"
} catch {
    Write-Host "   [ERREUR] API non accessible: $_"
}

# Test 3: Analyse simple avec une vidéo courte
Write-Host ""
Write-Host "3. Test d'analyse vidéo YouTube..."
Write-Host "   Note: L'analyse peut prendre 1-2 minutes..."
Write-Host "   Vidéo: Rick Astley - Never Gonna Give You Up"

$payload = @{
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    max_duration = 60
    analyze_motion = $false
    analyze_flashes = $true
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/analyze" `
        -Method Post `
        -ContentType "application/json" `
        -Body $payload `
        -TimeoutSec 300
    
    if ($result.success) {
        Write-Host "   [SUCCES] Analyse terminée!"
        Write-Host ""
        Write-Host "   RESULTATS:"
        Write-Host "   ==========="
        Write-Host "   Durée vidéo: $($result.video_duration)s"
        Write-Host "   Scènes détectées: $($result.num_scenes)"
        Write-Host "   ASL: $($result.average_shot_length)s/plan"
        Write-Host "   Score composite: $($result.composite_score)"
        Write-Host "   Évaluation: $($result.composite_evaluation.label)"
        Write-Host "   Description: $($result.composite_evaluation.description)"
        
        if ($result.motion_analysis) {
            Write-Host "   Mouvement: $($result.motion_analysis.motion_intensity)/100 ($($result.motion_analysis.level))"
        }
        
        if ($result.flash_analysis) {
            Write-Host "   Flashs: $($result.flash_analysis.flashes) détectés"
        }
        
        # Sauvegarder le résultat
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "temp_result.json" -Encoding utf8
        Write-Host ""
        Write-Host "   Résultat sauvegardé dans: temp_result.json"
        
    } else {
        Write-Host "   [ERREUR] Analyse échouée: $($result.error)"
    }
} catch {
    Write-Host "   [ERREUR] Erreur API: $_"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "TEST TERMINÉ"
Write-Host "============================================================"
Write-Host ""
Write-Host "Pour accéder à l'interface web:"
Write-Host "   Ouvrez http://localhost:5000 dans votre navigateur"
Write-Host ""
Write-Host "Appuyez sur Entrée pour quitter..."
Read-Host