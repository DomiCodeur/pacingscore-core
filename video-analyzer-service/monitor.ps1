# Monitoring du nombre de vidéos
$headers = @{ "apikey" = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"; "Authorization" = "Bearer sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t" }
Write-Host "Monitoring video_analyses..." -ForegroundColor Cyan
Write-Host "Ctrl+C pour arrêter" -ForegroundColor Yellow
while ($true) {
    try {
        $count = Invoke-RestMethod "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses?select=count" -Headers $headers -Method Get -ErrorAction Stop
        $time = Get-Date -Format "HH:mm:ss"
        Write-Host "[$time] Vidéos: $($count[0].count)" -ForegroundColor Green
        if ($count[0].count -ge 100) {
            Write-Host "?? Objectif 100 vidéos atteint !" -ForegroundColor Magenta
            break
        }
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
    }
    Start-Sleep -Seconds 30
}
