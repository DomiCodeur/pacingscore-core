"""
Flask API pour l'analyse vidéo
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from analyzer import VideoAnalyzer, YouTubeDownloader
from supabase_manager import supabase_manager
from typing import Dict, Any
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration depuis les variables d'environnement
CONFIG = {
    "threshold": float(os.getenv("SCENEDETECT_THRESHOLD", 27.0)),
    "max_video_duration": int(os.getenv("MAX_VIDEO_DURATION", 120)),
    "temp_dir": os.getenv("TEMP_DIR", "./temp/videos"),
    "host": os.getenv("FLASK_HOST", "0.0.0.0"),
    "port": int(os.getenv("FLASK_PORT", 5000))
}

# Services
analyzer = VideoAnalyzer(threshold=CONFIG["threshold"])
downloader = YouTubeDownloader()

# Verbose logging
print("=" * 60)
print("[PacingScore] Video Analyzer Service")
print("=" * 60)
print(f"[Config] Temp directory: {CONFIG['temp_dir']}")
print(f"[Config] Seuil de détection: {CONFIG['threshold']}")
print(f"[Config] Durée max video: {CONFIG['max_video_duration']}s")
print(f"[Config] Server: {CONFIG['host']}:{CONFIG['port']}")
print("=" * 60)


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
        "max_duration": 120,  # Optionnel, durée max en secondes
        "analyze_motion": true,  # Optionnel, analyser le mouvement (plus lent)
        "analyze_flashes": true  # Optionnel, détecter les flashs
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
        analyze_motion = data.get("analyze_motion", False)  # Désactivé par défaut pour performance
        analyze_flashes = data.get("analyze_flashes", True)
        
        # Créer le dossier temporaire
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        # Télécharger la vidéo
        print(f"[TÉLÉCHARGEMENT] {video_url}")
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
        print(f"[ANALYSE] Démarrage de l'analyse...")
        result = analyzer.analyze_video(
            video_path, 
            analyze_motion=analyze_motion,
            analyze_flashes=analyze_flashes
        )
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(video_path)
            print(f"[NETTOYAGE] {video_path}")
        except:
            pass
        
        # Sauvegarder dans Supabase
        if result.get("success"):
            supabase_manager.save_analysis_result(result, video_url)
        
        # Retourner les résultats
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/compare", methods=["POST"])
def compare_videos():
    """
    Compare deux vidéos pour visualiser les différences de pacing
    
    Paramètres (JSON):
    {
        "video1_url": "https://www.youtube.com/watch?v=...",
        "video2_url": "https://www.youtube.com/watch?v=...",
        "name1": "Puffin Rock",
        "name2": "Cocomelon"
    }
    """
    try:
        data = request.get_json()
        
        if not all(key in data for key in ["video1_url", "video2_url"]):
            return jsonify({
                "success": False,
                "error": "Les paramètres 'video1_url' et 'video2_url' sont requis"
            }), 400
        
        video1_url = data["video1_url"]
        video2_url = data["video2_url"]
        name1 = data.get("name1", "Vidéo 1")
        name2 = data.get("name2", "Vidéo 2")
        
        # Télécharger les deux vidéos
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        print(f"[TÉLÉCHARGEMENT] 1: {name1}")
        video1_path = downloader.download_video_snippet(
            video_url=video1_url,
            output_dir=CONFIG["temp_dir"],
            max_duration=120
        )
        
        print(f"[TÉLÉCHARGEMENT] 2: {name2}")
        video2_path = downloader.download_video_snippet(
            video_url=video2_url,
            output_dir=CONFIG["temp_dir"],
            max_duration=120
        )
        
        if not video1_path or not video2_path:
            return jsonify({
                "success": False,
                "error": "Échec du téléchargement d'une des vidéos"
            }), 500
        
        # Comparer les vidéos
        result = analyzer.analyze_comparison(video1_path, video2_path, name1, name2)
        
        # Nettoyer
        try:
            if video1_path and os.path.exists(video1_path):
                os.remove(video1_path)
            if video2_path and os.path.exists(video2_path):
                os.remove(video2_path)
        except:
            pass
        
        # Sauvegarder les analyses individuelles
        if result.get("success"):
            supabase_manager.save_analysis_result(
                result["comparison"]["video1"], 
                video1_url, 
                name1
            )
            supabase_manager.save_analysis_result(
                result["comparison"]["video2"], 
                video2_url, 
                name2
            )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/analyze-trailer", methods=["POST"])
def analyze_trailer():
    """
    Analyse un trailer et le compare à un épisode réel (si disponible)
    
    Paramètres (JSON):
    {
        "trailer_url": "https://www.youtube.com/watch?v=...",
        "episode_url": "https://www.youtube.com/watch?v=...",  # Optionnel
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
        episode_url = data.get("episode_url")
        series_title = data.get("series_title", "Série inconnue")
        
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        print(f"[TRAILER] Analyse de la bande-annonce de: {series_title}")
        
        # Utiliser l'analyse trailer vs épisode
        result = analyzer.analyze_trailer_vs_episode(
            trailer_url=trailer_url,
            episode_url=episode_url
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/history", methods=["GET"])
def get_history():
    """
    Récupère l'historique des analyses depuis Supabase
    """
    limit = request.args.get('limit', 10, type=int)
    
    # Si Supabase n'est pas configuré, retourner une réponse mock
    if not supabase_manager.client:
        return jsonify({
            "success": True,
            "data": [
                {
                    "series_title": "Puffin Rock (mock)",
                    "pacing_score": 65,
                    "composite_score": 62,
                    "average_shot_length": 8.5,
                    "evaluation_label": "CALME",
                    "created_at": "2026-02-26T16:30:00"
                },
                {
                    "series_title": "Cocomelon (mock)",
                    "pacing_score": 25,
                    "composite_score": 20,
                    "average_shot_length": 4.2,
                    "evaluation_label": "STIMULANT",
                    "created_at": "2026-02-26T16:25:00"
                }
            ]
        })
    
    try:
        history = supabase_manager.get_analysis_history(limit=limit)
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/")
def serve_ui():
    """
    Sert l'interface web
    """
    return app.send_static_file("index.html")


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
    # Pour éviter les problèmes avec Waitress sur Windows, on utilise Flask en mode debug
    print("[SERVEUR] Démarrage avec Flask (développement)")
    print(f"[SERVEUR] URL: http://{CONFIG['host']}:{CONFIG['port']}")
    print(f"[SERVEUR] Interface: http://{CONFIG['host']}:{CONFIG['port']}")
    print("=" * 60)
    app.run(host=CONFIG["host"], port=CONFIG["port"], debug=True, use_reloader=False)