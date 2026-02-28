
import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Configuration
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
tmdb_key = os.getenv("TMDB_API_KEY")
supabase: Client = create_client(url, key)

# Liste noire des mots-clés non appropriés pour enfants
NO_GO_KEYWORDS = [
    "house of the dragon", "last of us", "shogun", "knight of the seven kingdoms",
    "the boys", "stranger things", "game of thrones", "demon hunter", "skibidi toilet"
]

def get_fr_age_rating(tmdb_id):
    try:
        if not tmdb_id: return "0+"
        # Content Ratings
        url_age = f"https://api.themoviedb.org/3/tv/{tmdb_id}/content_ratings?api_key={tmdb_key}"
        r = requests.get(url_age)
        data = r.json()
        
        # Priorité au rating français (FR)
        for res in data.get('results', []):
            if res.get('iso_3166_1') == 'FR':
                rating = res.get('rating')
                if rating == 'U': return '0+'
                return f"{rating}+"
        
        # Fallback US
        for res in data.get('results', []):
            if res.get('iso_3166_1') == 'US':
                rating = res.get('rating')
                if 'G' in rating: return '0+'
                if '7' in rating: return '6+'
                if '14' in rating: return '12+'
                if 'MA' in rating: return '16+'
        
        return "0+"
    except:
        return "0+"

def cleanup_and_ages():
    print("--- NETTOYAGE ET AJOUT DES AGES REELS ---")
    
    response = supabase.table("video_analyses").select("*").execute()
    shows = response.data
    
    deleted_count = 0
    updated_count = 0

    for show in shows:
        show_id = show['id']
        title = (show.get('title') or show.get('video_path') or "").lower()
        
        # 1. Suppression du contenu inapproprié
        should_delete = False
        for keyword in NO_GO_KEYWORDS:
            if keyword in title:
                should_delete = True
                break
        
        if should_delete:
            supabase.table("video_analyses").delete().eq("id", show_id).execute()
            print(f"DEL: {title}")
            deleted_count += 1
            continue

        # 2. Mise à jour de l'âge réel via TMDB
        tmdb_data = show.get('tmdb_data')
        tmdb_id = None
        if isinstance(tmdb_data, dict):
            tmdb_id = tmdb_data.get('id')
        
        if tmdb_id:
            real_age = get_fr_age_rating(tmdb_id)
            supabase.table("video_analyses").update({"age_rating": real_age}).eq("id", show_id).execute()
            print(f"AGE: {title} -> {real_age}")
            updated_count += 1

    print(f"\nTermine ! {deleted_count} supprimes, {updated_count} ages mis a jour.")

if __name__ == "__main__":
    cleanup_and_ages()
