"""
Crée une vidéo de test simple avec plusieurs scènes pour tester l'analyse
"""
import cv2
import numpy as np
import os

def create_test_video():
    """Crée une vidéo de test avec différentes scènes"""
    output_path = os.path.join("temp", "test_video.mp4")
    os.makedirs("temp", exist_ok=True)
    
    # Définir les paramètres de la vidéo
    width, height = 640, 480
    fps = 30
    duration_per_scene = 3  # 3 secondes par scène
    
    # Créer le writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Création d'une vidéo de test à {output_path}")
    
    # Scène 1: Rouge (3 secondes)
    for i in range(fps * duration_per_scene):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (0, 0, 255)  # Rouge
        out.write(frame)
    
    # Scène 2: Bleu (3 secondes)
    for i in range(fps * duration_per_scene):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (255, 0, 0)  # Bleu
        out.write(frame)
    
    # Scène 3: Vert (3 secondes)
    for i in range(fps * duration_per_scene):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (0, 255, 0)  # Vert
        out.write(frame)
    
    # Scène 4: Jaune (3 secondes)
    for i in range(fps * duration_per_scene):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (0, 255, 255)  # Jaune
        out.write(frame)
    
    out.release()
    
    print(f"Vidéo créée avec succès! Durée totale: {duration_per_scene * 4} secondes")
    print(f"Taille: {width}x{height}, FPS: {fps}")
    
    return output_path

if __name__ == "__main__":
    video_path = create_test_video()
    print(f"\nChemin du fichier: {video_path}")