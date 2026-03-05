import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def populate_clean_queue():
    """Remplissage sélectif : Max 3 vidéos par série culte + Films"""
    
    series_to_search = [
        "Bluey", "Babar", "Peppa Pig", "Petit Ours Brun", "Trotro", 
        "Tchoupi", "Simon le lapin", "Masha et l'Ours", "Puffin Rock", "Pocoyo"
    ]
    
    unique_videos = {}
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Ajouter les Séries (Limité à 3 par série)
    for series in series_to_search:
        print(f"Injection Série: {series}")
        try:
            url = "https://api.dailymotion.com/videos"
            params = {"fields": "id,title,url", "limit": 3, "search": series, "family_filter": "true"}
            videos = requests.get(url, params=params).json().get("list", [])
            for v in videos:
                vid_id = v.get("id")
                unique_videos[vid_id] = {"video_url": f"https://www.dailymotion.com/video/{vid_id}", "series_title": f"{series} - {v.get('title')}", "scan_type": "serie_enfant"}
        except: pass

    # 2. Ajouter des Films (Limité à 20 films uniques)
    print("Injection Films d'animation...")
    try:
        url = "https://api.dailymotion.com/videos"
        params = {"fields": "id,title,url", "limit": 20, "search": "film animation complet français", "family_filter": "true"}
        videos = requests.get(url, params=params).json().get("list", [])
        for v in videos:
            vid_id = v.get("id")
            if vid_id not in unique_videos:
                unique_videos[vid_id] = {"video_url": f"https://www.dailymotion.com/video/{vid_id}", "series_title": v.get("title"), "scan_type": "film_animation"}
    except: pass

    # 3. Insertion Queue
    for v in unique_videos.values():
        supabase.table("analysis_results").insert(v).execute()
    print(f"Queue prête : {len(unique_videos)} vidéos sélectionnées (Finis les doublons sauvages !)")

if __name__ == "__main__":
    populate_clean_queue()
