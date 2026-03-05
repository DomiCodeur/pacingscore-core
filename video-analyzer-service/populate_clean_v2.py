import os
import requests
from dotenv import load_dotenv
from supabase import create_client
from time import sleep

load_dotenv()
SUPABASE_URL = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDkxMDUxNzIsImV4cCI6MjAyNDY4MTE3Mn0.CC7yB7r3mxHsl-3ocHBBXxutGOLIf6uFDpnR9CzHNlA"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_tmdb_kids_content():
    """Récupère les séries et films d'animation pour enfants via TMDB"""
    series = []
    movies = []
    
    # 1. Séries d'animation pour enfants
    url = "https://api.themoviedb.org/3/discover/tv"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": "16,10762",  # Animation + Kids
        "language": "fr-FR",
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    for i in range(1, 4):  # 3 pages = ~60 séries
        params["page"] = i
        try:
            response = requests.get(url, params=params).json()
            for show in response.get("results", []):
                if show.get("original_language") in ["fr", "en"]:  # On se limite au français et anglais
                    series.append({
                        "title": show.get("name"),
                        "tmdb_id": show.get("id"),
                        "poster_path": show.get("poster_path")
                    })
        except: pass
        sleep(0.5)  # Respecter les limites de l'API
    
    # 2. Films d'animation pour enfants
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": "16",  # Animation
        "certification_country": "FR",
        "certification.lte": "U",  # Pour tous publics
        "language": "fr-FR",
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    for i in range(1, 4):  # 3 pages = ~60 films
        params["page"] = i
        try:
            response = requests.get(url, params=params).json()
            for movie in response.get("results", []):
                if movie.get("original_language") in ["fr", "en"]:
                    movies.append({
                        "title": movie.get("title"),
                        "tmdb_id": movie.get("id"),
                        "poster_path": movie.get("poster_path")
                    })
        except: pass
        sleep(0.5)
    
    return series, movies

def search_dailymotion(query, limit=3, scan_type="serie_enfant"):
    """Recherche intelligente sur Dailymotion avec filtrage des titres"""
    results = []
    
    try:
        url = "https://api.dailymotion.com/videos"
        params = {
            "fields": "id,title,url",
            "limit": limit * 2,  # On prend plus pour avoir de la marge après filtrage
            "search": query,
            "family_filter": "true",
            "languages": "fr"
        }
        videos = requests.get(url, params=params).json().get("list", [])
        
        # Filtrage intelligent des résultats
        filtered_videos = []
        for v in videos:
            title = v.get("title", "").lower()
            
            # Critères d'exclusion
            if any(x in title for x in ["complet en francais", "film complet", "streaming"]):
                continue
                
            # Vérification que le titre original est dans le titre de la vidéo
            if query.lower() in title:
                filtered_videos.append(v)
                
            if len(filtered_videos) >= limit:
                break
                
        for v in filtered_videos:
            vid_id = v.get("id")
            results.append({
                "video_url": f"https://www.dailymotion.com/video/{vid_id}",
                "series_title": f"{query} - {v.get('title')}",
                "scan_type": scan_type,
                "tmdb_title": query
            })
            
    except Exception as e:
        print(f"Erreur pour {query}: {str(e)}")
        
    return results

def populate_clean_queue():
    """Remplissage intelligent avec contenu TMDB + Dailymotion"""
    
    # 1. Vider la table existante
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        supabase.table("analysis_results").delete().neq("id", 0).execute()
        print("Table nettoyée !")
    except Exception as e:
        print(f"Erreur nettoyage : {str(e)}")
    
    # 2. Récupérer le contenu TMDB
    series, movies = get_tmdb_kids_content()
    print(f"TMDB: {len(series)} séries et {len(movies)} films trouvés")
    
    # 3. Ajouter les séries d'animation (3 épisodes max)
    unique_videos = {}
    for show in series:
        title = show.get("title")
        print(f"Recherche série: {title}")
        videos = search_dailymotion(title, limit=3, scan_type="serie_enfant")
        for v in videos:
            v["tmdb_id"] = show.get("tmdb_id")
            v["poster_path"] = show.get("poster_path")
            unique_videos[v["video_url"]] = v
        sleep(0.5)
    
    # 4. Ajouter les films d'animation
    for movie in movies:
        title = movie.get("title")
        print(f"Recherche film: {title}")
        videos = search_dailymotion(title, limit=1, scan_type="film_animation")
        for v in videos:
            v["tmdb_id"] = movie.get("tmdb_id")
            v["poster_path"] = movie.get("poster_path")
            unique_videos[v["video_url"]] = v
        sleep(0.5)
    
    # 5. Insertion dans la queue d'analyse
    for v in unique_videos.values():
        try:
            supabase.table("analysis_results").insert(v).execute()
        except Exception as e:
            print(f"Erreur insertion {v.get('series_title')}: {str(e)}")
    
    print("Queue prete : {} videos selectionnees".format(len(unique_videos)))
    print("Note : Les posters TMDB seront utilisés automatiquement par le backend")

if __name__ == "__main__":
    populate_clean_queue()