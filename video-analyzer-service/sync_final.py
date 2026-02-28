from supabase_manager import supabase_manager
import json
res = supabase_manager.client.table(" analysis_results\).select(\*\).eq(\success\, True).execute()
for r in res.data:
 title = r.get(\series_title\)
 score = r.get(\pacing_score\, 0)
 payload = {
 \title\: title,
 \pacing_score\: score,
 \age_rating\: \0-6\,
 \tmdb_data\: {\source\: \dailymotion\, \id\: r.get(\video_key\)}
 }
 try:
 supabase_manager.client.table(\video_analyses\).upsert(payload, on_conflict=\title\).execute()
 print(\SYNC OK: \ + title)
 except Exception as e:
 print(\SYNC ERR: \ + title + " : \ + str(e))
