import os
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def find_tmdb_id(title, year=None):
    """Cherche l'ID TMDB correspondant à un titre"""
    # Préparer la requête (recherche dans les films et séries)
    url_movie = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&include_adult=false"
    url_tv = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={title}&include_adult=false"
    
    try:
        # Chercher dans les films
        r = requests.get(url_movie)
        if r.status_code == 200:
            results = r.json().get('results', [])
            if results:
                # Vérifier l'année si fournie
                if year:
                    for item in results:
                        if item.get('release_date', '')[:4] == str(year):
                            return item['id'], 'movie'
                # Sinon prendre le premier
                return results[0]['id'], 'movie'
        
        # Chercher dans les séries
        r = requests.get(url_tv)
        if r.status_code == 200:
            results = r.json().get('results', [])
            if results:
                if year:
                    for item in results:
                        if item.get('first_air_date', '')[:4] == str(year):
                            return item['id'], 'tv'
                return results[0]['id'], 'tv'
        
    except Exception as e:
        print(f"Erreur recherche TMDB: {e}")
    
    return None, None

def get_video_info(video_id):
    """Récupère les informations d'une vidéo YouTube depuis l'API TMDB"""
    # Chercher les vidéos pour ce film/série
    # Note: on ne peut pas faire ça directement sans l'ID TMDB
    # On va plutôt chercher par titre
    return None

# Liste des vidéos YouTube trouvées
youtube_videos = [
    {"title": "BALLERINA (Animation, Danse - 2016) - NOUVELLE Bande Annonce VF / FilmsActu", 
     "url": "https://www.youtube.com/watch?v=xLpySILgb5k", "year": 2016},
    {"title": "LE GRAND MECHANT RENARD Bande Annonce VF (Animation, 2017)", 
     "url": "https://www.youtube.com/watch?v=ds_w9o2I8Yw", "year": 2017},
    {"title": "MISS PEREGRINE Bande Annonce VF (TIM BURTON - 2016)", 
     "url": "https://www.youtube.com/watch?v=i-TiNC3zpPw", "year": 2016},
    {"title": "Bande annonce \"Fenetre sur le parascolaire\"", 
     "url": "https://www.youtube.com/watch?v=4aWWbCnlgHw", "year": None},
    {"title": "La recree de Lucie Bande annonce", 
     "url": "https://www.youtube.com/watch?v=xFjQZGqFtZQ", "year": None},
    {"title": "Accompagner la parentalite - Bande-annonce", 
     "url": "https://www.youtube.com/watch?v=2KFRy-86Bek", "year": None}
]

print("Recherche des IDs TMDB correspondants...")
print("="*50)

video_data = []
for video in youtube_videos:
    # Extraire le titre principal (avant le pipe)
    main_title = video['title'].split(' - ')[0].split('Band')[0].strip()
    
    # Chercher l'ID TMDB
    tmdb_id, media_type = find_tmdb_id(main_title, video['year'])
    
    if tmdb_id:
        print(f"[OK] {main_title} -> ID TMDB: {tmdb_id} ({media_type})")
        video['tmdb_id'] = tmdb_id
        video['media_type'] = media_type
        video['simple_title'] = main_title
        video_data.append(video)
    else:
        print(f"[NO] {main_title} -> Non trouve sur TMDB")

print("\n" + "="*50)
print(f"Total: {len(video_data)} vidéos avec correspondance TMDB")

# Sauvegarder dans un fichier pour le scanner
import json
with open('france_safe_videos.json', 'w', encoding='utf-8') as f:
    json.dump(video_data, f, ensure_ascii=False, indent=2)

print("\nDonnees sauvegardees dans france_safe_videos.json")
print("\nExemple de format:")
print(json.dumps(video_data[0] if video_data else {}, ensure_ascii=False, indent=2))
