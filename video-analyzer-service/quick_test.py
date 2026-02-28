"""
Test rapide de l'analyseur (sans serveur HTTP)
"""
from analyzer import VideoAnalyzer, YouTubeDownloader
import os

print("=" * 60)
print("TEST RAPIDE PacingScore")
print("=" * 60)

# 1. Créer une vidéo de test simple
print("\n1. Création d'une vidéo de test...")
import cv2
import numpy as np

os.makedirs("temp", exist_ok=True)
test_video_path = "temp/test_simple.mp4"

# Créer une vidéo avec plusieurs scènes
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(test_video_path, fourcc, 10, (320, 240))

# Scène 1: Rouge (2 secondes)
for _ in range(20):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (0, 0, 255)
    out.write(frame)

# Scène 2: Bleu (2 secondes)
for _ in range(20):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (255, 0, 0)
    out.write(frame)

# Scène 3: Vert (2 secondes)
for _ in range(20):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:, :] = (0, 255, 0)
    out.write(frame)

out.release()
print(f"   Vidéo créée: {test_video_path}")

# 2. Analyser la vidéo
print("\n2. Analyse de la vidéo...")
analyzer = VideoAnalyzer(threshold=27.0)

result = analyzer.analyze_video(test_video_path, analyze_motion=False, analyze_flashes=True)

if result.get("success"):
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    print(f"Durée vidéo: {result['video_duration']} secondes")
    print(f"Scènes détectées: {result['num_scenes']}")
    print(f"ASL (Average Shot Length): {result['average_shot_length']} secondes")
    print(f"Score de pacing: {result['pacing_score']}")
    print(f"Score composite: {result['composite_score']}")
    print(f"Évaluation: {result['composite_evaluation']['label']}")
    print(f"Description: {result['composite_evaluation']['description']}")
    
    print("\nDétection des flashs:")
    flash = result.get('flash_analysis', {})
    print(f"  - Frames noirs: {flash.get('black_frames', 0)}")
    print(f"  - Flashs détectés: {flash.get('flashes', 0)}")
    print(f"  - Intensité: {flash.get('intensity', 0)}/100")
    
    print("\n" + "=" * 60)
    print("TEST REUSSI")
    print("=" * 60)
else:
    print(f"\n❌ ERREUR: {result.get('error')}")

# 3. Tester yt-dlp (téléchargement YouTube)
print("\n3. Test yt-dlp...")
try:
    downloader = YouTubeDownloader()
    # Note: On ne télécharge pas vraiment pour éviter les problèmes
    print("   yt-dlp importé avec succès")
    print("   Fonctionne en mode Python direct")
except Exception as e:
    print(f"   ⚠️  Erreur: {e}")

print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)