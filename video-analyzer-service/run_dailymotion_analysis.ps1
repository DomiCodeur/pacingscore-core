cd "C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service"
.\venv\Scripts\python.exe analyze_dailymotion_videos.py 2>&1 | Tee-Object -FilePath "C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service\dailymotion_analysis.log"
Write-Host "Script terminé. Voir dailymotion_analysis.log pour les logs."