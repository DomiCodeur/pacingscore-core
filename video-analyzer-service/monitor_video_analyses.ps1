$headers = @{ "apikey" = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"; "Authorization" = "Bearer sb_publishable 2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t" }
$last = 0
Write-Host "`n=== Surveillance video_analyses (toutes les 30s) ==="
while ($true) {
    try {
        $count = Invoke-RestMethod "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses?select=count" -Headers $headers -Method Get -TimeoutSec 5
        $current = $count[0].count
        $delta = $current - $last
        $time = Get-Date -Format "HH:mm:ss"
        if ($delta -gt 0) {
            Write-Host "[$time] +$delta => Total: $current" -ForegroundColor Green
        } else {
            Write-Host "[$time] Total: $current" -ForegroundColor Gray
        }
        $last = $current
        if ($current -ge 100) {
            Write-Host "`n🎉🎉🎉 100 VIDÉOS ATTEINTES ! 🎉🎉🎉" -ForegroundColor Magenta
            break
        }
    } catch {
        Write-Host "[$($(Get-Date -Format HH:mm:ss))] Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep -Seconds 30
}
