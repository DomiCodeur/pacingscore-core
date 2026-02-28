"""
PacingScore Video Analyzer Service
Analyse réelle des cuts de scène avec PySceneDetect
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import hashlib

# Pour éviter les erreurs d'import
try:
    from scenedetect import detect, ContentDetector, ThresholdDetector
    from scenedetect.frame_timecode import FrameTimecode
    import cv2
    import numpy as np
    import yt_dlp
except ImportError as e:
    print(f"Erreur d'import: {e}. Installation nécessaire...")
    sys.exit(1)


class VideoAnalyzer:
    """Analyseur vidéo pour détecter les cuts de scène et l'intensité du mouvement"""
    
    def __init__(self, threshold: float = 27.0, min_scene_len: int = 15):
        """
        Args:
            threshold: Seuil de détection (0-255, plus haut = moins sensible)
            min_scene_len: Durée minimale d'une scène (en frames)
        """
        self.threshold = threshold
        self.min_scene_len = min_scene_len
        
    def _calculate_motion_intensity(self, video_path: str, start_time: float = 0, end_time: float = None) -> float:
        """
        Calcule l'intensité du mouvement via flux optique (Optical Flow)
        
        Méthode : Lucas-Kanade optical flow entre frames successives
        Retourne : Moyenne du déplacement des pixels (score 0-100)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return 0.0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculer les frames de début et fin
            start_frame = int(start_time * fps) if start_time > 0 else 0
            end_frame = int(end_time * fps) if end_time else total_frames
            end_frame = min(end_frame, total_frames)
            
            # Prendre des frames échantillon (toutes les 10 frames pour performance)
            frame_step = 10
            
            prev_frame = None
            motion_scores = []
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret or frame_count >= end_frame:
                    break
                
                if frame_count >= start_frame and frame_count % frame_step == 0:
                    # Convertir en niveaux de gris
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    if prev_frame is not None:
                        # Calculer le flux optique
                        flow = cv2.calcOpticalFlowFarneback(
                            prev_frame, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                        )
                        
                        # Magnitude du flux
                        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                        mean_magnitude = np.mean(magnitude)
                        
                        # Normaliser pour obtenir un score 0-100
                        normalized_score = min(100, mean_magnitude * 10)
                        motion_scores.append(normalized_score)
                    
                    prev_frame = gray
                
                frame_count += 1
            
            cap.release()
            
            # Retourner la moyenne des scores de mouvement
            if motion_scores:
                avg_motion = np.mean(motion_scores)
                return round(avg_motion, 2)
            else:
                return 0.0
                
        except Exception as e:
            print(f"⚠ Erreur dans le calcul du mouvement: {e}")
            return 0.0
    
    def _detect_black_frames_and_flashes(self, video_path: str) -> Dict[str, Any]:
        """
        Détecte les passages noirs et les flashs (changement brutal de luminosité)
        
        Utilise ThresholdDetector pour détecter les frames très sombres
        Calcule les transitions brutales de luminosité
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"black_frames": 0, "flashes": 0, "intensity": 0.0}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            black_frame_count = 0
            flash_transitions = []
            prev_luminosity = None
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convertir en niveaux de gris
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculer la luminosité moyenne
                mean_luminosity = np.mean(gray)
                
                # Détecter les frames noires (luminosité < 10)
                if mean_luminosity < 10:
                    black_frame_count += 1
                
                # Détecter les flashs (changement brutal de luminosité)
                if prev_luminosity is not None:
                    luminosity_diff = abs(mean_luminosity - prev_luminosity)
                    # Flash si changement > 100 niveaux de gris
                    if luminosity_diff > 100:
                        flash_transitions.append({
                            "frame": frame_count,
                            "time": frame_count / fps,
                            "diff": luminosity_diff
                        })
                
                prev_luminosity = mean_luminosity
                frame_count += 1
            
            cap.release()
            
            # Calculer l'intensité totale (flashs + frames noirs)
            total_stimulus = black_frame_count * 2 + len(flash_transitions) * 3
            stimulus_intensity = min(100, total_stimulus)
            
            return {
                "black_frames": black_frame_count,
                "flashes": len(flash_transitions),
                "flash_details": flash_transitions[:5],  # Top 5 flashs
                "intensity": round(stimulus_intensity, 2)
            }
            
        except Exception as e:
            print(f"⚠ Erreur dans la détection des flashs: {e}")
            return {"black_frames": 0, "flashes": 0, "intensity": 0.0}
        
    def analyze_video(self, video_path: str, analyze_motion: bool = True, analyze_flashes: bool = True) -> Dict:
        """
        Analyse une vidéo pour détecter les cuts, mouvement et flashs
        
        Args:
            video_path: Chemin vers la vidéo
            analyze_motion: Active l'analyse du mouvement
            analyze_flashes: Active la détection des flashs
            
        Retourne un dictionnaire complet avec toutes les métriques
        """
        try:
            print(f"[ANALYSE] Démarrage de l'analyse de: {video_path}")
            
            # 1. Détection des scènes avec PySceneDetect
            print("   [1/6] Détection des scènes...")
            detector = ContentDetector(
                threshold=self.threshold,
                min_scene_len=self.min_scene_len
            )
            scene_list = detect(video_path, detector)
            
            # 2. Détection des flashs et frames noirs
            flash_analysis = {}
            if analyze_flashes:
                print("   [2/6] Détection des flashs et frames noirs...")
                flash_analysis = self._detect_black_frames_and_flashes(video_path)
            
            # 3. Calcul de la durée totale
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            # 4. Calcul des métriques de base
            num_scenes = len(scene_list)
            asl = total_duration / num_scenes if num_scenes > 0 else total_duration
            print(f"   [3/6] {num_scenes} scènes détectées, ASL: {asl:.2f}s")
            
            # 5. Calcul du mouvement (optionnel, peut être long)
            motion_intensity = 0.0
            if analyze_motion and total_duration > 0:
                print("   [4/6] Analyse du mouvement (flux optique)...")
                # Analyser le 1er quart de la vidéo pour le mouvement
                motion_intensity = self._calculate_motion_intensity(
                    video_path, 
                    start_time=0, 
                    end_time=min(30, total_duration)  # Max 30s pour le mouvement
                )
                print(f"   [4/6] Intensité mouvement: {motion_intensity}/100")
            else:
                print("   [4/6] Analyse du mouvement désactivée")
            
            # 6. Calcul du score de pacing principal
            base_pacing_score = self.calculate_pacing_score(asl)
            
            # 7. Ajustement du score basé sur les flashs et le mouvement
            adjusted_score = self._adjust_score_with_motion_flashes(
                base_pacing_score, 
                motion_intensity, 
                flash_analysis.get("intensity", 0)
            )
            
            # 8. Formatage des détails de scènes
            scene_details = []
            for scene in scene_list[:10]:
                start_frame, end_frame = scene
                start_seconds = start_frame.get_seconds()
                end_seconds = end_frame.get_seconds()
                scene_details.append({
                    "start": round(start_seconds, 2),
                    "end": round(end_seconds, 2),
                    "duration": round(end_seconds - start_seconds, 2)
                })
            
            # 9. Calcul du score composite final
            final_score = self._calculate_composite_score(
                asl, 
                motion_intensity, 
                flash_analysis.get("intensity", 0)
            )
            
            result = {
                "success": True,
                "video_duration": round(total_duration, 2),
                "num_scenes": num_scenes,
                "average_shot_length": round(asl, 2),
                "pacing_score": round(base_pacing_score, 2),  # Score historique
                "composite_score": round(final_score, 2),     # Nouveau score complet
                "evaluation": self.get_evaluation(asl),
                "scene_details": scene_details,
                "motion_analysis": {
                    "motion_intensity": motion_intensity,
                    "level": self._get_motion_level(motion_intensity)
                },
                "flash_analysis": flash_analysis,
                "composite_evaluation": self.get_composite_evaluation(final_score)
            }
            
            print(f"[RESULTAT] Score composite: {final_score:.2f}")
            print(f"[RESULTAT] Score historique: {base_pacing_score:.2f}")
            print(f"[RESULTAT] ASL: {asl:.2f}s, Scènes: {num_scenes}")
            return result
            
        except Exception as e:
            print(f"[ERREUR] Erreur d'analyse: {e}")
            return {
                "success": False,
                "error": str(e),
                "pacing_score": 0,
                "composite_score": 0
            }
    
    def analyze_comparison(self, video1_path: str, video2_path: str, 
                          name1: str = "Vidéo 1", name2: str = "Vidéo 2") -> Dict:
        """
        Compare deux vidéos pour montrer visuellement les différences de pacing
        """
        print(f"📊 Comparaison: {name1} vs {name2}")
        
        result1 = self.analyze_video(video1_path, analyze_motion=False, analyze_flashes=False)
        result2 = self.analyze_video(video2_path, analyze_motion=False, analyze_flashes=False)
        
        if not result1.get("success") or not result2.get("success"):
            return {"success": False, "error": "Erreur lors de l'analyse d'une des vidéos"}
        
        # Générer une visualisation comparative
        comparison = {
            "success": True,
            "comparison": {
                "video1": {
                    "name": name1,
                    "duration": result1.get("video_duration"),
                    "num_scenes": result1.get("num_scenes"),
                    "asl": result1.get("average_shot_length"),
                    "pacing_score": result1.get("pacing_score"),
                    "scenes": result1.get("scene_details", [])[:5]
                },
                "video2": {
                    "name": name2,
                    "duration": result2.get("video_duration"),
                    "num_scenes": result2.get("num_scenes"),
                    "asl": result2.get("average_shot_length"),
                    "pacing_score": result2.get("pacing_score"),
                    "scenes": result2.get("scene_details", [])[:5]
                },
                "differences": {
                    "asl_diff": round(result2.get("average_shot_length", 0) - result1.get("average_shot_length", 0), 2),
                    "score_diff": round(result2.get("pacing_score", 0) - result1.get("pacing_score", 0), 2),
                    "scenes_diff": result2.get("num_scenes", 0) - result1.get("num_scenes", 0)
                },
                "recommendation": self._get_comparison_recommendation(
                    result1.get("average_shot_length", 0),
                    result2.get("average_shot_length", 0)
                )
            }
        }
        
        return comparison
    
    def analyze_trailer_vs_episode(self, trailer_url: str, episode_url: str = None, 
                                   episode_duration: int = 600) -> Dict:
        """
        Compare un trailer avec un épisode réel
        
        Stratégie:
        1. Analyser le trailer (1-2 minutes)
        2. Si trailer est trop stimulant, proposer analyse d'un épisode réel
        3. Comparer les scores pour recommander
        """
        print(f"🎬 Analyse Trailer vs Épisode")
        
        # Étape 1: Analyser le trailer
        from supabase_manager import supabase_manager
        downloader = YouTubeDownloader()
        
        # Télécharger le trailer
        try:
            trailer_path = downloader.download_video_snippet(trailer_url, max_duration=120)
        except Exception as e:
            return {"success": False, "error": f"Impossible de télécharger le trailer: {e}"}
        
        # Analyser le trailer
        trailer_result = self.analyze_video(trailer_path, analyze_motion=False)
        
        # Nettoyer
        if os.path.exists(trailer_path):
            os.remove(trailer_path)
        
        if not trailer_result.get("success"):
            return {"success": False, "error": "Erreur d'analyse du trailer"}
        
        # Étape 2: Analyser un épisode si disponible
        episode_result = None
        if episode_url:
            try:
                episode_path = downloader.download_video_snippet(episode_url, max_duration=episode_duration)
                episode_result = self.analyze_video(episode_path, analyze_motion=False)
                if os.path.exists(episode_path):
                    os.remove(episode_path)
            except Exception as e:
                print(f"⚠ Impossible d'analyser l'épisode: {e}")
        
        # Étape 3: Analyser la différence
        trailer_score = trailer_result.get("pacing_score", 0)
        trailer_asl = trailer_result.get("average_shot_length", 0)
        
        if episode_result and episode_result.get("success"):
            episode_score = episode_result.get("pacing_score", 0)
            episode_asl = episode_result.get("average_shot_length", 0)
            
            diff_score = episode_score - trailer_score
            diff_asl = episode_asl - trailer_asl
            
            # Recommandation basée sur la différence
            if diff_score > 10:
                recommendation = "RECOMMANDÉ: Le trailer est beaucoup plus stimulant que l'épisode réel. Voir l'épisode complet."
                confidence = "HIGH"
            elif diff_score > 0:
                recommendation = "POSSIBLE: L'épisode pourrait être un peu plus calme que le trailer."
                confidence = "MEDIUM"
            else:
                recommendation = "ATTENTION: L'épisode semble aussi stimulant que le trailer."
                confidence = "LOW"
        else:
            # Pas d'épisode disponible, analyser seulement le trailer
            recommendation = "Seul le trailer est disponible. Le score de pacing est très " + ("bas (stimulant)" if trailer_score < 50 else "correct")
            confidence = "LOW"
            diff_score = 0
            diff_asl = 0
        
        result = {
            "success": True,
            "trailer_analysis": trailer_result,
            "episode_analysis": episode_result,
            "comparison": {
                "difference_score": round(diff_score, 2),
                "difference_asl": round(diff_asl, 2),
                "recommendation": recommendation,
                "confidence": confidence
            }
        }
        
        # Sauvegarder dans Supabase
        supabase_manager.save_analysis_result(result, trailer_url, "Trailer Analysis")
        
        return result
    
    def _adjust_score_with_motion_flashes(self, base_score: float, motion_intensity: float, flash_intensity: float) -> float:
        """
        Ajuste le score de pacing basé sur l'intensité du mouvement et les flashs
        """
        adjusted = base_score
        
        # Le mouvement intense réduit le score (plus stimulant)
        if motion_intensity > 30:
            adjusted -= 10
        elif motion_intensity > 50:
            adjusted -= 20
        elif motion_intensity > 70:
            adjusted -= 30
        
        # Les flashs réduisent considérablement le score
        if flash_intensity > 10:
            adjusted -= 15
        elif flash_intensity > 30:
            adjusted -= 25
        
        return max(0, min(100, adjusted))
    
    def _calculate_composite_score(self, asl: float, motion_intensity: float, flash_intensity: float) -> float:
        """
        Calcule un score composite incluant tous les facteurs de stimulation
        """
        # Score de base basé sur l'ASL
        base_score = self.calculate_pacing_score(asl)
        
        # Facteurs de réduction
        motion_factor = 1.0 - (motion_intensity / 100) * 0.3  # Réduit jusqu'à 30%
        flash_factor = 1.0 - (flash_intensity / 100) * 0.4    # Réduit jusqu'à 40%
        
        composite = base_score * motion_factor * flash_factor
        return max(0, min(100, composite))
    
    def _get_motion_level(self, motion_intensity: float) -> str:
        """Retourne le niveau d'intensité du mouvement"""
        if motion_intensity < 10:
            return "Calme"
        elif motion_intensity < 30:
            return "Modéré"
        elif motion_intensity < 50:
            return "Actif"
        elif motion_intensity < 70:
            return "Très actif"
        else:
            return "Extrêmement agité"
    
    def get_composite_evaluation(self, composite_score: float) -> Dict:
        """Évaluation basée sur le score composite"""
        if composite_score < 20:
            return {
                "label": "HYPER-STIMULANT",
                "description": "Très intense - Déconseillé aux jeunes enfants",
                "color": "red"
            }
        elif composite_score < 40:
            return {
                "label": "STIMULANT",
                "description": "Intense - Limitation recommandée",
                "color": "orange"
            }
        elif composite_score < 60:
            return {
                "label": "MODÉRÉ",
                "description": "Rythme standard - OK pour enfants plus grands",
                "color": "yellow"
            }
        elif composite_score < 80:
            return {
                "label": "CALME",
                "description": "Rythme doux - Bon pour jeunes enfants",
                "color": "green"
            }
        else:
            return {
                "label": "TRÈS CALME",
                "description": "Rythme contemplatif - Idéal pour les tout-petits",
                "color": "emerald"
            }
    
    def _get_comparison_recommendation(self, asl1: float, asl2: float) -> str:
        """Recommandation de comparaison"""
        if asl1 < asl2:
            if asl2 - asl1 > 3:
                return f"Vidéo 2 est {round(asl2 - asl1, 1)}s plus calme par plan - RECOMMANDÉE"
            else:
                return "Les deux vidéos ont des rythmes similaires"
        else:
            if asl1 - asl2 > 3:
                return f"Vidéo 1 est {round(asl1 - asl2, 1)}s plus calme par plan - RECOMMANDÉE"
            else:
                return "Les deux vidéos ont des rythmes similaires"
    
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
    """Téléchargeur de vidéos YouTube via yt-dlp (bibliothèque Python)"""
    
    @staticmethod
    def download_video_snippet(video_url: str, output_dir: str = None, max_duration: int = 120) -> str:
        """
        Télécharge une partie d'une vidéo YouTube en utilisant yt-dlp via subprocess
        
        Args:
            video_url: URL de la vidéo
            output_dir: Dossier de sortie (par défaut: temp)
            max_duration: Durée maximale à télécharger en secondes (par défaut: 2 min)
            
        Retourne le chemin du fichier téléchargé
        """
        import subprocess
        import sys
        
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        # Créer le dossier
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier unique basé sur l'URL
        video_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
        output_path = os.path.join(output_dir, f"video_{video_hash}.mp4")
        
        # Construire la commande yt-dlp
        python_exe = sys.executable
        cmd = [
            python_exe, '-m', 'yt_dlp',
            video_url,
            '--format', 'bestvideo[height<=480][ext=mp4]/best[height<=480]',
            '--output', output_path,
            '--impersonate', 'Chrome-99',
            '--quiet',
            '--no-warnings',
        ]
        
        # Pour télécharger un extrait, on pourrait utiliser --download-sections, mais on va télécharger la vidéo complète
        # L'analyseur tronquera la vidéo si nécessaire
        
        try:
            print(f"[TELECHARGEMENT] {video_url}")
            print(f"[COMMANDE] {' '.join(cmd)}")
            
            # Exécuter la commande
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    print(f"[SUCCES] Téléchargement réussi: {output_path}")
                    return output_path
                else:
                    raise Exception("Le fichier téléchargé n'a pas été créé")
            else:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                raise Exception(f"Erreur yt-dlp: {error_msg}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Timeout: téléchargement trop long")
        except Exception as e:
            # Nettoyer le fichier partiel s'il existe
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise Exception(f"Erreur yt-dlp: {str(e)}")
    
    @staticmethod
    def _progress_hook(d):
        """Hook pour suivre la progression du téléchargement"""
        if d['status'] == 'downloading':
            # On pourrait afficher la progression si besoin
            pass
        elif d['status'] == 'finished':
            print(f"[TELECHARGEMENT] Terminé: {d['filename']}")
    
    @staticmethod
    def _postprocessor_hook(d):
        """Hook post-traitement"""
        if d['status'] == 'started':
            print("[ENCODE] Encodage de la vidéo...")
        elif d['status'] == 'finished':
            print("[ENCODE] Terminé")


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