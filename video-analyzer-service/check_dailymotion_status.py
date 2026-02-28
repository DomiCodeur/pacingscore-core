from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
r = s.table('analysis_results').select('id,series_title,success,pacing_score').eq('scan_type', 'dailymotion_enfant').execute()
success = [x for x in r.data if x.get('success')]
failed = [x for x in r.data if not x.get('success')]
non_analysees = [x for x in r.data if x.get('pacing_score') is None]
print(f'Réussies: {len(success)}')
print(f'Échouées: {len(failed)}')
print(f'Non analysées (pacing_score NULL): {len(non_analysees)}')
print(f'Total Dailymotion: {len(r.data)}')
if success:
    print("\nExemples de réussites:")
    for item in success[:3]:
        print(f" - {item['series_title']} (score: {item.get('pacing_score')})")
if failed:
    print("\nExemples d'échecs:")
    for item in failed[:3]:
        print(f" - {item['series_title']} (ID: {item['id']})")