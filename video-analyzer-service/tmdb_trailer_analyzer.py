"""
Analyseur de trailers TMDB pour détecter les cuts de scène
"""

import os
import json
import requests
import time
from typing import List, Dict, Any
from analyzer import VideoAnalyzer, YouTubeDownloader
import subprocess

class TMDBTrailerAnalyzer:
    """Analyse les trailers des séries enfants depuis TMDB"""
    
    def __init__(self, tmdb_api_key: str):
        self.tmdb_api_key = tmdb_api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.analyzer = VideoAnalyzer(threshold=27.0)
        self.downloader = YouTubeDownloader()
        
    def get_show_trailers(self, tmdb_id: int) -> List[Dict[str, str]]:
        """Récupère les trailers d'une série depuis TMDB"""
        url = f"{self.base_url}/tv/{tmdb_id}/videos"
        params = {
            "api_key": self.tmdb_api_key,
            "language": "fr-FR"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            trailers = []
            for video in data.get("results", []):
                if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                    trailers.append({
                        "key": video.get("key"),
                        "name": video.get("name", "Trailer"),
                        "url": f"https://www.youtube.com/watch?v={video.get('key')}"
                    })
            
            return trailers
            
        except Exception as e:
            print(f"Erreur récupération trailers: {e}")
            return []
    
    def analyze_show(self, tmdb_id: int, show_title: str) -> Dict[str, Any]:
        """Analyse une série via ses trailers"""
        
        print(f"\n{'='*60}")
        print(f"Analyse de: {show_title} (ID: {tmdb_id})")
        print(f"{'='*60}")
        
        # 1. Récupérer les trailers
        print("→ Récupération des trailers...")
        trailers = self.get_show_trailers(tmdb_id)
        
        if not trailers:
            print("✗ Aucun trailer trouvé sur TMDB")
            return {
                "success": False,
                "error": "Aucun trailer disponible sur TMDB",
                "show_title": show_title,
                "tmdb_id": tmdb_id
            }
        
        print(f"→ {len(trailers)} trailer(s) trouvé(s)")
        
        # 2. Analyser le premier trailer (généralement le principal)
        trailer = trailers[0]
        print(f"→ Analyse du trailer: {trailer['name']}")
        print(f"→ URL: {trailer['url']}")
        
        # Télécharger (2 minutes max)
        try:
            video_path = self.downloader.download_video_snippet(
                video_url=trailer["url"],
                max_duration=120
            )
            
            if not video_path:
                print("✗ Échec du téléchargement du trailer")
                return {
                    "success": False,
                    "error": "Échec téléchargement trailer",
                    "show_title": show_title,
                    "tmdb_id": tmdb_id
                }
            
            # Analyser les cuts
            print("→ Analyse des cuts de scène...")
            result = self.analyzer.analyze_video(video_path)
            
            # Nettoyer
            try:
                os.remove(video_path)
            except:
                pass
            
            if result["success"]:
                print(f"✓ ASL: {result['average_shot_length']} secondes")
                print(f"✓ Score: {result['pacing_score']}%")
                print(f"→ Évaluation: {result['evaluation']['label']}")
                
                return {
                    "success": True,
                    "show_title": show_title,
                    "tmdb_id": tmdb_id,
                    "trailer_url": trailer["url"],
                    "video_duration": result["video_duration"],
                    "num_scenes": result["num_scenes"],
                    "average_shot_length": result["average_shot_length"],
                    "pacing_score": result["pacing_score"],
                    "evaluation": result["evaluation"],
                    "scene_details": result.get("scene_details", [])
                }
            else:
                print(f"✗ Erreur d'analyse: {result.get('error', 'Inconnue')}")
                return {
                    "success": False,
                    "error": result.get("error", "Erreur inconnue"),
                    "show_title": show_title,
                    "tmdb_id": tmdb_id
                }
                
        except Exception as e:
            print(f"✗ Erreur lors de l'analyse: {e}")
            return {
                "success": False,
                "error": str(e),
                "show_title": show_title,
                "tmdb_id": tmdb_id
            }
    
    def scan_popular_shows(self, genre_ids: List[int] = None, max_shows: int = 5) -> List[Dict[str, Any]]:
        """
        Scan les séries populaires par genre
        
        Args:
            genre_ids: Liste des IDs de genre (16 = Animation, 10751 = Family)
            max_shows: Nombre max de séries à analyser
        """
        if genre_ids is None:
            genre_ids = [16, 10751]  # Animation + Family
        
        print(f"\n{'='*60}")
        print(f"SCAN TMDB - Genre IDs: {genre_ids}")
        print(f"{'='*60}")
        
        # Récupérer les séries populaires
        url = f"{self.base_url}/discover/tv"
        params = {
            "api_key": self.tmdb_api_key,
            "language": "fr-FR",
            "with_genres": ",".join(map(str, genre_ids)),
            "sort_by": "popularity.desc",
            "page": 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            shows = data.get("results", [])[:max_shows]
            
            print(f"→ {len(shows)} séries à analyser")
            
            results = []
            for i, show in enumerate(shows, 1):
                print(f"\n[{i}/{len(shows)}] {show.get('name')}")
                
                # Pause pour éviter de surcharger
                if i > 1:
                    time.sleep(2)
                
                result = self.analyze_show(show["id"], show.get("name"))
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Erreur lors du scan: {e}")
            return []
    
    def save_to_file(self, results: List[Dict[str, Any]], filename: str = "analysis_results.json"):
        """Sauvegarde les résultats dans un fichier JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Résultats sauvegardés dans: {filename}")
    
    def display_summary(self, results: List[Dict[str, Any]]):
        """Affiche un résumé des résultats"""
        print("\n" + "="*60)
        print("RÉSUMÉ DES ANALYSES")
        print("="*60)
        
        successful = [r for r in results if r.get("success")]
        
        if not successful:
            print("Aucun résultat réussi")
            return
        
        print(f"Total analysé: {len(results)}")
        print(f"Réussi: {len(successful)}")
        
        # Top 3 les plus calmes
        print("\nTop 3 les plus calmes:")
        top_calm = sorted(successful, key=lambda x: x.get("pacing_score", 0), reverse=True)[:3]
        for i, show in enumerate(top_calm, 1):
            print(f"  {i}. {show['show_title']}: {show['pacing_score']}% (ASL: {show['average_shot_length']}s)")
        
        # Top 3 les plus stimulants
        print("\nTop 3 les plus stimulants:")
        top_exciting = sorted(successful, key=lambda x: x.get("pacing_score", 0))[:3]
        for i, show in enumerate(top_exciting, 1):
            print(f"  {i}. {show['show_title']}: {show['pacing_score']}% (ASL: {show['average_shot_length']}s)")


def main():
    """Exemple d'utilisation"""
    
    # Clés d'API
    TMDB_API_KEY = "65a5c670b9644a800c3d59f2885d4d4f"
    
    # Créer l'analyseur
    analyzer = TMDBTrailerAnalyzer(TMDB_API_KEY)
    
    # Scanner des séries populaires Animation + Family
    results = analyzer.scan_popular_shows(
        genre_ids=[16, 10751],
        max_shows=3  # Nombre limité pour le test
    )
    
    # Afficher le résumé
    analyzer.display_summary(results)
    
    # Sauvegarder les résultats
    analyzer.save_to_file(results, "tmdb_analysis_results.json")


if __name__ == "__main__":
    main()