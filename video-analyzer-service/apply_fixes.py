import re

filepath = "analyze_dailymotion_videos.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Ajouter force_format à la signature
content = content.replace(
    "def download_video_snippet(video_url: str, max_duration: int = 60) -> Optional[str]:",
    "def download_video_snippet(video_url: str, max_duration: int = 60, force_format: bool = False) -> Optional[str]:"
)

# 2. Remplacer la commande yt-dlp (ajouter if force_format)
old_cmd = '''    cmd = ["yt-dlp", "--format", "bestvideo[height<=480][ext=mp4]/best[height<=480]", "--output", output_path, "--impersonate", "Chrome-99", "--quiet", "--no-warnings", video_url]'''

new_cmd = '''    if force_format:
        cmd = ["yt-dlp", "--format", "best[height<=480]/best", "--output", output_path, "--impersonate", "Chrome-99", "--quiet", "--no-warnings", "--no-check-certificate", video_url]
    else:
        cmd = ["yt-dlp", "--format", "bestvideo[height<=480][ext=mp4]/best[height<=480]", "--output", output_path, "--impersonate", "Chrome-99", "--quiet", "--no-warnings", "--no-check-certificate", video_url]'''

content = content.replace(old_cmd, new_cmd)

# 3. Remplacer subprocess.run + ajouter gestion erreurs
old_run = '''    try:
        # Executer la commande
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
        
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Erreur yt-dlp: {e}")
        print(e.stderr.decode('utf-8', errors='replace'))
        return None'''

new_run = '''    try:
        result = subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            print(f"   [ERROR] Fichier vide ou inexistant: {output_path}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Erreur yt-dlp: {e}")
        print(e.stderr.decode('utf-8', errors='replace'))
        return None
    except subprocess.TimeoutExpired:
        print(f"   [ERROR] Timeout yt-dlp")
        return None
    except Exception as e:
        print(f"   [ERROR] Erreur inattendue: {e}")
        return None'''

content = content.replace(old_run, new_run)

# 4. Remplacer l'appel à download_video_snippet dans analyze_video
old_download_call = '''        print("   [DOWNLOAD] Telechargement...")
        video_path = download_video_snippet(video_url, max_duration=60)
        if not video_path:
            return {"success": False, "error": "Echec telechargement"}
        
        print(f"   [OK] Video telechargee: {video_path}")'''

new_download_call = '''        print("   [DOWNLOAD] Telechargement...")
        
        video_path = None
        try:
            video_path = download_video_snippet(video_url, max_duration=60)
            if video_path:
                print(f"   [OK] Video telechargee (yt-dlp): {video_path}")
        except Exception as e1:
            print(f"   [WARN] yt-dlp a echoue: {e1}")
            try:
                print("   [RETRY] Essai autre format...")
                video_path = download_video_snippet(video_url, max_duration=60, force_format=True)
                if video_path:
                    print(f"   [OK] Video telechargee (retry): {video_path}")
            except Exception as e2:
                print(f"   [ERROR] Telechargement echoue: {e2}")
                return {"success": False, "error": "Echec telechargement (formats)"}
        
        if not video_path or not os.path.exists(video_path):
            return {"success": False, "error": "Echec telechargement (fichier)"}'''

content = content.replace(old_download_call, new_download_call)

# 5. Modifier la signature de save_results_to_supabase
content = content.replace(
    "def save_results_to_supabase(video_id: str, result: Dict[str, Any]) -> bool:",
    "def save_results_to_supabase(video_id: str, result: Dict[str, Any], video_url: str = None, series_title: str = None, video_key: str = None, tmdb_id: int = None) -> bool:"
)

# 6. Ajouter l'insertion video_analyses dans save_results_to_supabase (avant le return True)
old_save_end = '''        except Exception as e:
            print(f"   [ERROR] Erreur sauvegarde Supabase: {e}")
            return False

    return True'''

new_save_end = '''        except Exception as e:
            print(f"   [ERROR] Erreur mise a jour analysis_results: {e}")
            return False

    # 2. Si analyse reussie, inserer dans video_analyses (avec verification doublons)
    if result.get("success"):
        success = manager.save_analysis_result(
            result=result,
            video_url=video_url or "",
            series_title=series_title,
            tmdb_id=tmdb_id,
            video_key=video_key
        )
        if success:
            print(f"   [OK] Resultat sauvegarde dans video_analyses")
        else:
            print(f"   [WARN] Echec sauvegarde video_analyses (deja existant ?)")

    return True'''

content = content.replace(old_save_end, new_save_end)

# 7. Remplacer l'appel dans main()
old_call = '''        # Sauvegarder les resultats
        if save_results_to_supabase(video["id"], result):
            success_count += 1
            print(f"[OK] Video {i} terminee avec succes")
        else:
            print(f"[ERROR] Video {i} echec sauvegarde")'''

new_call = '''        # Sauvegarder les resultats avec parametres supplementaires
        video_url = video.get("video_url")
        series_title = video.get("series_title")
        video_key = video.get("video_key")
        tmdb_id = video.get("tmdb_id")
        if save_results_to_supabase(video["id"], result, video_url=video_url, series_title=series_title, video_key=video_key, tmdb_id=tmdb_id):
            success_count += 1
            print(f"[OK] Video {i} terminee avec succes")
        else:
            print(f"[ERROR] Video {i} echec sauvegarde")'''

content = content.replace(old_call, new_call)

# Écrire le fichier modifié
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixes appliques avec succes !")
