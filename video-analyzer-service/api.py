"""
Flask API pour l'analyse vidéo
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from analyzer import VideoAnalyzer, YouTubeDownloader
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    "threshold": 27.0,  # Sensibilité de détection
    "max_video_duration": 120,  # 2 minutes max
    "temp_dir": "./temp/videos",
    "host": "0.0.0.0",
    "port": 5000
}

# Services
analyzer = VideoAnalyzer(threshold=CONFIG["threshold"])
downloader = YouTubeDownloader()


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de vérification de santé"""
    return jsonify({
        "status": "healthy",
        "service": "pacing-score-video-analyzer",
        "version": "1.0.0"
    })


@app.route("/analyze", methods=["POST"])
def analyze_video():
    """
    Analyse une vidéo YouTube pour détecter les cuts de scène
    
    Paramètres (JSON):
    {
        "video_url": "https://www.youtube.com/watch?v=...",
        "max_duration": 120  # Optionnel, durée max en secondes
    }
    """
    try:
        # Récupérer les paramètres
        data = request.get_json()
        
        if not data or "video_url" not in data:
            return jsonify({
                "success": False,
                "error": "Le paramètre 'video_url' est requis"
            }), 400
        
        video_url = data["video_url"]
        max_duration = data.get("max_duration", CONFIG["max_video_duration"])
        
        # Créer le dossier temporaire
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        # Télécharger la vidéo
        print(f"Téléchargement de: {video_url}")
        video_path = downloader.download_video_snippet(
            video_url=video_url,
            output_dir=CONFIG["temp_dir"],
            max_duration=max_duration
        )
        
        if not video_path:
            return jsonify({
                "success": False,
                "error": "Échec du téléchargement"
            }), 500
        
        # Analyser la vidéo
        print(f"Analyse de: {video_path}")
        result = analyzer.analyze_video(video_path)
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(video_path)
            print(f"Nettoyé: {video_path}")
        except:
            pass
        
        # Retourner les résultats
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/analyze-batch", methods=["POST"])
def analyze_batch():
    """
    Analyse plusieurs vidéos en batch
    
    Paramètres (JSON):
    {
        "videos": [
            {"url": "...", "title": "..."},
            {"url": "...", "title": "..."}
        ],
        "max_duration": 120
    }
    """
    try:
        data = request.get_json()
        
        if not data or "videos" not in data:
            return jsonify({
                "success": False,
                "error": "Le paramètre 'videos' est requis"
            }), 400
        
        videos = data["videos"]
        max_duration = data.get("max_duration", CONFIG["max_video_duration"])
        results = []
        
        for video_info in videos:
            video_url = video_info.get("url")
            video_title = video_info.get("title", "Inconnu")
            
            try:
                # Télécharger et analyser
                video_path = downloader.download_video_snippet(
                    video_url=video_url,
                    output_dir=CONFIG["temp_dir"],
                    max_duration=max_duration
                )
                
                if video_path:
                    result = analyzer.analyze_video(video_path)
                    result["video_title"] = video_title
                    result["video_url"] = video_url
                    results.append(result)
                    
                    # Nettoyer
                    os.remove(video_path)
                    
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "video_title": video_title,
                    "video_url": video_url
                })
        
        return jsonify({
            "success": True,
            "total_analyzed": len(results),
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/analyze-from-trailer", methods=["POST"])
def analyze_from_trailer():
    """
    Analyse une série via sa bande-annonce YouTube
    Stratégie recommandée pour éviter de télécharger de longues vidéos
    
    Paramètres (JSON):
    {
        "trailer_url": "https://www.youtube.com/watch?v=...",
        "series_title": "Nom de la série"
    }
    """
    try:
        data = request.get_json()
        
        if not data or "trailer_url" not in data:
            return jsonify({
                "success": False,
                "error": "Le paramètre 'trailer_url' est requis"
            }), 400
        
        trailer_url = data["trailer_url"]
        series_title = data.get("series_title", "Série inconnue")
        
        print(f"Analyse de la bande-annonce de: {series_title}")
        
        # Télécharger les 2 premières minutes de la bande-annonce
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        video_path = downloader.download_video_snippet(
            video_url=trailer_url,
            output_dir=CONFIG["temp_dir"],
            max_duration=120  # 2 minutes
        )
        
        if not video_path:
            return jsonify({
                "success": False,
                "error": "Échec du téléchargement de la bande-annonce"
            }), 500
        
        # Analyser
        result = analyzer.analyze_video(video_path)
        
        # Ajouter les informations de la série
        result["series_title"] = series_title
        result["trailer_url"] = trailer_url
        
        # Nettoyer
        os.remove(video_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("PacingScore Video Analyzer Service")
    print("=" * 60)
    print(f"Démarrage sur {CONFIG['host']}:{CONFIG['port']}")
    print(f"Temp directory: {CONFIG['temp_dir']}")
    print(f"Seuil de détection: {CONFIG['threshold']}")
    print("=" * 60)
    
    app.run(host=CONFIG["host"], port=CONFIG["port"], debug=True)