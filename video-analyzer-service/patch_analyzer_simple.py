# -*- coding: utf-8 -*-
"""
Simple patcher for analyzer.py to add start_time/end_time support
"""

import sys

def patch():
    path = 'analyzer.py'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. Change analyze_video signature
        if 'def analyze_video(self, video_path: str, analyze_motion: bool = True, analyze_flashes: bool = True) -> Dict:' in line:
            line = line.replace(
                'analyze_flashes: bool = True) -> Dict:',
                'analyze_flashes: bool = True, start_time: float = 0, end_time: float = None) -> Dict:'
            )
            new_lines.append(line)
            i += 1
            # Also update docstring
            while i < len(lines) and '"""' in lines[i]:
                new_lines.append(lines[i])
                i += 1
                if lines[i-1].strip().endswith('"""'):
                    break
                if 'analyze_motion: Active' in lines[i]:
                    # Insert new args before the blank line
                    new_lines.append(lines[i])
                    i += 1
                    new_lines.append(lines[i])  # analyze_flashes
                    i += 1
                    new_lines.append('            start_time: Temps de début d\'analyse en secondes (optionnel)\n')
                    new_lines.append('            end_time: Temps de fin d\'analyse en secondes (optionnel, None = jusqu\'à la fin)\n')
                    break
            continue
        
        # 2. Update _detect_black_frames_and_flashes signature
        if 'def _detect_black_frames_and_flashes(self, video_path: str) -> Dict[str, Any]:' in line:
            line = line.replace(
                'video_path: str) -> Dict[str, Any]:',
                'video_path: str, start_time: float = 0, end_time: float = None) -> Dict[str, Any]:'
            )
            new_lines.append(line)
            i += 1
            # Add logic after cap = cv2.VideoCapture
            while i < len(lines):
                if 'total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                    # Insert segment handling
                    new_lines.append('\n')
                    new_lines.append('            # Calculer les frames de début et fin si segment spécifié\n')
                    new_lines.append('            start_frame = int(start_time * fps) if start_time > 0 else 0\n')
                    new_lines.append('            end_frame = int(end_time * fps) if end_time else total_frames\n')
                    new_lines.append('            end_frame = min(end_frame, total_frames)\n')
                    break
                new_lines.append(lines[i])
                i += 1
            continue
        
        # 3. Update the loop in _detect_black_frames_and_flashes to respect start_frame
        if 'frame_count = 0' in line and i+1 < len(lines) and 'while True:' in lines[i+1]:
            new_lines.append(line)
            i += 1
            new_lines.append(lines[i])  # while True
            i += 1
            # Insert check for start_frame
            new_lines.append('                if frame_count < start_frame:\n')
            new_lines.append('                    frame_count += 1\n')
            new_lines.append('                    continue\n')
            continue
        
        # 4. Update condition "if not ret or frame_count >= end_frame:"
        if 'if not ret or frame_count >= end_frame:' in line:
            new_lines.append('                if not ret or frame_count >= end_frame:\n')
            i += 1
            continue
        
        # 5. Update analyze_video: add duration calculation
        if 'cap.release()' in line and i+1 < len(lines) and '# 4. Calcul' in lines[i+1]:
            new_lines.append(line)
            i += 1
            # Insert analyzed_duration calculation
            new_lines.append('\n')
            new_lines.append('            # Si on a un segment spécifié, calculer sa durée\n')
            new_lines.append('            if start_time or end_time:\n')
            new_lines.append('                segment_end = min(end_time, total_duration) if end_time else total_duration\n')
            new_lines.append('                analyzed_duration = segment_end - start_time\n')
            new_lines.append('            else:\n')
            new_lines.append('                analyzed_duration = total_duration\n')
            continue
        
        # 6. Update ASL calculation
        if 'asl = total_duration / num_scenes if num_scenes > 0 else total_duration' in line:
            new_lines.append('            asl = analyzed_duration / num_scenes if num_scenes > 0 else analyzed_duration\n')
            i += 1
            continue
        
        # 7. Update motion intensity call
        if 'motion_intensity = self._calculate_motion_intensity(' in line:
            # Capture the whole call
            call_lines = [line]
            i += 1
            while i < len(lines) and ')' not in call_lines[-1]:
                call_lines.append(lines[i])
                i += 1
            # Replace with new call
            new_lines.append('                motion_intensity = self._calculate_motion_intensity(\n')
            new_lines.append('                    video_path, \n')
            new_lines.append('                    start_time=start_time, \n')
            new_lines.append('                    end_time=start_time + min(30, analyzed_duration)  # 30s max dans le segment\n')
            new_lines.append('                )\n')
            continue
        
        # 8. Update result dict: video_duration
        if '"video_duration": round(total_duration, 2),' in line:
            new_lines.append('                "video_duration": round(analyzed_duration, 2),  # durée analysée\n')
            i += 1
            continue
        
        # 9. Update detect call in analyze_video
        if 'scene_list = detect(video_path, detector)' in line:
            new_lines.append('            if start_time or end_time:\n')
            new_lines.append('                scene_list = detect(video_path, detector, start_time=start_time, end_time=end_time)\n')
            new_lines.append('            else:\n')
            new_lines.append('                scene_list = detect(video_path, detector)\n')
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("[OK] analyzer.py patched")

if __name__ == '__main__':
    patch()
