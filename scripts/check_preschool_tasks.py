#!/usr/bin/env python3
import os, requests, json
SUPABASE_URL = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjEwMjY0OSwiZXhwIjoyMDg3Njc4NjQ5fQ.sZ-Chd1T7o-iUy9Swchj2RtM5HQLPNv_dKjOvdxlfNw"
headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}
ids = ["502","34921","125760","114718","225261"]
for tid in ids:
    url = f"{SUPABASE_URL}/rest/v1/analysis_tasks?tmdb_id=eq.{tid}&select=*"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            print(f"TMDB {tid}: {json.dumps(data[0], ensure_ascii=False)}")
        else:
            print(f"TMDB {tid}: pas de tâche")
    else:
        print(f"TMDB {tid}: erreur {r.status_code}")
