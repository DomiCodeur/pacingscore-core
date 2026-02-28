import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Configuration
load_dotenv('C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env')
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
tmdb_key = os.getenv("TMDB_API_KEY")
supabase: Client = create_client(url, key)

def get_fr_title(tmdb_id):
    try:
        if not tmdb_id: return None, None
        r = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={tmdb_key}&language=fr-FR")
        data = r.json()
        return data.get('name'), data.get('overview')
    except:
        return None, None

def sync():
    print("Démarrage du script Mollo-Sync (Français + Scores)...")
    
    response = supabase.table("video_analyses").select("*").execute()
    shows = response.data
    
    safe_scores = {
        "Babar": 85,
        "Peppa Pig": 75,
        "Caillou": 80,
        "Tchoupi": 90,
        "Simon": 78,
        "Pocoyo": 82,
        "Petit Ours Brun": 95,
        "Bluey": 75,
        "Puffin Rock": 88
    }

    for show in shows:
        show_id = show['id']
        current_title = show.get('title') or show.get('video_path') or ""
        tmdb_data = show.get('tmdb_data')
        tmdb_id = None
        
        # Récupération de l'ID TMDB
        if isinstance(tmdb_data, dict):
            tmdb_id = tmdb_data.get('id')
        
        updates = {}
        
        # 1. Traduction
        if tmdb_id:
            fr_name, fr_desc = get_fr_title(tmdb_id)
            if fr_name:
                updates['title'] = fr_name
                updates['description'] = fr_desc
                print(f"Traduction : {current_title} -> {fr_name}")

        # 2. Score
        for search_key, new_score in safe_scores.items():
            if search_key.lower() in current_title.lower():
                updates['pacing_score'] = new_score
                print(f"Score ajuste pour {current_title}: {new_score}")
        
        if updates:
            supabase.table("video_analyses").update(updates).eq("id", show_id).execute()

    print("Sync terminee !")

if __name__ == "__main__":
    sync()
