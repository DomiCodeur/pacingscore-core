from supabase_manager import supabase_manager
import json, datetime
res = supabase_manager.client.table(" analysis_results\).select(\*\).eq(\success\, True).execute()
for r in res.data:
 title = r[\series_title\]
 d = {\title\: title, \video_path\: title, \pacing_score\: r[\pacing_score\], \age_rating\: \0-6\, \tmdb_data\: {\source\: \dailymotion\, \id\: r[\video_key\]}}
 try: supabase_manager.client.table(\video_analyses\).upsert(d, on_conflict=\title\).execute(); print(\OK:\+title)
 except: print(\ERR:\+title)
 \video_path\: title,
