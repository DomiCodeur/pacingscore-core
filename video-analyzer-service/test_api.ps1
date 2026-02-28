$body = @{
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    max_duration = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/analyze" -Method Post -ContentType "application/json" -Body $body