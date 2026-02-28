from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
print("URL:", os.getenv('SUPABASE_URL'))
print("Key length:", len(os.getenv('SUPABASE_KEY', '')))

try:
    s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    # Essayer de récupérer un nombre limité de lignes
    r = s.table('video_analyses').select('*').limit(5).execute()
    print(f'Found {len(r.data)} rows in video_analyses')
    for row in r.data:
        print(row)
except Exception as e:
    print(f"Error: {e}")
    # Essayer de vérifier si la table existe en comptant
    try:
        count = s.table('video_analyses').select('*').execute()
        print(f"Count: {len(count.data)}")
    except Exception as e2:
        print(f"Error counting: {e2}")