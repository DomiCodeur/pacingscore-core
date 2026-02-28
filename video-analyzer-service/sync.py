from supabase_manager import supabase_manager
res = supabase_manager.client.table(" analysis_results\).select(\* \).eq(\success\, True).execute()
for r in res.data:
 d = {\title\: r[\series_title\], \video_path\: r[\series_title\], \pacing_score\: r[\pacing_score\], \age_rating\: \0-6\, \tmdb_data\: {\source\: \dailymotion\}}
 try: supabase_manager.client.table(\video_analyses\).upsert(d, on_conflict=\title\).execute(); print(\OK:\+r[\series_title\])
 except: print(\ERR:\+r[\series_title\])
