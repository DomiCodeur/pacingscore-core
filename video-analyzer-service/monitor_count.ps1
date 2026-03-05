$headers = @{ "apikey" = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"; "Authorization" = "Bearer sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t" }
while ($true) {
    try {
        $count = Invoke-RestMethod "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses?select=count" -Headers $headers -Method Get -ErrorAction Stop
        $time = Get-Date -Format "HH:mm:ss"
        "$time - Videos: $($count[0].count)" | Out-File -FilePath "C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service\video_count.txt" -Append
        if ($count[0].count -ge 100) {
            "?? OBJECTIF 100 VIDÉOS ATTEINT !" | Out-File -FilePath "C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service\video_count.txt" -Append
            break
        }
    } catch {
        "Erreur: $_" | Out-File -FilePath "C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service\video_count.txt" -Append
    }
    Start-Sleep -Seconds 60
}
