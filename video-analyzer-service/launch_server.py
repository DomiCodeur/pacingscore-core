#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de lancement direct du serveur Flask pour tester l'API
"""
import sys
import time
import requests
from threading import Thread

# Ajouter le répertoire courant au path
sys.path.insert(0, '.')

from api import app
from analyzer import VideoAnalyzer, YouTubeDownloader

def test_api():
    """Test l'API avec une vidéo YouTube simple"""
    print("=" * 60)
    print("TEST DE L'API")
    print("=" * 60)
    
    # Attendre que le serveur soit prêt
    print("Attente du démarrage du serveur...")
    for i in range(20):
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print("✓ Serveur prêt!")
                break
        except:
            pass
        
        if i == 19:
            print("✗ Serveur non démarré après 20 tentatives")
            return
        
        time.sleep(2)
    
    # Test health check
    print("\nTest health check...")
    try:
        r = requests.get("http://localhost:5000/health", timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test analyse directe (sans passer par l'API)
    print("\n" + "=" * 60)
    print("TEST DIRECT DE L'ANALYSEUR")
    print("=" * 60)
    
    analyzer = VideoAnalyzer(threshold=27.0)
    
    # Créer une vidéo de test
    import cv2
    import numpy as np
    import os
    
    os.makedirs("temp", exist_ok=True)
    test_video = "temp/test_server.mp4"
    
    # Créer une vidéo simple
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video, fourcc, 10, (320, 240))
    
    for color in [(0, 0, 255), (255, 0, 0), (0, 255, 0)]:  # Rouge, Bleu, Vert
        for _ in range(10):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            frame[:, :] = color
            out.write(frame)
    
    out.release()
    print(f"Vidéo de test créée: {test_video}")
    
    # Analyser
    result = analyzer.analyze_video(test_video, analyze_motion=False, analyze_flashes=True)
    
    if result.get("success"):
        print("\n" + "=" * 60)
        print("RÉSULTATS DE L'ANALYSE")
        print("=" * 60)
        print(f"Durée vidéo: {result['video_duration']} secondes")
        print(f"Scènes: {result['num_scenes']}")
        print(f"ASL: {result['average_shot_length']} secondes")
        print(f"Score composite: {result['composite_score']}")
        print(f"Évaluation: {result['composite_evaluation']['label']}")
        print(f"Flashs détectés: {result['flash_analysis']['flashes']}")
    else:
        print(f"\nErreur: {result.get('error')}")

def run_server():
    """Lance le serveur Flask"""
    print("=" * 60)
    print("DÉMARRAGE DU SERVEUR FLASK")
    print("=" * 60)
    print("URL: http://localhost:5000")
    print("Interface: http://localhost:5000")
    print("=" * 60)
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )

if __name__ == "__main__":
    # Lancer le serveur dans un thread
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Attendre un peu et lancer les tests
    time.sleep(5)
    test_api()
    
    # Garder le programme en vie
    print("\n" + "=" * 60)
    print("Serveur en cours d'exécution...")
    print("Appuyez sur CTRL+C pour arrêter")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        sys.exit(0)