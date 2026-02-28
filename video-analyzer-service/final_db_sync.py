from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
s = create_client(os.getenv(" SUPABASE_URL\), os.getenv(\SUPABASE_KEY\))
res = s.table(\analysis_results\).select(\*\).eq(\success\, True).execute()
for r in res.data:
 t = r.get(\series_title\)
 d = {\video_path\: t, \pacing_score\: r.get(\pacing_score\), \metadata\: {\source\: \auto\}}
 try:
 s.table(\video_analyses\).upsert(d, on_conflict=\video_path\).execute()
 print(\OK: \+t)
 except Exception as e: print(\ERR: \+str(e))
