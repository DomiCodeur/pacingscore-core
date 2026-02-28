import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def find_dailymotion_videos_for_children():
    """Recherche des vidéos enfants sur Dailymotion via leur API"""
    
    # Rechercher des dessins animés pour enfants
    # On va utiliser des mots-clés français pour la recherche
    searches = [
        "dessin animé enfant",
        "animation enfant",
        "film enfant",
        "dessin animé jeunesse",
        "video éducative enfants",
        "film famille",
        "cartoon enfants",
        "dessin animé français"
    ]
    
    all_videos = []
    
    for search in searches:
        print(f"Recherche Dailymotion: {search}")
        
        try:
            # API Dailymotion
            url = f"https://api.dailymotion.com/videos"
            params = {
                "fields": "id,title,description,created_time,duration,url,thumbnail_url",
                "sort": "recent",
                "limit": 20,
                "search": search,
                "explicit": "false",
                "family_filter": "true"
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if "list" in data:
                videos = data["list"]
                print(f"  Trouvé {len(videos)} vidéos")
                
                for video in videos:
                    # Filtrer les vidéos qui semblent être pour enfants (durée < 60min)
                    if video.get("duration", 0) < 3600:  # Moins d'une heure
                        # Vérifier si c'est un vrai dessin animé (mots-clés dans le titre)
                        title_lower = video.get("title", "").lower()
                        if any(keyword in title_lower for keyword in ["dessin", "animation", "cartoon", "film", "enfant", "kids", "baby", "toddler"]):
                            all_videos.append({
                                "id": video.get("id"),
                                "title": video.get("title"),
                                "description": video.get("description"),
                                "url": f"https://www.dailymotion.com/video/{video.get('id')}",
                                "created_time": video.get("created_time"),
                                "duration": video.get("duration")
                            })
        except Exception as e:
            print(f"  Erreur: {e}")
            continue
    
    # Dédoublonner par ID
    unique_videos = {}
    for video in all_videos:
        if video["id"] not in unique_videos:
            unique_videos[video["id"]] = video
    
    return list(unique_videos.values())

def check_video_availability(video_url):
    """Vérifie si une vidéo Dailymotion est disponible"""
    try:
        # Tenter de récupérer les informations de la vidéo
        video_id = video_url.split("/")[-1]
        url = f"https://api.dailymotion.com/video/{video_id}"
        params = {"fields": "id,title,duration,available"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data.get("available", False)
    except:
        return False

def save_to_supabase(videos):
    """Sauvegarde les vidéos dans Supabase"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    saved_count = 0
    
    for video in videos:
        # Vérifier si la vidéo est déjà dans la base
        try:
            # Rechercher par titre
            result = supabase.table("analysis_results").select("*").eq("series_title", video["title"]).execute()
            if len(result.data) > 0:
                print(f"  {video['title']} déjà dans Supabase")
                continue
        except Exception as e:
            print(f"  Erreur vérification doublon: {e}")
        
        # Préparer les données
        data = {
            "series_title": video["title"],
            "video_url": video["url"],
            "scan_type": "dailymotion_ouvert",
            "series_overview": video.get("description", ""),
            "series_year": None,
            "series_genres": ["animation", "children"],
            "tmdb_id": None,  # Pas de correspondance TMDB
            "video_key": video["id"],
            "created_at": "now()",
            "success": False,
            "pending": True
        }
        
        try:
            # Insérer dans Supabase (sans analyse vidéo pour l'instant)
            result = supabase.table("analysis_results").insert(data).execute()
            if result.data:
                print(f"  ✅ Vidéo sauvegardée: {video['title']}")
                saved_count += 1
        except Exception as e:
            print(f"  ❌ Erreur Supabase: {e}")
    
    print(f"\n{saved_count} vidéos sauvegardées dans Supabase")

def main():
    print("=== RECHERCHE VIDÉOS ENFANTS SUR DAILYMOTION ===")
    print("L'API Dailymotion ne necessite pas de compte pour la recherche publique.")
    print()
    
    videos = find_dailymotion_videos_for_children()
    
    print(f"\n=== {len(videos)} VIDEOS TROUVEES ===")
    
    for i, video in enumerate(videos[:10], 1):
        title_safe = video['title'].replace('\u0301', '')  # Remove combining acute accent
        print(f"{i}. {title_safe}")
        print(f"   URL: {video['url']}")
        print(f"   Durée: {video.get('duration', 'N/A')}s")
        print()
    
    if len(videos) > 10:
        print(f"... et {len(videos) - 10} autres vidéos")
    
    # Sauvegarder dans Supabase
    if videos:
        print(f"\n=== SAUVEGARDE DANS SUPABASE ===")
        save_to_supabase(videos)
    
    return videos

if __name__ == "__main__":
    main()
