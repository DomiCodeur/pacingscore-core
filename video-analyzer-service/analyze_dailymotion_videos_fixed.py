import os
import sys
import time
import subprocess
import tempfile
import hashlib
from datetime import datetime

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

PROJECT_ROOT = r"C:\Users\mathi\Documents\GitHub\pacingscore-clean\video-analyzer-service"
sys.path.append(PROJECT_ROOT)

try:
    from analyzer import VideoAnalyzer
    from supabase_manager import SupabaseManager
except ImportError as e:
    print(f"Erreur d'import: {e}"); sys.exit(1)

def get_videos_to_analyze():
    manager = SupabaseManager()
    if not manager.client: return []
    try:
        response = manager.client.table("analysis_results").select("*").limit(200).execute()
        return [v for v in response.data if v.get('pacing_score') is None]
    except Exception as e:
        print(f"ERROR Fetching queue: {e}"); return []

def analyze_video_fast(video):
    analyzer = VideoAnalyzer(threshold=27.0)
    url = video.get("video_url")
    title = video.get("series_title")
    print(f"ANALYSE EN COURS: {title}")
    
    video_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    output_path = os.path.join(tempfile.gettempdir(), f"fast_{video_hash}.mp4")
    
    cmd = [sys.executable, '-m', 'yt_dlp', url, '--format', 'best[ext=mp4]/best', '--output', output_path, '--quiet', '--no-warnings', '--download-sections', '*0-120']
    
    try:
        subprocess.run(cmd, timeout=300) 
        if not os.path.exists(output_path): return {"success": False, "error": "DL failed"}
        result = analyzer.analyze_video(output_path, analyze_motion=False, analyze_flashes=False)
        if os.path.exists(output_path): os.remove(output_path)
        return result
    except Exception as e: 
        return {"success": False, "error": str(e)}

def save_result(video, result):
    manager = SupabaseManager()
    if not result.get("success", False):
        manager.client.table("analysis_results").update({"pacing_score": 0}).eq("id", video["id"]).execute()
        return

    # Normalisation du titre (Série vs Épisode)
    original_title = video.get("series_title")
    final_title = original_title
    final_score = int(result.get("pacing_score", 0))
    
    # Mapping Intelligence de Série
    series_rules = {
        "Petit Ours Brun": ["petit ours brun"],
        "Peppa Pig": ["peppa pig"],
        "Babar": ["babar"],
        "Trotro": ["trotro"],
        "Tchoupi": ["tchoupi"],
        "Simon": ["simon le lapin", "simon"],
        "Masha et l'Ours": ["masha"]
    }
    
    # On force les scores validés pour ces classiques
    fixed_scores = {"Petit Ours Brun": 65, "Peppa Pig": 75, "Babar": 85}

    for name, keywords in series_rules.items():
        if any(kw in original_title.lower() for kw in keywords):
            final_title = name
            if name in fixed_scores:
                final_score = fixed_scores[name]
            break

    # Mise à jour queue
    manager.client.table("analysis_results").update({"pacing_score": final_score, "success": True}).eq("id", video["id"]).execute()

    # Synchro Front (avec UPSERT manuel car on sait que l'id Supabase change)
    # Pour simuler un upsert sur video_path sans contrainte d'unicité, on cherche d'abord
    existing = manager.client.table("video_analyses").select("id").eq("video_path", final_title).execute()
    
    metadata = {"asl": result.get("average_shot_length"), "source": "intelligent_crawler", "display_age": "0+"}
    final_data = {
        "video_path": final_title,
        "pacing_score": final_score,
        "cuts_per_minute": (result.get("num_scenes", 0) / max(1, result.get("video_duration", 1))) * 60,
        "metadata": metadata,
        "analyzed_at": datetime.now().isoformat(),
        "age_rating": "0+"
    }

    try:
        if existing.data:
            # On met à jour l'existant (Pas de doublon !)
            manager.client.table("video_analyses").update(final_data).eq("id", existing.data[0]["id"]).execute()
            print(f"  MAJ SÉRIE TERMINÉE: {final_title} ({final_score}%)")
        else:
            # On insère le nouveau
            manager.client.table("video_analyses").insert(final_data).execute()
            print(f"  NOUVELLE SÉRIE TERMINÉE: {final_title} ({final_score}%)")
    except Exception as e:
        print(f"  ERREUR SYNC: {e}")

def main():
    print("DEMARRAGE DU FILLER INTELLIGENT (Séries groupées)...")
    while True:
        videos = get_videos_to_analyze()
        if not videos:
            print("En attente..."); time.sleep(30); continue
        for video in videos:
            result = analyze_video_fast(video)
            save_result(video, result)
            time.sleep(1)

if __name__ == "__main__":
    main()
