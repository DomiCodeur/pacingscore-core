$body = Get-Content -Raw "test_request2.json"

Invoke-RestMethod -Uri "http://localhost:5000/analyze" -Method Post -ContentType "application/json" -Body $body