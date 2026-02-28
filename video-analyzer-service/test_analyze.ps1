# Test d'analyse vidéo
Write-Host "Test d'analyse vidéo YouTube"
Write-Host "============================="

# Données de test
$payload = @{
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    max_duration = 60
    analyze_motion = $false
    analyze_flashes = $true
} | ConvertTo-Json

Write-Host "Envoi de la requête d'analyse..."
Write-Host "Cela peut prendre 1-2 minutes..."

try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/analyze" `
        -Method Post `
        -ContentType "application/json" `
        -Body $payload `
        -TimeoutSec 300
    
    Write-Host "Requête envoyée!"
    Write-Host "Resultat:"
    Write-Host ($result | ConvertTo-Json)
    
} catch {
    Write-Host "ERREUR: $_"
}