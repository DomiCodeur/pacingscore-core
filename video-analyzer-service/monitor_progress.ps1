$headers = @{ "apikey" = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"; "Authorization" = "Bearer sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t" }
$lastCount = 0
Write-Host "Monitoring progression (toutes les 30s)..." -ForegroundColor Cyan
while ($true) {
    try {
        $count = Invoke-RestMethod "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses?select=count" -Headers $headers -Method Get -ErrorAction Stop
        $current = $count[0].count
        $time = Get-Date -Format "HH:mm:ss"
        $diff = $current - $lastCount
        if ($diff -gt 0) {
            Write-Host "[$time] Vidéos: $current (+$diff)" -ForegroundColor Green
        } else {
            Write-Host "[$time] Vidéos: $current" -ForegroundColor Yellow
        }
        $lastCount = $current
        if ($current -ge 100) {
            Write-Host "🎉 OBJECTIF 100 VIDÉOS ATTEINT !" -ForegroundColor Magenta
            break
        }
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
    }
    Start-Sleep -Seconds 30
}
