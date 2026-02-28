#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple de PacingScore sans serveur HTTP
"""
import sys
sys.path.insert(0, '.')

from analyzer import VideoAnalyzer, YouTubeDownloader
import cv2
import numpy as np
import os
import json

print("=" * 60)
print("TEST SIMPLE PacingScore")
print("=" * 60)

# 1. Créer une vidéo de test
print("\n1. Création d'une vidéo de test...")
os.makedirs("temp", exist_ok=True)
test_video = "temp/test_simple2.mp4"

# Créer une vidéo avec des scènes rapides
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(test_video, fourcc, 10, (320, 240))

# Scène 1: Rouge (1 seconde = 10 frames)
for _ in range(10):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (0, 0, 255)  # Rouge
    out.write(frame)

# Scène 2: Bleu (1 seconde = 10 frames)
for _ in range(10):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (255, 0, 0)  # Bleu
    out.write(frame)

# Scène 3: Vert (1 seconde = 10 frames)
for _ in range(10):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (0, 255, 0)  # Vert
    out.write(frame)

# Scène 4: Jaune (1 seconde = 10 frames)
for _ in range(10):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (0, 255, 255)  # Jaune
    out.write(frame)

# Scène 5: Magenta (2 secondes = 20 frames)
for _ in range(20):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (255, 0, 255)  # Magenta
    out.write(frame)

out.release()
print(f"   Vidéo créée: {test_video}")
print(f"   Durée: 6 secondes")
print(f"   Scènes attendues: 5")

# 2. Analyser la vidéo
print("\n2. Analyse de la vidéo...")
analyzer = VideoAnalyzer(threshold=27.0)

result = analyzer.analyze_video(
    test_video, 
    analyze_motion=False,  # On désactive pour la vitesse
    analyze_flashes=True
)

# 3. Afficher les résultats
print("\n" + "=" * 60)
print("RÉSULTATS")
print("=" * 60)

if result.get("success"):
    print("[SUCCES] Analyse reussie")
    print(f"\nMetriques de base:")
    print(f"  Duree video: {result['video_duration']} secondes")
    print(f"  Scenes detectees: {result['num_scenes']}")
    print(f"  ASL: {result['average_shot_length']} secondes/plan")
    
    print(f"\nScores:")
    print(f"  Score historique: {result['pacing_score']}")
    print(f"  Score composite: {result['composite_score']:.2f}")
    
    print(f"\nEvaluation:")
    eval = result['composite_evaluation']
    print(f"  Label: {eval['label']}")
    print(f"  Description: {eval['description']}")
    print(f"  Couleur: {eval['color']}")
    
    print(f"\nFlashs:")
    flash = result['flash_analysis']
    print(f"  Flashs detectes: {flash['flashes']}")
    print(f"  Frames noirs: {flash['black_frames']}")
    print(f"  Intensite: {flash['intensity']}/100")
    
    print(f"\nDetection des scenes:")
    for i, scene in enumerate(result['scene_details']):
        print(f"  Scene {i+1}: {scene['start']:.1f}s a {scene['end']:.1f}s ({scene['duration']:.1f}s)")
    
    # Sauvegarde du résultat
    with open("temp/resultat_test.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n[SUCCES] Resultat sauvegarde dans: temp/resultat_test.json")
    
else:
    print(f"[ERREUR] {result.get('error')}")

# 4. Tester yt-dlp
print("\n" + "=" * 60)
print("TEST yt-dlp")
print("=" * 60)
try:
    downloader = YouTubeDownloader()
    print("[SUCCES] yt-dlp importe avec succes")
    print("[SUCCES] Fonctionne en mode Python direct")
    print("[SUCCES] Pas besoin de l'executable .exe")
except Exception as e:
    print(f"[ERREUR] Erreur yt-dlp: {e}")

print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)