import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def find_children_show_videos_dailymotion():
    """Recherche des dessins animés pour enfants <6 ans sur Dailymotion"""
    
    # Liste spécifique de séries pour enfants <6 ans
    # Selon la liste utilisée dans l'application Angular
    children_shows = [
        "Peppa Pig",
        "Babar",
        "Simon le petit fantôme",
        "Masha et l'Ours",
        "Ben & Holly",
        "Paw Patrol",
        "Bluey",
        "Les Pyjamasques",
        "Pocoyo",
        "Caillou",
        "Barbie Life in the Dreamhouse",
        "Blippi",
        "Pinkfong",
        "Baby Einstein",
        "Talking Tom",
        "Mickey Mouse",
        "Minions"
    ]
    
    all_videos = []
    
    for show in children_shows:
        print(f"Recherche Dailymotion: {show}")
        
        try:
            # API Dailymotion avec recherche par nom exact
            url = f"https://api.dailymotion.com/videos"
            params = {
                "fields": "id,title,description,created_time,duration,url,thumbnail_url,owner",
                "sort": "recent",
                "limit": 15,
                "search": show,
                "explicit": "false",
                "family_filter": "true"
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if "list" in data:
                videos = data["list"]
                print(f"  Trouvé {len(videos)} vidéos")
                
                for video in videos:
                    title = video.get("title", "")
                    title_lower = title.lower()
                    show_lower = show.lower()
                    
                    # Vérifier que le titre contient le nom de la série
                    if show_lower in title_lower:
                        # Filtrer par durée (idéal pour enfants <6 ans)
                        duration = video.get("duration", 0)
                        if 30 < duration < 1800:  # Entre 30 secondes et 30 minutes
                        
                            all_videos.append({
                                "id": video.get("id"),
                                "title": title,
                                "description": video.get("description", ""),
                                "url": f"https://www.dailymotion.com/video/{video.get('id')}",
                                "created_time": video.get("created_time"),
                                "duration": duration,
                                "show": show,
                                "owner": video.get("owner")
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

def save_to_supabase(videos):
    """Sauvegarde les vidéos dans Supabase avec métadonnées enrichies"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    saved_count = 0
    
    for video in videos:
        # Vérifier si la vidéo est déjà dans la base
        try:
            result = supabase.table("analysis_results").select("*").eq("video_key", video["id"]).execute()
            if len(result.data) > 0:
                print(f"  Video deja dans Supabase: {video['title'][:50]}...")
                continue
        except Exception as e:
            print(f"  Erreur verification doublon: {e}")
            continue
        
        # Préparer les données pour Supabase (sans la colonne 'pending')
        data = {
            "series_title": video["show"],
            "video_url": video["url"],
            "scan_type": "dailymotion_enfant",
            "series_overview": video["description"][:500] if video["description"] else "",
            "series_year": None,
            "series_genres": ["animation", "children", "education"],
            "tmdb_id": None,
            "video_key": video["id"],
            "success": False,
            "evaluation_label": "A analyser",
            "evaluation_description": "Video a analyser pour flashs lumineux",
            "evaluation_color": "orange"
        }
        
        try:
            # Insérer dans Supabase
            result = supabase.table("analysis_results").insert(data).execute()
            if result.data:
                print(f"  OK {video['show']}: {video['title'][:40]}...")
                saved_count += 1
        except Exception as e:
            print(f"  ERROR Supabase: {e}")
    
    print(f"\n{saved_count} videos sauvegardees dans Supabase")

def main():
    print("=== RECHERCHE DESSINS ANIMES POUR ENFANTS <6 ANS SUR DAILYMOTION ===")
    print("Series recherchees: Peppa Pig, Babar, Simon, Masha, etc.")
    print()
    
    videos = find_children_show_videos_dailymotion()
    
    print(f"\n=== {len(videos)} VIDEOS DE DESSINS ANIMES TROUVES ===")
    
    for i, video in enumerate(videos[:15], 1):
        # Remove unicode chars that cause encoding issues
        title_safe = ''.join(c for c in video['title'] if ord(c) < 128)
        show_safe = ''.join(c for c in video['show'] if ord(c) < 128)
        print(f"{i}. [{show_safe}] {title_safe}")
        print(f"   URL: {video['url']}")
        print(f"   Duree: {video['duration']}s")
        print()
    
    if len(videos) > 15:
        print(f"... et {len(videos) - 15} autres videos")
    
    # Sauvegarder dans Supabase
    if videos:
        print(f"\n=== SAUVEGARDE DANS SUPABASE ===")
        save_to_supabase(videos)
    
    return videos

if __name__ == "__main__":
    main()
