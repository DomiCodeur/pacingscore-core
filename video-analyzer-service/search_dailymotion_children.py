import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def find_children_show_videos_dailymotion(limit_total=100):
    """Recherche massive de dessins animés pour enfants sur Dailymotion"""
    
    search_queries = [
        "dessin animé complet", "petit ours brun", "trotro officiel", 
        "simon le lapin", "peppa pig français", "bluey episode complet",
        "didou dessine moi", "tchoupi officiel", "puffin rock", 
        "masha et l'ours", "petit ours brun compilation", "caillou français"
    ]
    
    unique_videos = {}
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    for query in search_queries:
        if len(unique_videos) >= limit_total:
            break
            
        print(f"Recherche Dailymotion pour: {query}")
        try:
            url = f"https://api.dailymotion.com/videos"
            params = {
                "fields": "id,title,description,duration,url",
                "limit": 50,
                "search": query,
                "explicit": "false",
                "family_filter": "true"
            }
            
            response = requests.get(url, params=params, timeout=20)
            videos = response.json().get("list", [])
            print(f"  Trouvé {len(videos)} vidéos")
            
            for video in videos:
                vid_id = video.get("id")
                # Vérifier si déjà en base pour ne pas saturer la queue inutilement
                res = supabase.table("analysis_results").select("id").eq("video_url", f"https://www.dailymotion.com/video/{vid_id}").execute()
                
                if not res.data:
                    unique_videos[vid_id] = {
                        "video_url": f"https://www.dailymotion.com/video/{vid_id}",
                        "series_title": video.get("title", ""),
                        "scan_type": "dailymotion_enfant"
                    }
                
                if len(unique_videos) >= limit_total:
                    break
        except Exception as e:
            print(f"  Erreur sur '{query}': {e}")
            
    return list(unique_videos.values())

def main():
    videos = find_children_show_videos_dailymotion(100)
    if not videos:
        print("Aucune nouvelle vidéo trouvée.")
        return
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Insertion de {len(videos)} nouvelles vidéos dans la file d'attente...")
    
    for v in videos:
        try:
            supabase.table("analysis_results").insert(v).execute()
        except:
            print(f"Échec insertion: {v.get('series_title')}")
        
    print("Insertion terminée. Prêt pour l'analyse !")

if __name__ == "__main__":
    main()
