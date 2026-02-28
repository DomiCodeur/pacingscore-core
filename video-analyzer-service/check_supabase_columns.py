import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

def check_columns():
    supabase = create_client(url, key)
    
    # Vérifier les colonnes de la table analysis_results
    try:
        # Essayer de faire un SELECT avec les colonnes que nous voulons
        response = supabase.table("analysis_results").select("tmdb_id", "video_key", "series_genres").limit(1).execute()
        print("[OK] Colonnes presentes")
        print(f"Colonnes trouvees: {response.data}")
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        print("\nColonnes manquantes detectees!")
        print("Ajoutez ces colonnes via SQL Editor Supabase:")
        print("""
ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS tmdb_id INTEGER UNIQUE,
ADD COLUMN IF NOT EXISTS video_key TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS scan_type TEXT,
ADD COLUMN IF NOT EXISTS series_year INTEGER,
ADD COLUMN IF NOT EXISTS series_overview TEXT,
ADD COLUMN IF NOT EXISTS series_genres JSONB;
        """)

if __name__ == "__main__":
    check_columns()
