import os
import sys
import json
import io
from datetime import datetime
from dotenv import load_dotenv

# UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8', line_buffering=True)

load_dotenv()

def run_france_scan_v2():
    from analyzer import VideoAnalyzer, YouTubeDownloader
    from supabase_manager import supabase_manager
    
    print(f"--- SCAN FRANCE V2 - VIDEOS TESTEES ---")
    
    # Charger les vidéos testées
    try:
        with open('france_safe_videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
    except FileNotFoundError:
        print("[ERROR] Fichier france_safe_videos.json introuvable")
        print("Lancez d'abord find_tmdb_ids.py")
        return
    
    if not videos:
        print("[ERROR] Aucune vidéo dans la liste")
        return
    
    print(f"[*] {len(videos)} vidéos à analyser")
    
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    for i, video in enumerate(videos):
        title = video.get('simple_title', video.get('title', 'Inconnu'))
        tmdb_id = video.get('tmdb_id')
        url = video.get('url')
        
        print(f"\n[{i+1}/{len(videos)}] Analyse: {title}")
        
        # Vérifier si déjà analysé
        if tmdb_id and supabase_manager.is_already_analyzed(tmdb_id, title):
            print(f"   [>] Déjà dans Supabase, passage...")
            continue
            
        try:
            # Télécharger un snippet (1 min max pour aller vite)
            path = downloader.download_video_snippet(url, max_duration=60)
            
            if path:
                print(f"   [+] Téléchargé. Analyse Flashs/Scènes...")
                result = analyzer.analyze_video(path, analyze_motion=False, analyze_flashes=True)
                
                if os.path.exists(path):
                    os.remove(path)
                    print(f"   [🗑️] Vidéo temporaire supprimée")
                
                if result.get("success"):
                    # Extraire l'ID YouTube de l'URL
                    video_key = url.split("v=")[-1].split("&")[0]
                    
                    result["series_metadata"] = {
                        "title": title,
                        "scan_date": datetime.now().isoformat(),
                        "tmdb_id": tmdb_id,
                        "video_key": video_key,
                        "media_type": video.get('media_type', 'movie')
                    }
                    
                    saved = supabase_manager.save_analysis_result(
                        result,
                        url,
                        title,
                        tmdb_id=tmdb_id,
                        video_key=video_key
                    )
                    
                    if saved:
                        print(f"   [OK] Injecté avec succès")
                    else:
                        print(f"   [!] Erreur injection Supabase")
                else:
                    print(f"   [!] Erreur analyse: {result.get('error')}")
            else:
                print(f"   [⚠️] Échec téléchargement (vidéo non disponible ?)")
                
        except Exception as e:
            print(f"   [❌] Erreur: {e}")
    
    print(f"\n[FIN] Scan terminé")

if __name__ == "__main__":
    run_france_scan_v2()
