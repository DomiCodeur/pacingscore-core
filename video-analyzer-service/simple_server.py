#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serveur Flask simple pour PacingScore
Lance le serveur et teste l'interface web
"""
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, '.')

# Import Flask et les dépendances
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "temp_dir": "./temp/videos",
    "threshold": 27.0
}

# Créer l'application Flask
app = Flask(__name__, static_folder='static')
CORS(app)

# Importer les modules après avoir créé l'app
from analyzer import VideoAnalyzer, YouTubeDownloader
from supabase_manager import supabase_manager

# Initialiser les services
analyzer = VideoAnalyzer(threshold=CONFIG["threshold"])
downloader = YouTubeDownloader()

# Créer le dossier temporaire
os.makedirs(CONFIG["temp_dir"], exist_ok=True)

print("=" * 60)
print("PacingScore Video Analyzer Service")
print("=" * 60)
print(f"Temp directory: {CONFIG['temp_dir']}")
print(f"Seuil de détection: {CONFIG['threshold']}")
print(f"Server: http://{CONFIG['host']}:{CONFIG['port']}")
print("=" * 60)

# Routes API
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
    """Analyse une vidéo YouTube"""
    try:
        data = request.get_json()
        
        if not data or "video_url" not in data:
            return jsonify({
                "success": False,
                "error": "Le paramètre 'video_url' est requis"
            }), 400
        
        video_url = data["video_url"]
        max_duration = data.get("max_duration", 120)
        analyze_motion = data.get("analyze_motion", False)
        analyze_flashes = data.get("analyze_flashes", True)
        
        print(f"[TELECHARGEMENT] {video_url}")
        
        # Télécharger la vidéo
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
        
        print(f"[ANALYSE] Démarrage de l'analyse...")
        
        # Analyser la vidéo
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
        
        print(f"[RESULTAT] Score: {result.get('composite_score', 'N/A')}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/history", methods=["GET"])
def get_history():
    """Récupère l'historique des analyses"""
    limit = request.args.get('limit', 10, type=int)
    
    if not supabase_manager.client:
        return jsonify({
            "success": True,
            "data": [
                {
                    "series_title": "Puffin Rock (test)",
                    "pacing_score": 65,
                    "composite_score": 62,
                    "average_shot_length": 8.5,
                    "evaluation_label": "CALME",
                    "created_at": "2026-02-26T16:30:00"
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
    """Sert l'interface web"""
    return send_from_directory('static', 'index.html')

@app.route("/compare", methods=["POST"])
def compare_videos():
    """Compare deux vidéos"""
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
        
        # Télécharger les vidéos
        os.makedirs(CONFIG["temp_dir"], exist_ok=True)
        
        print(f"[TELECHARGEMENT] 1: {name1}")
        video1_path = downloader.download_video_snippet(
            video_url=video1_url,
            output_dir=CONFIG["temp_dir"],
            max_duration=120
        )
        
        print(f"[TELECHARGEMENT] 2: {name2}")
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

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Démarrage du serveur PacingScore")
    print("=" * 60)
    print(f"Interface web: http://localhost:5000")
    print(f"API: http://localhost:5000/analyze")
    print("=" * 60)
    
    app.run(
        host=CONFIG["host"],
        port=CONFIG["port"],
        debug=True,
        use_reloader=False
    )