import os
import sys
import json
import time
import io
from datetime import datetime
from dotenv import load_dotenv

# Env config
load_dotenv()

# UTF-8 and Unbuffered output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8', line_buffering=True)

# Liste de secours pour contourner le blocage TMDB
EMERGENCY_SHOWS = [
    {"title": "The Last of Us Trailer", "url": "https://www.youtube.com/watch?v=uLtkt8BonwM"},
    {"title": "Stranger Things S4 Trailer", "url": "https://www.youtube.com/watch?v=yQEondeGvKo"},
    {"title": "The Boys S4 Trailer", "url": "https://www.youtube.com/watch?v=hG9ZAnS87Yw"},
    {"title": "House of the Dragon S2", "url": "https://www.youtube.com/watch?v=fNwwt25mheo"},
    {"title": "Shogun Trailer", "url": "https://www.youtube.com/watch?v=HIs9x49DK7I"}
]

def run_emergency_scan():
    from analyzer import VideoAnalyzer, YouTubeDownloader
    from supabase_manager import supabase_manager
    
    print(f"--- DEMARRAGE DU SCAN DE SECOURS (MODE HORS-TMDB) ---")
    print(f"[*] Utilisation de {len(EMERGENCY_SHOWS)} trailers prédéfinis.")
    
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    for i, show in enumerate(EMERGENCY_SHOWS):
        print(f"[{i+1}/{len(EMERGENCY_SHOWS)}] Analyse: {show['title']}")
        try:
            # On limite à 30 secondes pour aller très vite et tester la chaîne complète
            path = downloader.download_video_snippet(show['url'], max_duration=30) 
            if path:
                print(f"   [+] Téléchargé. Analyse en cours...")
                result = analyzer.analyze_video(path, analyze_motion=False, analyze_flashes=True)
                if os.path.exists(path): os.remove(path)
                
                if result.get("success"):
                    result["series_metadata"] = {"title": show['title'], "scan_date": datetime.now().isoformat()}
                    saved = supabase_manager.save_analysis_result(result, show['url'], show['title'])
                    if saved:
                        print(f"   [OK] Sauvegardé dans Supabase.")
                    else:
                        print(f"   [!] Erreur table/BDD.")
                else:
                    print(f"   [!] Erreur analyse: {result.get('error')}")
        except Exception as e:
            print(f"   [!!] Erreur: {e}")

if __name__ == "__main__":
    run_emergency_scan()
