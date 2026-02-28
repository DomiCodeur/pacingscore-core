import os
import sys
import json
import time
import io
import requests
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Env config
load_dotenv()

# UTF-8 and Unbuffered output for real-time logging
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8', line_buffering=True)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def run_auto_scan():
    from analyzer import VideoAnalyzer, YouTubeDownloader
    from supabase_manager import supabase_manager
    
    print(f"--- DEMARRAGE DU SCAN AUTOMATIQUE ---")
    
    # 1. Get trending shows - FILTRE POUR ENFANTS 6 ANS
    shows = []
    # On utilise la découverte par genre + mots-clés pour enfants
    # Genre "Animation" (16) + "Family" (10751)
    # Filtrage supplémentaire par mots-clés "kids", "children", "toddler"
    # Et on filtre par vote moyen >= 7 pour la qualité
    # ET on filtre pour les années 2020+ (plus récent pour moins de restrictions)
    url = f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16,10751&sort_by=popularity.desc&vote_average.gte=7.0&vote_count.gte=10&include_adult=false&first_air_date.gte=2020-01-01&page=1"
    r = requests.get(url)
    if r.status_code == 200:
        results = r.json().get('results', [])
        for item in results[:50]:
            tv_id = item['id']
            v_url = f"https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={TMDB_API_KEY}"
            v_res = requests.get(v_url).json()
            video_url = None
            video_key = None
            for v in v_res.get('results', []):
                if v['site'] == 'YouTube' and v['type'] in ['Trailer', 'Teaser']:
                    video_url = f"https://www.youtube.com/watch?v={v['key']}"
                    video_key = v['key']
                    break
            
            if video_url:
                # On ajoute l'année de sortie pour filtrer (2023+ pour des contenus récents pour enfants)
                year = item.get('first_air_date', '')[:4] if item.get('first_air_date') else ''
                if year and int(year) >= 2020:
                    shows.append({
                        "title": item.get('name'), 
                        "url": video_url,
                        "year": year,
                        "overview": item.get('overview', ''),
                        "genres": item.get('genre_ids', []),
                        "tmdb_id": tv_id,  # ID unique TMDB
                        "video_key": video_key  # ID unique YouTube
                    })
    
    print(f"[*] {len(shows)} dessins animés pour enfants (2020+) trouvés à analyser.")
    
    # Mettre à jour la structure pour stocker plus de metadata
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    # 2. Process
    for i, show in enumerate(shows):
        print(f"[{i+1}/{len(shows)}] Analyse: {show['title']} ({show['year']})")
        
        # Vérifier si déjà analysé (par tmdb_id ou title)
        if supabase_manager.is_already_analyzed(show['tmdb_id'], show['title']):
            print(f"   [>] Déjà analysé, passage...")
            continue
            
        try:
            path = downloader.download_video_snippet(show['url'], max_duration=60) # 1 min limit for speed
            if path:
                print(f"   [+] Téléchargé. Analyse en cours...")
                result = analyzer.analyze_video(path, analyze_motion=False, analyze_flashes=True)
                if os.path.exists(path): 
                    os.remove(path)  # SUPPRIME LA VIDÉO APRÈS ANALYSE
                    print(f"   [🗑️] Vidéo temporaire supprimée")
                
                if result.get("success"):
                    result["series_metadata"] = {
                        "title": show['title'], 
                        "scan_date": datetime.now().isoformat(),
                        "year": show['year'],
                        "overview": show['overview'],
                        "genres": show['genres'],
                        "tmdb_id": show['tmdb_id'],  # ID unique TMDB
                        "video_key": show['video_key']  # ID unique YouTube
                    }
                    # Tentative de sauvegarde
                    saved = supabase_manager.save_analysis_result(result, show['url'], show['title'], show['tmdb_id'], show['video_key'])
                    if saved:
                        print(f"   [OK] Sauvegardé dans Supabase (TMDB ID: {show['tmdb_id']})")
                    else:
                        print(f"   [!] Erreur table/BDD.")
                else:
                    print(f"   [!] Erreur analyse: {result.get('error')}")
        except Exception as e:
            print(f"   [!!] Erreur: {e}")

if __name__ == "__main__":
    run_auto_scan()
