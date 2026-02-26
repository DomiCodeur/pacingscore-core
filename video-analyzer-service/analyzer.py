"""
PacingScore Video Analyzer Service
Analyse réelle des cuts de scène avec PySceneDetect
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Pour éviter les erreurs d'import
try:
    from scenedetect import detect, ContentDetector, open_video
    from scenedetect.frame_timecode import FrameTimecode
    import cv2
except ImportError:
    print("PySceneDetect non installé. Installation nécessaire...")
    sys.exit(1)


class VideoAnalyzer:
    """Analyseur vidéo pour détecter les cuts de scène"""
    
    def __init__(self, threshold: float = 27.0, min_scene_len: int = 15):
        """
        Args:
            threshold: Seuil de détection (0-255, plus haut = moins sensible)
            min_scene_len: Durée minimale d'une scène (en frames)
        """
        self.threshold = threshold
        self.min_scene_len = min_scene_len
        
    def analyze_video(self, video_path: str) -> Dict:
        """
        Analyse une vidéo pour détecter les cuts et calculer l'ASL
        
        Retourne un dictionnaire avec les métriques
        """
        try:
            # Ouvrir la vidéo
            video = open_video(video_path)
            
            # Détecter les scènes
            scene_list = detect(
                video=video,
                detector=ContentDetector(threshold=self.threshold),
                min_scene_len=self.min_scene_len
            )
            
            # Calculer la durée totale en secondes
            total_duration = video.duration.seconds
            
            # Nombre de scènes détectées
            num_scenes = len(scene_list)
            
            # Calculer l'ASL (Average Shot Length)
            if num_scenes > 0:
                asl = total_duration / num_scenes
            else:
                asl = total_duration
            
            # Calculer le score de pacing
            pacing_score = self.calculate_pacing_score(asl)
            
            # Formatage des résultats
            result = {
                "success": True,
                "video_duration": round(total_duration, 2),
                "num_scenes": num_scenes,
                "average_shot_length": round(asl, 2),
                "pacing_score": round(pacing_score, 2),
                "evaluation": self.get_evaluation(asl),
                "scene_details": [
                    {
                        "start": start.seconds,
                        "end": end.seconds,
                        "duration": (end - start).seconds
                    }
                    for start, end in scene_list[:10]  # Limit to first 10 scenes
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pacing_score": 0
            }
    
    def calculate_pacing_score(self, asl: float) -> float:
        """
        Calcule le score de calme basé sur l'ASL
        
        ASL (Average Shot Length) = Durée moyenne d'un plan en secondes
        
        Plus l'ASL est élevée, plus le score est bon (plus calme)
        """
        # Formule logique :
        # ASL < 4s  → Score très bas (très stimulant)
        # ASL 4-9s  → Score moyen (stimulant)
        # ASL 9-14s → Score bon (calme)
        # ASL > 14s → Score excellent (très calme)
        
        if asl < 4:
            # ASL très court : très mauvais pour les enfants
            score = 10  # Score très bas
        elif asl < 6:
            # ASL court : mauvais
            score = 25
        elif asl < 8:
            # ASL moyen : acceptable
            score = 45
        elif asl < 10:
            # ASL bon : correct
            score = 65
        elif asl < 14:
            # ASL élevé : bon
            score = 80
        elif asl < 20:
            # ASL très élevé : excellent
            score = 90
        else:
            # ASL extrêmement élevé : parfait
            score = 98
        
        return score
    
    def get_evaluation(self, asl: float) -> Dict:
        """Retourne une évaluation basée sur l'ASL"""
        
        if asl < 4:
            return {
                "label": "TRÈS STIMULANT",
                "description": "Cuts extrêmement fréquents (< 4s). Déconseillé aux jeunes enfants.",
                "color": "red"
            }
        elif asl < 6:
            return {
                "label": "STIMULANT",
                "description": "Cuts fréquents (4-6s). Peut être fatigant.",
                "color": "orange"
            }
        elif asl < 8:
            return {
                "label": "MODÉRÉ",
                "description": "Cuts normaux (6-8s). Convient aux enfants plus grands.",
                "color": "yellow"
            }
        elif asl < 10:
            return {
                "label": "CALME",
                "description": "Cuts modérés (8-10s). Bon rythme pour les jeunes enfants.",
                "color": "lime"
            }
        elif asl < 14:
            return {
                "label": "TRÈS CALME",
                "description": "Cuts rares (10-14s). Idéal pour les tout-petits.",
                "color": "green"
            }
        else:
            return {
                "label": "CONTEMPLATIF",
                "description": "Cuts très rares (> 14s). Parfait pour la concentration.",
                "color": "emerald"
            }


class YouTubeDownloader:
    """Téléchargeur de vidéos YouTube via yt-dlp"""
    
    @staticmethod
    def download_video_snippet(video_url: str, output_dir: str = None, max_duration: int = 120) -> str:
        """
        Télécharge une partie d'une vidéo YouTube
        
        Args:
            video_url: URL de la vidéo
            output_dir: Dossier de sortie (par défaut: temp)
            max_duration: Durée maximale à télécharger en secondes (par défaut: 2 min)
            
        Retourne le chemin du fichier téléchargé
        """
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        # Créer le dossier
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        import hashlib
        video_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
        output_path = os.path.join(output_dir, f"video_{video_hash}.mp4")
        
        # Commande yt-dlp
        # On télécharge en 360p (suffisant pour détecter les cuts)
        # On limite à la durée max pour économiser de l'espace
        cmd = [
            "yt-dlp",
            "--format", "worst[height<=480]",
            "--download-sections", f"*0:00-{max_duration // 60}:{max_duration % 60}",
            "--merge-output-format", "mp4",
            "--quiet",
            "--no-warnings",
            "--output", output_path,
            video_url
        ]
        
        try:
            # Exécuter la commande
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                raise Exception(f"Échec du téléchargement: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Timeout lors du téléchargement")
        except Exception as e:
            raise Exception(f"Erreur yt-dlp: {str(e)}")


def main():
    """Exemple d'utilisation"""
    analyzer = VideoAnalyzer(threshold=27.0)
    downloader = YouTubeDownloader()
    
    # Exemple avec une vidéo YouTube
    video_url = "https://www.youtube.com/watch?v=EXAMPLE"
    
    try:
        # Télécharger
        print("Téléchargement de la vidéo...")
        video_path = downloader.download_video_snippet(video_url)
        
        # Analyser
        print("Analyse des cuts de scène...")
        result = analyzer.analyze_video(video_path)
        
        # Afficher les résultats
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Nettoyer
        os.remove(video_path)
        
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main()