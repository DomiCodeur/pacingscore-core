import os
import sys
import json
import time
import io
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Env config
load_dotenv()

# UTF-8 support for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8')

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def debug_tmdb():
    print(f"[*] Test TMDB avec clé: {TMDB_API_KEY[:5]}...")
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={TMDB_API_KEY}"
    try:
        r = requests.get(url)
        print(f"[*] TMDB Status: {r.status_code}")
        if r.status_code == 200:
            count = len(r.json().get('results', []))
            print(f"[*] TMDB a retourné {count} résultats")
        else:
            print(f"[*] TMDB Error: {r.text}")
    except Exception as e:
        print(f"[!] Erreur TMDB: {e}")

def debug_supabase():
    print(f"[*] Test Supabase avec URL: {SUPABASE_URL}...")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Try to list tables implicitly by trying a common meta query or just a select
        print("[*] Client Supabase initialisé")
    except Exception as e:
        print(f"[!] Erreur Supabase: {e}")

if __name__ == "__main__":
    debug_tmdb()
    debug_supabase()
