import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def find_animation_movies_dailymotion(limit_total=50):
    """Recherche massive de FILMS d'animation longs (>45 min)"""
    
    search_queries = [
        "film d'animation complet en français", "film complet disney fr", 
        "miyazaki film complet fr", "gforce film complet", "film animation bébé complet",
        "film barbie français complet", "film pixar complet en français"
    ]
    
    unique_movies = {}
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    for query in search_queries:
        if len(unique_movies) >= limit_total:
            break
            
        print(f"Recherche Dailymotion FILMS pour: {query}")
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
                duration = video.get("duration", 0)
                
                # On ne garde que les vidéos LONGUES (> 45 min) pour que ce soit des films
                if duration > 2700: 
                    # Vérifier si déjà en base pour ne pas saturer la queue inutilement
                    res = supabase.table("analysis_results").select("id").eq("video_url", f"https://www.dailymotion.com/video/{vid_id}").execute()
                    
                    if not res.data:
                        unique_movies[vid_id] = {
                            "video_url": f"https://www.dailymotion.com/video/{vid_id}",
                            "series_title": video.get("title", ""),
                            "scan_type": "film_animation", # Nouveau tag
                            "metadata": {"duration": duration, "style": "Film"}
                        }
                
                if len(unique_movies) >= limit_total:
                    break
        except Exception as e:
            print(f"  Erreur sur '{query}': {e}")
            
    return list(unique_movies.values())

def main():
    movies = find_animation_movies_dailymotion(50)
    if not movies:
        print("Aucun nouveau film trouvé.")
        return
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Insertion de {len(movies)} nouveaux FILMS dans la file d'attente...")
    
    for m in movies:
        try:
            # On retire metadata qui buggait tout à l'heure
            m_clean = {
                "video_url": m["video_url"],
                "series_title": m["series_title"],
                "scan_type": m["scan_type"]
            }
            supabase.table("analysis_results").insert(m_clean).execute()
        except:
            print(f"Échec insertion film: {m.get('series_title')}")
        
    print("Insertion terminée. Prêt pour l'analyse des films !")

if __name__ == "__main__":
    main()
