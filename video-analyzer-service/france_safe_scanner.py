import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Liste de trailers officiels sur des chaînes françaises (souvent disponibles en France)
FRANCE_SAFE_TRAILERS = [
    {"title": "Wonka (Bande-Annonce)", "url": "https://www.youtube.com/watch?v=nyH8m8M9mO0", "tmdb_id": 787699},
    {"title": "Spider-Man : Across the Spider-Verse", "url": "https://www.youtube.com/watch?v=m4v76_K_U9o", "tmdb_id": 569094},
    {"title": "Élémentaire (Disney Pixar)", "url": "https://www.youtube.com/watch?v=hXz9UAtPSTo", "tmdb_id": 976573},
    {"title": "Migration (Illumination)", "url": "https://www.youtube.com/watch?v=cZpS3CInwSg", "tmdb_id": 940551},
    {"title": "Wish : Asha et la Bonne Étoile", "url": "https://www.youtube.com/watch?v=N_H4_8M8fSc", "tmdb_id": 1022796},
    {"title": "Miraculous : Le Film", "url": "https://www.youtube.com/watch?v=yYfO2GCHq7w", "tmdb_id": 496450},
    {"title": "Bluey (Série Disney)", "url": "https://www.youtube.com/watch?v=3SIs1H6gG20", "tmdb_id": 82728},
    {"title": "La Pat' Patrouille : Le Film", "url": "https://www.youtube.com/watch?v=7uK38-U-C5o", "tmdb_id": 675353},
    {"title": "Tous en Scène 2", "url": "https://www.youtube.com/watch?v=Wp8I7bS2fV8", "tmdb_id": 438695},
    {"title": "Les Minions 2", "url": "https://www.youtube.com/watch?v=isRE4B7QREU", "tmdb_id": 438148}
]

def run_france_safe_scan():
    from analyzer import VideoAnalyzer, YouTubeDownloader
    from supabase_manager import supabase_manager
    import sys
    import io
    from datetime import datetime

    # UTF-8 pour Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8', line_buffering=True)

    print(f"--- DEMARRAGE DU SCAN FRANCE-SAFE (ANTI-BLOCAGE) ---")
    
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    for i, show in enumerate(FRANCE_SAFE_TRAILERS):
        print(f"[{i+1}/{len(FRANCE_SAFE_TRAILERS)}] Analyse: {show['title']}")
        
        # Vérification doublon
        if supabase_manager.is_already_analyzed(show['tmdb_id'], show['title']):
            print(f"   [>] Déjà dans Supabase, on passe.")
            continue
            
        try:
            # On télécharge un snippet pour l'analyse
            path = downloader.download_video_snippet(show['url'], max_duration=45) 
            if path:
                print(f"   [+] Téléchargé. Analyse Flashs/Scènes...")
                result = analyzer.analyze_video(path, analyze_motion=False, analyze_flashes=True)
                
                if os.path.exists(path): 
                    os.remove(path)
                    print(f"   [🗑️] Vidéo temporaire supprimée.")
                
                if result.get("success"):
                    # Extraction de l'ID Youtube depuis l'URL
                    v_key = show['url'].split("v=")[-1]
                    result["series_metadata"] = {
                        "title": show['title'], 
                        "scan_date": datetime.now().isoformat(),
                        "tmdb_id": show['tmdb_id'],
                        "video_key": v_key
                    }
                    
                    saved = supabase_manager.save_analysis_result(
                        result, 
                        show['url'], 
                        show['title'], 
                        tmdb_id=show['tmdb_id'], 
                        video_key=v_key
                    )
                    if saved:
                        print(f"   [OK] Injecté avec succès.")
                    else:
                        print(f"   [!] Erreur lors de l'injection.")
                else:
                    print(f"   [!] Erreur analyse: {result.get('error')}")
        except Exception as e:
            print(f"   [!!] Erreur sur {show['title']}: {e}")

if __name__ == "__main__":
    run_france_safe_scan()
