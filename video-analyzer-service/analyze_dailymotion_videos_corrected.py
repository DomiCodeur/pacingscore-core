# -*- coding: utf-8 -*-
"""
Script pour analyser les videos Dailymotion et les sauvegarder dans Supabase
Corrige le probleme de yt-dlp pour Dailymotion
"""

import os
import sys
import time
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ajouter le repertoire parent au path pour importer analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from analyzer import VideoAnalyzer
    from supabase_manager import SupabaseManager
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)


def download_dailymotion_video(video_url: str, max_duration: int = 60) -> Optional[str]:
    """
    Telecharge un extrait d'une video Dailymotion via yt-dlp
    
    Args:
        video_url: URL de la video Dailymotion
        max_duration: Duree maximale en secondes
    
    Returns:
        Chemin du fichier telecharge ou None
    """
    temp_dir = tempfile.gettempdir()
    video_id = video_url.split("/")[-1]
    output_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
    
    # Essayer plusieurs formats pour Dailymotion
    formats = [
        "best[height<=480]/best",
        "best[height<=480][ext=mp4]/best[height<=480]",
        "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
        "best[ext=mp4]/best",
    ]
    
    for fmt in formats:
        cmd = [
            "yt-dlp",
            "--format", fmt,
            "--output", output_path,
            "--quiet",
            "--no-warnings",
            "--no-check-certificate",
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"   [OK] Video telechargee avec format: {fmt}")
                return output_path
            else:
                print(f"   [WARN] Format '{fmt}' a echoue")
        except subprocess.TimeoutExpired:
            print(f"   [WARN] Timeout avec format: {fmt}")
        except Exception as e:
            print(f"   [WARN] Erreur avec format '{fmt}': {e}")
    
    # Nettoyer le fichier partiel s'il existe
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except:
            pass
    
    return None


def get_videos_to_analyze() -> List[Dict[str, Any]]:
    """Recupere les videos Dailymotion non analysees de Supabase"""
    manager = SupabaseManager()
    
    if not manager.client:
        print("[ERROR] Supabase non configuree")
        return []
    
    try:
        # Recuperer les videos Dailymotion avec success=False ou pacing_score NULL
        response = manager.client.table("analysis_results").select("*").eq("scan_type", "dailymotion_enfant").execute()
        videos = response.data
        
        # Filtrer: seulement celles non analysees (pacing_score NULL) ou echecs
        to_analyze = [v for v in videos if v.get("pacing_score") is None or not v.get("success")]
        
        return to_analyze
    except Exception as e:
        print(f"[ERROR] Erreur recuperation videos: {e}")
        return []


def analyze_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse une video et retourne les resultats"""
    analyzer = VideoAnalyzer(threshold=27.0)
    
    video_url = video.get("video_url")
    series_title = video.get("series_title")
    video_key = video.get("video_key")
    
    print(f"\n[ANALYSE] {series_title}")
    print(f"   URL: {video_url}")
    
    # Telecharger un extrait de 60 secondes
    try:
        print("   [DOWNLOAD] Telechargement...")
        video_path = download_dailymotion_video(video_url, max_duration=60)
        
        if not video_path:
            print("   [ERROR] Echec telechargement")
            return {"success": False, "error": "Download failed"}
        
        print(f"   [OK] Video telechargee: {video_path}")
        
        # Analyser les flashs
        print("   [ANALYSIS] Analyse flashs/scenes...")
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
            
        return result
        
    except Exception as e:
        print(f"   [ERROR] Erreur analyse: {e}")
        return {"success": False, "error": str(e)}


def save_results_to_supabase(video_id: str, result: Dict[str, Any], video_url: str = None, series_title: str = None, video_key: str = None, tmdb_id: int = None) -> bool:
    """Sauvegarde les resultats dans analysis_results ET video_analyses"""
    manager = SupabaseManager()
    
    if not manager.client:
        print("[ERROR] Supabase non configuree")
        return False
    
    # 1. Mettre a jour la tache dans analysis_results
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
    }
    
    if result.get("error"):
        update_data["error"] = result["error"]
    
    try:
        response = manager.client.table("analysis_results").update(update_data).eq("id", video_id).execute()
        print(f"   [OK] Resultats mis a jour dans analysis_results")
    except Exception as e:
        print(f"   [ERROR] Erreur mise a jour analysis_results: {e}")
        return False
    
    # 2. Si analyse reussie, inserer dans video_analyses
    if result.get("success"):
        success = manager.save_analysis_result(
            result=result,
            video_url=video_url or "",
            series_title=series_title,
            tmdb_id=tmdb_id,
            video_key=video_key
        )
        if success:
            print(f"   [OK] Resultat sauvegarde dans video_analyses")
        else:
            print(f"   [WARN] Echec sauvegarde video_analyses")
    
    return True


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
        if save_results_to_supabase(
            video["id"], 
            result, 
            video_url=video.get("video_url"),
            series_title=video.get("series_title"),
            video_key=video.get("video_key"),
            tmdb_id=video.get("tmdb_id")
        ):
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
