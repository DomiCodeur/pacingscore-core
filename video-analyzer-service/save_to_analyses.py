# -*- coding: utf-8 -*-
"""Script pour sauvegarder les resultats Dailymotion dans video_analyses"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List

try:
    from supabase_manager import SupabaseManager
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)


def save_videos_to_analyses():
    """Sauvegarde les resultats Dailymotion reussis dans video_analyses"""
    manager = SupabaseManager()
    
    if not manager.client:
        print("[ERROR] Supabase non configuree")
        return False
    
    try:
        # Recuperer les videos Dailymotion reussies mais non sauvegardees
        response = manager.client.table('analysis_results').select('*').eq('scan_type', 'dailymotion_enfant').eq('success', True).is_('pacing_score', 'null').execute()
        videos = response.data
        
        if not videos:
            print("[INFO] Toutes les videos reussies sont deja dans video_analyses")
            return True
        
        print(f"[INFO] {len(videos)} videos a sauvegarder dans video_analyses")
        
        saved_count = 0
        for i, video in enumerate(videos, 1):
            print(f"\n[VIDEO {i}/{len(videos)}] {video.get('series_title')}")
            
            # Recuperer les donnees de l analyse
            video_url = video.get('video_url')
            series_title = video.get('series_title')
            video_key = video.get('video_key')
            tmdb_id = video.get('tmdb_id')
            
            # Construire le resultat
            result = {
                'success': video.get('success'),
                'video_duration': video.get('video_duration'),
                'num_scenes': video.get('num_scenes'),
                'average_shot_length': video.get('average_shot_length'),
                'pacing_score': video.get('pacing_score'),
                'composite_score': video.get('pacing_score'),
            }
            
            # Sauvegarder dans video_analyses
            success = manager.save_analysis_result(
                result=result,
                video_url=video_url or '',
                series_title=series_title,
                tmdb_id=tmdb_id,
                video_key=video_key
            )
            
            if success:
                saved_count += 1
                print(f"   [OK] Sauvegarde dans video_analyses")
                
                # Mettre a jour pacing_score dans analysis_results
                try:
                    manager.client.table('analysis_results').update({'pacing_score': video.get('pacing_score')}).eq('id', video['id']).execute()
                    print(f"   [OK] pacing_score mis a jour dans analysis_results")
                except Exception as e:
                    print(f"   [WARN] Erreur mise a jour pacing_score: {e}")
            else:
                print(f"   [WARN] Echec sauvegarde")
        
        print(f"\n[RESULT] {saved_count}/{len(videos)} videos sauvegardees")
        return saved_count == len(videos)
    
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        return False

if __name__ == "__main__":
    save_videos_to_analyses()
