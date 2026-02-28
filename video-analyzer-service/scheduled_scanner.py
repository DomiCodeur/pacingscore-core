"""
Système de scan programmé pour PacingScore
Analyse les nouveautés automatiquement selon des priorités
"""

import os
import sys
import json
import schedule
import time
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
from analyzer import VideoAnalyzer, YouTubeDownloader
from supabase_manager import supabase_manager

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf8')

# Simuler une base de données de séries à scanner
SAMPLE_SERIES_DB = [
    {
        "title": "Puffin Rock",
        "type": "series",
        "trailer_url": "https://www.youtube.com/watch?v=XIdp_T6r92s",
        "priority": 1,
        "category": ["Animation", "Bébé", "Nature"]
    },
    {
        "title": "Bluey",
        "type": "series",
        "trailer_url": "https://www.youtube.com/watch?v=0_u6eCH6fO0",
        "priority": 1,
        "category": ["Animation", "Famille", "Humour"]
    },
    {
        "title": "Peppa Pig",
        "type": "series",
        "trailer_url": "https://www.youtube.com/watch?v=S53pL0D7oG0",
        "priority": 2,
        "category": ["Animation", "Bébé", "Educatif"]
    },
    {
        "title": "Cocomelon",
        "type": "series",
        "trailer_url": "https://www.youtube.com/watch?v=t_6_G0S6_9s",
        "priority": 2,
        "category": ["Animation", "Musique", "Bébé"]
    }
]


class ScheduledScanner:
    """Scanneur programmé pour analyser automatiquement les séries"""
    
    def __init__(self, analyzer: VideoAnalyzer, downloader: YouTubeDownloader):
        self.analyzer = analyzer
        self.downloader = downloader
        self.series_db = SAMPLE_SERIES_DB
        self.scanned_today = set()
        
    def get_priority_series(self, limit: int = 5) -> List[Dict]:
        """Récupère les séries à scanner par priorité"""
        print(f"[*] Récupération des séries à scanner (max: {limit})")
        
        # Filtrer par priorité
        priority_1 = [s for s in self.series_db if s["priority"] == 1]
        priority_2 = [s for s in self.series_db if s["priority"] == 2]
        
        result = []
        for series in priority_1 + priority_2:
            if len(result) >= limit:
                break
            if series["trailer_url"] not in self.scanned_today:
                result.append(series)
        
        print(f"[+] {len(result)} séries sélectionnées")
        return result
    
    def scan_series(self, series: Dict[str, Any]) -> Dict[str, Any]:
        """Scanne une série et sauvegarde le résultat"""
        title = series.get("title", "Série inconnue")
        trailer_url = series.get("trailer_url")
        
        if not trailer_url:
            return {"success": False, "error": "URL manquante", "title": title}
        
        print(f"\n{'='*60}")
        print(f"[*] Scannage: {title}")
        print(f"{'='*60}")
        
        try:
            print(f"   Téléchargement du trailer...")
            video_path = self.downloader.download_video_snippet(
                video_url=trailer_url,
                max_duration=120
            )
            
            if not video_path:
                raise Exception("Echec du téléchargement")
            
            print(f"   Analyse du trailer...")
            result = self.analyzer.analyze_video(
                video_path, 
                analyze_motion=False,
                analyze_flashes=True
            )
            
            if os.path.exists(video_path):
                os.remove(video_path)
            
            if not result.get("success"):
                raise Exception(f"Erreur d'analyse: {result.get('error')}")
            
            result["series_metadata"] = {
                "title": title,
                "type": series.get("type"),
                "categories": series.get("category", []),
                "priority": series.get("priority"),
                "scan_date": datetime.now().isoformat()
            }
            
            supabase_manager.save_analysis_result(result, trailer_url, title)
            self.scanned_today.add(trailer_url)
            
            print(f"   [+] Analyse terminée - Score: {result.get('composite_score', 'N/A')}")
            result["success"] = True
            return result
            
        except Exception as e:
            error_msg = f"Erreur lors du scannage de {title}: {str(e)}"
            print(f"   [!] {error_msg}")
            supabase_manager.save_analysis_result({"success": False, "error": error_msg}, trailer_url, title)
            return {"success": False, "error": error_msg}

    def run_scheduled_scan(self, max_series: int = 50):
        """Exécute un scan programmé"""
        print(f"\n{'='*60}")
        print(f"[*] SCAN PROGRAMMÉ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        series_to_scan = self.get_priority_series(limit=max_series)
        if not series_to_scan:
            print("Aucune série à scanner aujourd'hui")
            return
        
        results = []
        for series in series_to_scan:
            result = self.scan_series(series)
            results.append(result)
            time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"[*] RAPPORT DE SCAN - Succès: {len([r for r in results if r.get('success')])} / Echecs: {len([r for r in results if not r.get('success')])}")
        print(f"{'='*60}")
        return results

def init_scheduled_scanner():
    """Initialise le scanner programmé"""
    return ScheduledScanner(
        analyzer=VideoAnalyzer(threshold=27.0),
        downloader=YouTubeDownloader()
    )

if __name__ == "__main__":
    print("Lancement du scan manuel...")
    scanner = init_scheduled_scanner()
    scanner.run_scheduled_scan(max_series=50)
