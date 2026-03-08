"""
Worker Python pour l'analyse vidéo réelle (Indice Mollo)

Récupère les tâches dans analysis_tasks, trouve le trailer YouTube, analyse la vidéo,
et sauvegarde le score réel dans mollo_scores.
"""

import os
import sys
import time
import json
import logging
import requests
from typing import Dict, Any, Optional

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import VideoAnalyzer, YouTubeDownloader
from supabase_manager import supabase_manager
import subprocess

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paramètres
POLL_INTERVAL = 5  # secondes entre chaque vérification de tâches
MAX_ANALYSIS_DURATION = 120  # secondes max d'analyse (trailer)
# Dossier temporaire : utiliser TEMP_DIR si défini, sinon un sous-dossier unique par conteneur
base_temp = os.getenv("TEMP_DIR", "/tmp/videos")
# Isoler par hostname de conteneur pour éviter les conflits entre workers scalés
container_id = os.uname().nodename if hasattr(os, 'uname') else os.getenv("HOSTNAME", "unknown")
TEMP_DIR = os.path.join(base_temp, container_id)
os.makedirs(TEMP_DIR, exist_ok=True)

# Services
analyzer = VideoAnalyzer(threshold=27.0)
downloader = YouTubeDownloader()


def get_video_info(video_url: str) -> Optional[Dict]:
    """
    Récupère les métadonnées d'une vidéo sans la télécharger.
    Retourne un dict avec 'duration', 'title', etc.
    """
    try:
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            video_url,
            '--dump-single-json',
            '--no-download',
            '--quiet',
            '--no-warnings',
            '--ignore-errors',
            '--no-check-certificate',
            '--geo-bypass',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            info = json.loads(result.stdout)
            return info
        else:
            logger.debug(f"get_video_info failed for {video_url}: {result.stderr[:200]}")
    except Exception as e:
        logger.error(f"Erreur get_video_info pour {video_url}: {e}")
    return None


def search_episode_flexible(title: str) -> Optional[Dict]:
    """
    Recherche un épisode réel via Dailymotion API (pas de clé nécessaire).
    Stratégie :
      - Recherche Dailymotion avec query large
      - Filtre de durée : 120–1800s (2–30 min)
      - Exclusion mots-clés publicitaires
      - Retourne la vidéo la plus longue
    """
    try:
        # Dailymotion API publique
        query = f"{title} episode"
        logger.info(f"Recherche Dailymotion: '{query}'")
        url = "https://api.dailymotion.com/videos"
        params = {
            "search": query,
            "limit": "10",
            "fields": "id,title,duration,url"
        }
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Dailymotion API error {resp.status_code}")
            return None
        data = resp.json()
        items = data.get("list", [])
        if not items:
            logger.debug(f"Aucun résultat Dailymotion pour '{query}'")
            return None

        best_candidate = None
        best_duration = 0

        for video in items:
            video_url = video.get("url")
            video_duration = video.get("duration", 0)
            video_title = video.get("title", "").lower()

            # Exclure trailers/teasers
            if any(kw in video_title for kw in ['trailer', 'bande-annonce', 'teaser', 'preview', 'promo', 'official trailer']):
                logger.debug(f"Exclu (trailer): {video_title[:50]}")
                continue

            # Durée 2-30 min
            if not (120 <= video_duration <= 1800):
                logger.debug(f"Durée hors plage ({video_duration}s): {video_title[:50]}")
                continue

            if video_duration > best_duration:
                best_duration = video_duration
                best_candidate = {
                    'url': video_url,
                    'title': video.get("title", ""),
                    'duration': video_duration,
                    'source': 'Dailymotion'
                }
                logger.info(f"✅ Candidat Dailymotion: {video.get('title','')[:80]} ({video_duration}s)")

        if best_candidate:
            logger.info(f"🎯 Meilleure vidéo Dailymotion sélectionnée: {best_candidate['title'][:80]} ({best_candidate['duration']}s)")
            return best_candidate
        else:
            logger.warning(f"Aucune vidéo Dailymotion admissible pour: {title}")
            return None

    except Exception as e:
        logger.error(f"Erreur lors de la recherche Dailymotion pour '{title}': {e}")
        return None


def search_movie_flexible(title: str) -> Optional[Dict]:
    """
    Recherche un film via Dailymotion API.
    Durée attendue : 30 min à 3 heures (1800–10800s)
    """
    try:
        query = f"{title}"
        logger.info(f"Recherche Dailymotion (film): '{query}'")
        url = "https://api.dailymotion.com/videos"
        params = {
            "search": query,
            "limit": "10",
            "fields": "id,title,duration,url"
        }
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            logger.error(f"Dailymotion API error {resp.status_code}")
            return None
        data = resp.json()
        items = data.get("list", [])
        if not items:
            logger.debug(f"Aucun résultat Dailymotion pour '{query}'")
            return None

        best_candidate = None
        best_duration = 0

        for video in items:
            video_url = video.get("url")
            video_duration = video.get("duration", 0)
            video_title = video.get("title", "").lower()

            # Exclure trailers/teasers
            if any(kw in video_title for kw in ['trailer', 'bande-annonce', 'teaser', 'preview', 'promo', 'official trailer', 'extrait']):
                logger.debug(f"Exclu (trailer): {video_title[:50]}")
                continue

            # Durée 30 min à 3 heures
            if not (1800 <= video_duration <= 10800):
                logger.debug(f"Durée hors plage film ({video_duration}s): {video_title[:50]}")
                continue

            if video_duration > best_duration:
                best_duration = video_duration
                best_candidate = {
                    'url': video_url,
                    'title': video.get("title", ""),
                    'duration': video_duration,
                    'source': 'Dailymotion'
                }
                logger.info(f"✅ Candidat Dailymotion (film): {video.get('title','')[:80]} ({video_duration}s)")

        if best_candidate:
            logger.info(f"🎯 Film sélectionné: {best_candidate['title'][:80]} ({best_candidate['duration']}s)")
            return best_candidate
        else:
            logger.warning(f"Aucune vidéo Dailymotion admissible pour film: {title}")
            return None

    except Exception as e:
        logger.error(f"Erreur lors de la recherche film Dailymotion pour '{title}': {e}")
        return None


def find_local_video_url_from_estimation(metadata: Dict) -> Optional[Dict]:
    """
    Si l'estimation contient déjà une vidéo, on peut l'utiliser.
    """
    if metadata:
        video_path = metadata.get("video_path")
        if video_path and video_path.startswith("http"):
            return {
                'url': video_path,
                'title': metadata.get('fr_title', 'Vidéo locale'),
                'duration': None
            }
    return None


def process_task(task: Dict[str, Any]) -> bool:
    """
    Traite une tâche d'analyse.
    """
    task_id = task.get("id")
    tmdb_id = task.get("tmdb_id")
    
    if not task_id or not tmdb_id:
        logger.error(f"Tâche invalide: {task}")
        return False
    
    logger.info(f"=== Traitement tâche {task_id} (TMDB ID: {tmdb_id}) ===")
    
    video_path = None
    try:
        supabase_manager.update_analysis_task_status(task_id, "processing")
        
        meta = supabase_manager.get_metadata_estimation(tmdb_id)
        if not meta:
            raise Exception(f"Impossible de trouver l'estimation pour TMDB ID {tmdb_id}")
        
        title = meta.get("title") or meta.get("metadata", {}).get("fr_title", "Série inconnue")
        logger.info(f"Série: {title}")
        
        media_type = meta.get("media_type", "tv")
        episode_info = find_local_video_url_from_estimation(meta.get("metadata", {}))
        if not episode_info:
            if media_type == "movie":
                episode_info = search_movie_flexible(title)
            else:
                episode_info = search_episode_flexible(title)
        
        if not episode_info:
            raise Exception(f"Impossible de trouver une vidéo pour {title}")
        
        video_url = episode_info['url']
        logger.info(f"Vidéo trouvée: {episode_info.get('title', '?')} (url: {video_url})")
        
        logger.info(f"Récupération des métadonnées: {video_url}")
        video_info = get_video_info(video_url)
        if not video_info:
            raise Exception("Impossible de récupérer les infos de la vidéo")
        
        total_duration = video_info.get('duration', 0)
        logger.info(f"Durée totale: {total_duration}s")
        
        if total_duration > 300:
            segment_start = 120
            segment_duration = min(MAX_ANALYSIS_DURATION, total_duration - segment_start)
        else:
            segment_start = 0
            segment_duration = min(MAX_ANALYSIS_DURATION, total_duration)
        
        logger.info(f"Segment analysé: start={segment_start}s, duration={segment_duration}s")
        
        logger.info(f"Téléchargement du segment: {video_url}")
        video_path = downloader.download_video_snippet(
            video_url=video_url,
            output_dir=TEMP_DIR,
            max_duration=segment_duration,
            start_time=segment_start
        )
        
        if not video_path:
            raise Exception("Échec du téléchargement")
        
        logger.info("Analyse vidéo en cours...")
        result = analyzer.analyze_video(video_path, analyze_motion=True, analyze_flashes=True)
        
        if not result.get("success"):
            error_msg = result.get("error", "Échec de l'analyse")
            raise Exception(f"Analyse échouée: {error_msg}")
        
        asl = result.get("average_shot_length", 0)
        real_score = result.get("composite_score", result.get("pacing_score", 0))
        num_scenes = result.get("num_scenes", 0)
        scene_details = result.get("scene_details", [])
        video_duration_analysis = result.get("video_duration", 0)
        cuts_per_minute = (num_scenes / video_duration_analysis * 60) if video_duration_analysis > 0 else 0
        motion_intensity = result.get("motion_analysis", {}).get("motion_intensity", 0.0)
        
        logger.info(f"Résultat: ASL={asl:.2f}s, Score={real_score:.1f}, Scènes={num_scenes}, CPM={cuts_per_minute:.2f}, Motion={motion_intensity:.2f}")
        
        success = supabase_manager.save_mollo_score(
            tmdb_id=str(tmdb_id),
            real_score=real_score,
            asl=asl,
            video_url=video_url,
            scene_details=scene_details,
            source=episode_info.get('source', 'unknown'),
            video_type='episode' if media_type == 'tv' else 'film',
            cuts_per_minute=cuts_per_minute,
            video_duration=video_duration_analysis,
            motion_intensity=motion_intensity,
            metadata=meta  # transmet les métadonnées complètes de la tâche
        )
        
        if not success:
            logger.error(f"Échec sauvegarde Mollo pour TMDB ID {tmdb_id} - tâche {task_id}")
            raise Exception("Échec de la sauvegarde du score Mollo")
        
        supabase_manager.mark_task_completed(task_id)
        logger.info(f"✅ Tâche {task_id} terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur sur tâche {task_id}: {e}")
        supabase_manager.mark_task_failed(task_id, str(e))
        return False
        
    finally:
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Vidéo supprimée: {video_path}")
            except Exception as e:
                logger.warning(f"Impossible de supprimer la vidéo {video_path}: {e}")


def main_loop():
    """Boucle principale du worker"""
    logger.info("🚀 Démarrage du worker Mollo")
    logger.info(f"Polling toutes les {POLL_INTERVAL}s")
    logger.info("=" * 60)
    
    processed_count = 0
    
    while True:
        try:
            logger.debug("Recherche de tâches pending...")
            task = supabase_manager.get_next_pending_task()
            
            if task:
                logger.info(f"Tâche trouvée: ID={task.get('id')} TMDB={task.get('tmdb_id')}")
                success = process_task(task)
                if success:
                    processed_count += 1
                    logger.info(f"📊 Total traité: {processed_count} tâches")
            else:
                logger.debug("Aucune tâche pending, attente...")
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL)
    
    logger.info("👋 Worker arrêté")


if __name__ == "__main__":
    main_loop()
