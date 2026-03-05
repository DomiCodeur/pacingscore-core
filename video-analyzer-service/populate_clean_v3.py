import os
import requests
from supabase import create_client
from time import sleep

# Configuration Supabase
SUPABASE_URL = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
SUPABASE_KEY = "sb-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwOTEwNTE3MiwiZXhwIjoyMDI0NjgxMTcyfQ.VjT6TxKKupXnWQ21FJK82CiGuvoR7dTxOiJgWJb7trk"
TMDB_API_KEY = "65a5c670b9644a800c3d59f2885d4d4f"

def clean_database():
    """Nettoie la base de donnees"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Nettoyage de la base...")
    
    # 1. Supprime les titres generiques
    data = supabase.table("video_analyses").delete().execute()
    print("- Base nettoyee")
    
    # 2. Met a jour les scores des series cultes
    series_scores = {
        "Babar": 85,
        "Peppa Pig": 75,
        "Petit Ours Brun": 65,
        "Trotro": 45,
        "Tchoupi": 35
    }
    
    for series, score in series_scores.items():
        data = supabase.table("video_analyses").update({
            "pacing_score": score
        }).like("title", f"%{series}%").execute()
    print("- Scores mis a jour")

def get_tmdb_content():
    """Recupere les series et films d'animation via TMDB"""
    print("Recuperation du contenu TMDB...")
    
    # 1. Series d'animation
    url = "https://api.themoviedb.org/3/discover/tv"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": "16,10762",  # Animation + Kids
        "language": "fr-FR",
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    series = []
    for i in range(1, 3):  # 2 pages = ~40 series
        params["page"] = i
        try:
            response = requests.get(url, params=params).json()
            for show in response.get("results", []):
                if show.get("original_language") in ["fr", "en"]:
                    series.append({
                        "title": show.get("name"),
                        "tmdb_id": show.get("id"),
                        "poster_path": show.get("poster_path")
                    })
        except Exception as e:
            print(f"Erreur TMDB Series: {str(e)}")
        sleep(0.5)
    
    # 2. Films d'animation
    url = "https://api.themoviedb.org/3/discover/movie"
    params.update({
        "with_genres": "16",
        "certification.lte": "U"
    })
    
    movies = []
    for i in range(1, 3):
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
        except Exception as e:
            print(f"Erreur TMDB Films: {str(e)}")
        sleep(0.5)
    
    print(f"- {len(series)} series et {len(movies)} films trouves")
    return series, movies

def find_video(query, limit=3):
    """Trouve les videos Dailymotion correspondantes"""
    try:
        url = "https://api.dailymotion.com/videos"
        params = {
            "fields": "id,title,url",
            "limit": limit * 2,
            "search": query,
            "languages": "fr"
        }
        response = requests.get(url, params=params).json()
        videos = response.get("list", [])
        
        filtered = []
        for v in videos:
            if len(filtered) >= limit:
                break
                
            title = v.get("title", "").lower()
            if not any(x in title for x in ["complet en francais", "film complet", "streaming"]):
                filtered.append(v)
                
        return filtered
    except Exception as e:
        print(f"Erreur Dailymotion pour {query}: {str(e)}")
        return []

def populate_database():
    """Remplit la base avec du contenu de qualite"""
    print("Population de la base...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Nettoie la base
    clean_database()
    
    # 2. Recupere le contenu TMDB
    series, movies = get_tmdb_content()
    
    # 3. Ajoute les series
    for show in series:
        videos = find_video(show["title"], limit=3)
        for v in videos:
            try:
                supabase.table("video_analyses").insert({
                    "title": show["title"],
                    "video_url": f"https://www.dailymotion.com/video/{v['id']}",
                    "pacing_score": 75,  # Score par defaut
                    "age_rating": "0+",
                    "tmdb_data": {
                        "id": show["tmdb_id"],
                        "poster_path": show["poster_path"]
                    }
                }).execute()
            except Exception as e:
                print(f"Erreur insertion {show['title']}: {str(e)}")
    
    # 4. Ajoute les films
    for movie in movies:
        videos = find_video(movie["title"], limit=1)
        for v in videos:
            try:
                supabase.table("video_analyses").insert({
                    "title": movie["title"],
                    "video_url": f"https://www.dailymotion.com/video/{v['id']}",
                    "pacing_score": 65,  # Score par defaut
                    "age_rating": "6+",
                    "tmdb_data": {
                        "id": movie["tmdb_id"],
                        "poster_path": movie["poster_path"]
                    }
                }).execute()
            except Exception as e:
                print(f"Erreur insertion {movie['title']}: {str(e)}")
    
    print("Population terminee")

if __name__ == "__main__":
    populate_database()