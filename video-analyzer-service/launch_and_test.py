#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lance le serveur et teste l'interface web
"""
import subprocess
import time
import requests
import sys
import os

def start_server():
    """Démarre le serveur Flask dans un subprocess"""
    print("=" * 60)
    print("Démarrage du serveur PacingScore")
    print("=" * 60)
    
    # Démarrer le serveur
    process = subprocess.Popen(
        [sys.executable, "simple_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=os.getcwd()
    )
    
    return process

def test_server(process, timeout=30):
    """Teste si le serveur est prêt"""
    print("\nAttente du démarrage du serveur...")
    
    for i in range(timeout):
        # Lire la sortie du processus
        line = process.stdout.readline()
        if line:
            print(f"  {line.strip()}")
        
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print(f"\n[SUCCES] Serveur prêt après {i+1} secondes!")
                return True
        except:
            pass
        
        time.sleep(1)
    
    print("\n[ERREUR] Serveur non démarré après {timeout} secondes")
    return False

def test_interface():
    """Teste l'interface web"""
    print("\n" + "=" * 60)
    print("TEST INTERFACE WEB")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200 and "PacingScore" in response.text:
            print("[SUCCES] Interface web accessible")
            print("URL: http://localhost:5000")
            
            # Sauvegarder le HTML
            with open("temp_interface.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("HTML sauvegardé dans: temp_interface.html")
            
            return True
        else:
            print("[ERREUR] Interface web non détectée")
            return False
    except Exception as e:
        print(f"[ERREUR] Impossible d'accéder: {e}")
        return False

def test_api():
    """Teste l'API"""
    print("\n" + "=" * 60)
    print("TEST API")
    print("=" * 60)
    
    try:
        # Test health check
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"[SUCCES] Health check: {response.json()}")
        
        # Test analyse directe (sans vidéo YouTube)
        print("\nTest d'analyse rapide...")
        
        # On va tester l'analyseur directement
        from analyzer import VideoAnalyzer
        import cv2
        import numpy as np
        
        # Créer une vidéo de test
        os.makedirs("temp", exist_ok=True)
        test_video = "temp/test_server.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video, fourcc, 10, (320, 240))
        
        for color in [(0, 0, 255), (255, 0, 0), (0, 255, 0)]:
            for _ in range(10):
                frame = np.zeros((240, 320, 3), dtype=np.uint8)
                frame[:, :] = color
                out.write(frame)
        
        out.release()
        
        # Analyser
        analyzer = VideoAnalyzer(threshold=27.0)
        result = analyzer.analyze_video(test_video, analyze_motion=False, analyze_flashes=True)
        
        if result.get("success"):
            print(f"[SUCCES] Analyse directe réussie")
            print(f"  Score: {result['composite_score']}")
            print(f"  ASL: {result['average_shot_length']}s")
            print(f"  Évaluation: {result['composite_evaluation']['label']}")
            
            # Sauvegarder le résultat
            import json
            with open("temp_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Résultat sauvegardé dans: temp_result.json")
            
            return True
        else:
            print(f"[ERREUR] Analyse échouée: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"[ERREUR] Erreur API: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("PacingScore - Lancement et Tests")
    print("=" * 60)
    
    # 1. Démarrer le serveur
    server_process = start_server()
    
    # 2. Attendre que le serveur soit prêt
    if not test_server(server_process, timeout=30):
        print("\n[ERREUR] Le serveur n'a pas démarré correctement")
        server_process.kill()
        return 1
    
    # 3. Tester l'interface web
    interface_ok = test_interface()
    
    # 4. Tester l'API
    api_ok = test_api()
    
    # 5. Résumé
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)
    print(f"Interface web: {'SUCCES' if interface_ok else 'ECHEC'}")
    print(f"API: {'SUCCES' if api_ok else 'ECHEC'}")
    
    if interface_ok and api_ok:
        print("\nTout fonctionne!")
        print("URL: http://localhost:5000")
        print("\nLe serveur continue de tourner...")
        print("Appuyez sur CTRL+C pour arrêter")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            server_process.kill()
            return 0
    else:
        print("\nDes tests ont échoué")
        server_process.kill()
        return 1

if __name__ == "__main__":
    sys.exit(main())