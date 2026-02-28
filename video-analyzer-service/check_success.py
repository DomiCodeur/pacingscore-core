from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
print(f"URL: {os.getenv('SUPABASE_URL')}")
print(f"Key length: {len(os.getenv('SUPABASE_KEY', ''))}")

s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
r = s.table('analysis_results').select('id,series_title,success').eq('scan_type', 'dailymotion_enfant').execute()
success = [x for x in r.data if x.get('success')]
print(f'Vidéos réussies: {len(success)}')
print(f'Vidéos échouées: {len(r.data) - len(success)}')

if success:
    print("\nExemples de réussites:")
    for item in success[:3]:
        print(f" - {item['series_title']}")