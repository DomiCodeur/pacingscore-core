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
from typing import Dict, Any, Optional, List

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


def search_episode_flexible(title: str) -> List[Dict]:
    """
    Recherche un épisode réel via Dailymotion API (pas de clé nécessaire).
    Stratégie :
      - Recherche Dailymotion avec query large
      - Filtre de durée : 120–1800s (2–30 min)
      - Exclusion mots-clés publicitaires
      - Retourne la liste des vidéos candidates triées par durée décroissante
    """
    try:
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
            return []
        data = resp.json()
        items = data.get("list", [])
        if not items:
            logger.debug(f"Aucun résultat Dailymotion pour '{query}'")
            return []

        candidates = []

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

            candidates.append({
                'url': video_url,
                'title': video.get("title", ""),
                'duration': video_duration,
                'source': 'Dailymotion'
            })
            logger.info(f"✅ Candidat Dailymotion: {video.get('title','')[:80]} ({video_duration}s)")

        # Trier par durée décroissante
        candidates.sort(key=lambda x: x['duration'], reverse=True)
        if candidates:
            logger.info(f"🎯 {len(candidates)} vidéos candidates trouvées (max {candidates[0]['duration']}s)")
            return candidates
        else:
            logger.warning(f"Aucune vidéo Dailymotion admissible pour: {title}")
            return []

    except Exception as e:
        logger.error(f"Erreur lors de la recherche Dailymotion pour '{title}': {e}")
        return []


def search_movie_flexible(title: str) -> List[Dict]:
    """
    Recherche un film via Dailymotion API.
    Durée attendue : 30 min à 3 heures (1800–10800s)
    Retourne une liste de candidats triés par durée décroissante.
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
            return []
        data = resp.json()
        items = data.get("list", [])
        if not items:
            logger.debug(f"Aucun résultat Dailymotion pour '{query}'")
            return []

        candidates = []

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

            candidates.append({
                'url': video_url,
                'title': video.get("title", ""),
                'duration': video_duration,
                'source': 'Dailymotion'
            })
            logger.info(f"✅ Candidat Dailymotion (film): {video.get('title','')[:80]} ({video_duration}s)")

        # Trier par durée décroissante
        candidates.sort(key=lambda x: x['duration'], reverse=True)
        if candidates:
            logger.info(f"🎯 {len(candidates)} films candidates trouvés (max {candidates[0]['duration']}s)")
            return candidates
        else:
            logger.warning(f"Aucune vidéo Dailymotion admissible pour film: {title}")
            return []

    except Exception as e:
        logger.error(f"Erreur lors de la recherche film Dailymotion pour '{title}': {e}")
        return []


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
        
        meta = task.get("metadata", {})
        if not meta:
            raise Exception(f"Impossible de trouver les métadonnées dans la tâche {task_id}")
        
        title = meta.get("title") or meta.get("fr_title", "Série inconnue")
        logger.info(f"Série: {title}")
        
        media_type = task.get("media_type", "tv")
        episode_info = find_local_video_url_from_estimation(meta.get("metadata", {}))
        candidates = []
        if episode_info:
            candidates = [episode_info]  # une seule candidate locale
        else:
            if media_type == "movie":
                candidates = search_movie_flexible(title)
            else:
                candidates = search_episode_flexible(title)
        
        if not candidates:
            raise Exception(f"Impossible de trouver une vidéo pour {title}")
        
        logger.info(f"⚙️  {len(candidates)} candidats à tester")
        
        for candidate in candidates:
            video_path = None  # Réinitialiser pour chaque candidat
            video_url = candidate['url']
            logger.info(f"🎬 Essai candidat: {candidate.get('title','?')} ({candidate['duration']}s)")
            
            try:
                logger.info(f"Récupération des métadonnées: {video_url}")
                video_info = get_video_info(video_url)
                if not video_info:
                    logger.warning(f"Impossible de récupérer infos vidéo pour {video_url}, candidat suivant")
                    continue
                
                total_duration = video_info.get('duration', 0)
                logger.info(f"Durée totale: {total_duration}s")
                
                if total_duration > 300:
                    # RULE 2: Commencer au milieu (éviter intro/générique)
                    segment_start = max(60, int(total_duration * 0.1))  # au moins 60s ou 10%
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
                    logger.warning(f"Échec du téléchargement pour {video_url}, candidat suivant")
                    continue
                
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
                
                # RULE 1: Quality Check - si trop peu de scènes, vidéo suspecte
                if num_scenes < 15:
                    logger.warning(f"⚠  Candidat rejeté (QUALITY CHECK): seulement {num_scenes} scènes sur {segment_duration}s (ASL={asl:.2f}s). Vidéo suspecte (générique/statique/fake).")
                    continue  # passage au candidat suivant (le finally nettoiera)
                
                # Good candidate: sauvegarder et terminer
                success = supabase_manager.save_mollo_score(
                    tmdb_id=str(tmdb_id),
                    real_score=real_score,
                    asl=asl,
                    video_url=video_url,
                    scene_details=scene_details,
                    source=candidate.get('source', 'unknown'),
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
                logger.info(f"✅ Tâche {task_id} terminée avec succès (candidat validé)")
                return True
                
            except Exception as e:
                logger.warning(f"Erreur avec candidat {candidate.get('title', '?')}: {e}")
                continue
            finally:
                # Nettoyage de la vidéo téléchargée après chaque tentative
                if video_path and os.path.exists(video_path):
                    try:
                        os.remove(video_path)
                        logger.info(f"Vidéo supprimée: {video_path}")
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer {video_path}: {e}")
        
        # Si on arrive ici, aucun candidat n'a passé le quality check
        error_msg = f"Aucun candidat vidéo valide pour {title} après vérification qualité"
        logger.error(f"❌ {error_msg}")
        supabase_manager.mark_task_failed(task_id, error_msg)
        return False
        
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
            source=candidate.get('source', 'unknown'),
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
