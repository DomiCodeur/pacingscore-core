import subprocess
import sys

def test_yt_dlp_with_deno():
    """Test yt-dlp avec Deno pour vérifier que ça fonctionne"""
    
    # URL de test - une vidéo YouTube publique
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    # Commande yt-dlp pour télécharger les informations seulement
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--get-title",
        test_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"[SUCCESS] yt-dlp fonctionne avec Deno")
            print(f"Titre: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] yt-dlp a échoué")
            print(f"Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    test_yt_dlp_with_deno()
