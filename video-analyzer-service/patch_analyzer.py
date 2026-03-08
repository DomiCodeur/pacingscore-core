#!/usr/bin/env python3
"""
Patch analyzer.py pour ajouter le support de l'analysesegmentée.

Modifications :
- analyze_video : ajoute start_time=0, end_time=None
- _detect_black_frames_and_flashes : ajoute start_time, end_time
- _calculate_motion_intensity : déjà supporté
- Appels internes : passer les paramètres
"""

import re
import sys

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Modifier la signature de analyze_video
    old_sig = r'def analyze_video\(self, video_path: str, analyze_motion: bool = True, analyze_flashes: bool = True\) -> Dict:'
    new_sig = 'def analyze_video(self, video_path: str, analyze_motion: bool = True, analyze_flashes: bool = True, start_time: float = 0, end_time: float = None) -> Dict:'
    content = re.sub(old_sig, new_sig, content)
    
    # 2. Ajouter start_time/end_time dans la docstring
    old_doc = '''        Args:
            video_path: Chemin vers la vidéo
            analyze_motion: Active l'analyse du mouvement
            analyze_flashes: Active la détection des flashs'''
    new_doc = '''        Args:
            video_path: Chemin vers la vidéo
            analyze_motion: Active l'analyse du mouvement
            analyze_flashes: Active la détection des flashs
            start_time: Temps de début d'analyse en secondes (optionnel)
            end_time: Temps de fin d'analyse en secondes (optionnel, None = jusqu'à la fin)'''
    content = content.replace(old_doc, new_doc)
    
    # 3. Remplacer l'appel à _detect_black_frames_and_flashes pour passer start_time, end_time
    old_flash_call = 'flash_analysis = self._detect_black_frames_and_flashes(video_path)'
    new_flash_call = 'flash_analysis = self._detect_black_frames_and_flashes(video_path, start_time, end_time)'
    content = content.replace(old_flash_call, new_flash_call)
    
    # 4. Modifier la détection des scènes pour utiliser start/end
    old_detect = '''            scene_list = detect(video_path, detector)'''
    new_detect = '''            if start_time or end_time:
                scene_list = detect(video_path, detector, start_time=start_time, end_time=end_time)
            else:
                scene_list = detect(video_path, detector)'''
    content = content.replace(old_detect, new_detect)
    
    # 5. Calcul durée analysée
    old_dur_calc = '''            cap.release()
            
            # 4. Calcul des métriques de base'''
    new_dur_calc = '''            cap.release()
            
            # Si on a un segment spécifié, calculer sa durée
            if start_time or end_time:
                segment_end = min(end_time, total_duration) if end_time else total_duration
                analyzed_duration = segment_end - start_time
            else:
                analyzed_duration = total_duration
            
            # 4. Calcul des métriques de base'''
    content = content.replace(old_dur_calc, new_dur_calc)
    
    # 6. Remplacer l'utilisation de total_duration par analyzed_duration dans ASL
    old_asl = '            asl = total_duration / num_scenes if num_scenes > 0 else total_duration'
    new_asl = '            asl = analyzed_duration / num_scenes if num_scenes > 0 else analyzed_duration'
    content = content.replace(old_asl, new_asl)
    
    # 7. Remplacer le paramètre video_duration dans le result
    old_result_dur = '                "video_duration": round(total_duration, 2),'
    new_result_dur = '                "video_duration": round(analyzed_duration, 2),  # durée analysée'
    content = content.replace(old_result_dur, new_result_dur)
    
    # 8. Mettre à jour l'appel à _calculate_motion_intensity pour passer start/end
    old_motion_call = '''                motion_intensity = self._calculate_motion_intensity(
                    video_path, 
                    start_time=0, 
                    end_time=min(30, total_duration)  # Max 30s pour le mouvement
                )'''
    new_motion_call = '''                motion_intensity = self._calculate_motion_intensity(
                    video_path, 
                    start_time=start_time, 
                    end_time=start_time + min(30, analyzed_duration)  # 30s max dans le segment
                )'''
    content = content.replace(old_motion_call, new_motion_call)
    
    # 9. Modifier _detect_black_frames_and_flashes pour accepter start_time, end_time
    old_flash_sig = '    def _detect_black_frames_and_flashes(self, video_path: str) -> Dict[str, Any]:'
    new_flash_sig = '    def _detect_black_frames_and_flashes(self, video_path: str, start_time: float = 0, end_time: float = None) -> Dict[str, Any]:'
    content = re.sub(old_flash_sig, new_flash_sig, content)
    
    # 10. Dans _detect_black_frames_and_flashes, ajouter le calcul des frames de début/fin
    old_flash_start = '''            cap = cv2.VideoCapture(video_path)
            
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
                    break'''
    new_flash_start = '''            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"black_frames": 0, "flashes": 0, "intensity": 0.0}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculer les frames de début et fin si segment spécifié
            start_frame = int(start_time * fps) if start_time > 0 else 0
            end_frame = int(end_time * fps) if end_time else total_frames
            end_frame = min(end_frame, total_frames)
            
            black_frame_count = 0
            flash_transitions = []
            prev_luminosity = None
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret or frame_count >= end_frame:
                    break
                
                if frame_count < start_frame:
                    frame_count += 1
                    continue'''
    content = content.replace(old_flash_start, new_flash_start)
    
    # 11. Écrire le fichier patché
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] {path} patched successfully")

if __name__ == '__main__':
    patch_file('analyzer.py')
