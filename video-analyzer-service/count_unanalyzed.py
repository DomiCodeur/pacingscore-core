from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Compter les vidéos non analysées
r = s.table('analysis_results').select('id,series_title,pacing_score').eq('scan_type', 'dailymotion_enfant').execute()
unanalyzed = [x for x in r.data if x.get('pacing_score') is None]
print(f"Vidéos non analysées (pacing_score NULL): {len(unanalyzed)}")
if unanalyzed:
    print("Exemples:")
    for item in unanalyzed[:5]:
        print(f" - {item['series_title']} (ID: {item['id']})")