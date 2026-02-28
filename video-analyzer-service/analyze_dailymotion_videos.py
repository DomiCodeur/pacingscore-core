"""
Script pour analyser les vidéos Dailymotion et les sauvegarder dans Supabase
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Ajouter le répertoire parent au path pour importer analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from analyzer import VideoAnalyzer, YouTubeDownloader
    from supabase_manager import SupabaseManager
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)


def get_videos_to_analyze() -> List[Dict[str, Any]]:
    """Récupère les vidéos Dailymotion non analysées de Supabase"""
    manager = SupabaseManager()
    
    if not manager.client:
        print("[ERROR] Supabase non configuree")
        return []
    
    try:
        # Selectionner les videos Dailymotion avec success=false ET sans pacing_score
        # (pour ne pas réanalyser les vidéos déjà échouées)
        response = manager.client.table("analysis_results").select("*").eq("scan_type", "dailymotion_enfant").eq("success", False).is_("pacing_score", "null").execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] Erreur recuperation videos: {e}")
        return []


def analyze_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse une video et retourne les resultats"""
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    video_url = video.get("video_url")
    series_title = video.get("series_title")
    video_key = video.get("video_key")
    
    print(f"\n[ANALYSE] {series_title}")
    print(f"   URL: {video_url}")
    
    # Telecharger un extrait de 60 secondes
    try:
        print("   [DOWNLOAD] Telechargement...")
        video_path = downloader.download_video_snippet(video_url, max_duration=60)
        
        if not video_path:
            print("   [ERROR] Echec telechargement")
            return {"success": False, "error": "Download failed"}
        
        print(f"   [OK] Video telechargee: {video_path}")
        
        # Analyser les flashs
        print("   Analyse flashs/scenes...")
        result = analyzer.analyze_video(video_path, analyze_motion=False, analyze_flashes=True)
        
        # Supprimer le fichier temporaire
        if os.path.exists(video_path):
            os.remove(video_path)
            print("   [CLEAN] Fichier temporaire supprime")
        
        # Si l analyse a reussi, ajouter les metadonnees
        if result.get("success"):
            result["series_title"] = series_title
            result["video_url"] = video_url
            result["video_key"] = video_key
            # result["analysis_date"] = datetime.now().isoformat()  # Commented out until column exists
            
        return result
        
    except Exception as e:
        print(f"   [ERROR] Erreur analyse: {e}")
        return {"success": False, "error": str(e)}


def save_results_to_supabase(video_id: str, result: Dict[str, Any]) -> bool:
    """Sauvegarde les resultats dans Supabase"""
    manager = SupabaseManager()
    
    if not manager.client:
        print("[ERROR] Supabase non configuree")
        return False
    
    # Preparer les donnees a mettre a jour
    update_data = {
        "success": result.get("success", False),
        "video_duration": result.get("video_duration"),
        "num_scenes": result.get("num_scenes"),
        "average_shot_length": result.get("average_shot_length"),
        "pacing_score": result.get("pacing_score"),
        "evaluation_label": result.get("evaluation", {}).get("label"),
        "evaluation_description": result.get("evaluation", {}).get("description"),
        "evaluation_color": result.get("evaluation", {}).get("color"),
        "scene_details": result.get("scene_details", []),
        # "analysis_date": datetime.now().isoformat()  # Commented out until column exists
    }
    
    if result.get("error"):
        update_data["error"] = result["error"]
    
    try:
        # Mettre a jour la ligne existante
        response = manager.client.table("analysis_results").update(update_data).eq("id", video_id).execute()
        print(f"   [OK] Resultats sauvegardes dans Supabase")
        return True
    except Exception as e:
        print(f"   [ERROR] Erreur sauvegarde Supabase: {e}")
        return False


def main():
    """Fonction principale"""
    print("=" * 60)
    print("[ANALYSE] VIDEOS DAILYMOTION - PacingScore Kids Protection")
    print("=" * 60)
    
    # Recuperer les videos a analyser
    print("\n[INFO] Recuperation des videos non analysees...")
    videos = get_videos_to_analyze()
    
    if not videos:
        print("[INFO] Aucune video a analyser (toutes sont deja analysees)")
        return
    
    print(f"[INFO] {len(videos)} videos a analyser")
    
    # Analyser chaque video
    success_count = 0
    for i, video in enumerate(videos, 1):
        print(f"\n{'='*60}")
        print(f"[INFO] Video {i}/{len(videos)}")
        print(f"{'='*60}")
        
        # Analyser la video
        result = analyze_video(video)
        
        # Sauvegarder les resultats
        if save_results_to_supabase(video["id"], result):
            success_count += 1
            print(f"[OK] Video {i} terminee avec succes")
        else:
            print(f"[ERROR] Video {i} echec sauvegarde")
        
        # Pause courte entre les videos
        if i < len(videos):
            print("   Pause de 2 secondes...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"[RESULT] RESULTATS FINAUX")
    print(f"{'='*60}")
    print(f"[OK] Videos analysees avec succes: {success_count}/{len(videos)}")
    print(f"[INFO] Taux de succes: {(success_count/len(videos)*100):.1f}%")
    
    if success_count == len(videos):
        print("\n[SUCCESS] Toutes les videos ont ete analysees !")
    else:
        print(f"\n[WARNING] {len(videos) - success_count} video(s) n'ont pas pu etre analysee(s)")


if __name__ == "__main__":
    main()