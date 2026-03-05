import re

filepath = "analyze_dailymotion_videos.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Ajouter la fonction download_video_snippet avant analyze_video
old_analyze_start = r"""def analyze_video(video: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Analyse une video Dailymotion

    Args:
        video: Dictionnaire avec les informations de la video

    Returns:
        Dictionnaire avec les resultats
    \"\"\""""

new_analyze_start = r"""def download_video_snippet(video_url: str, max_duration: int = 60, force_format: bool = False) -> Optional[str]:
    \"\"\"Telecharge un extrait d'une video

    Args:
        video_url: URL de la video
        max_duration: Duree maximale en secondes
        force_format: Forcer un format different

    Returns:
        Chemin du fichier telecharge ou None
    \"\"\"

    # Creer un nom de fichier unique
    temp_dir = tempfile.gettempdir()
    video_id = video_url.split('/')[-1]
    output_path = os.path.join(temp_dir, f"video_{video_id}.mp4")

    # Construire la commande yt-dlp avec gestion d'erreur
    if force_format:
        # Essayer avec liste de formats (plus permissif)
        cmd = [\"yt-dlp\", \"--format\", \"best[height<=480]/best\", \"--output\", output_path, \"--impersonate\", \"Chrome-99\", \"--quiet\", \"--no-warnings\", \"--no-check-certificate\", video_url]
    else:
        # Format original
        cmd = [\"yt-dlp\", \"--format\", \"bestvideo[height<=480][ext=mp4]/best[height<=480]\", \"--output\", output_path, \"--impersonate\", \"Chrome-99\", \"--quiet\", \"--no-warnings\", \"--no-check-certificate\", video_url]

    try:
        # Executer la commande
        result = subprocess.run(cmd, check=True, capture_output=True, timeout=60)

        # Verifier si le fichier existe
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            print(f"   [ERROR] Fichier vide ou inexistant: {output_path}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Erreur yt-dlp: {e}")
        print(e.stderr.decode(\\\'utf-8\\\', errors=\\\'replace\\\'))
        return None
    except subprocess.TimeoutExpired:
        print(f"   [ERROR] Timeout yt-dlp")
        return None
    except Exception as e:
        print(f"   [ERROR] Erreur inattendue: {e}")
        return None


def analyze_video(video: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"Analyse une video Dailymotion

    Args:
        video: Dictionnaire avec les informations de la video

    Returns:
        Dictionnaire avec les resultats
    \"\"\""""

content = content.replace(old_analyze_start, new_analyze_start)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Fichier modifié avec succès !")
