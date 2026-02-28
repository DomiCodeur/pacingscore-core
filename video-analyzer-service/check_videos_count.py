from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
r = s.table('analysis_results').select('*').eq('scan_type', 'dailymotion_enfant').execute()
print(f'Vidéos Dailymotion enregistrées: {len(r.data)}')

# Compter aussi les vidéos en attente d'analyse
pending = s.table('analysis_results').select('*').eq('scan_type', 'dailymotion_enfant').eq('success', False).execute()
print(f'Vidéos en attente: {len(pending.data)}')

# Afficher quelques informations
if len(r.data) > 0:
    print("\nExemples de vidéos:")
    for i, v in enumerate(r.data[:5], 1):
        print(f"{i}. {v['series_title']} - {v['video_url']}")
