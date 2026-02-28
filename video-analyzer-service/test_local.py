"""
Test de l'analyseur sur une vidéo locale
"""
from analyzer import VideoAnalyzer
import json

# Créer l'analyseur
analyzer = VideoAnalyzer(threshold=27.0)

# Analyser la vidéo de test
video_path = "temp/test_video.mp4"

print(f"Analyse de: {video_path}")
result = analyzer.analyze_video(video_path)

# Afficher les résultats
print("\n" + "="*60)
print("RÉSULTATS DE L'ANALYSE")
print("="*60)
print(json.dumps(result, indent=2, ensure_ascii=False))