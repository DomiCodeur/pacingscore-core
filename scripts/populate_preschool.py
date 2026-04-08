#!/usr/bin/env python3
"""
Populate la base de données avec des valeurs sûres pour la tranche d'âge 0-5 ans.
Récupère les informations depuis TMDB et crée des tâches d'analyse dans Supabase.
"""

import os
import requests

# Charger manuellement les variables d'environnement depuis .env à la racine
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.isfile(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# Clé TMDB peut être sous deux noms selon les configs
TMDB_KEY = os.getenv('TMDB_API_KEY') or os.getenv('tmdb.api.key')

# Liste des programmes présumés "preschool" / très jeunes enfants
# Format: (nom, media_type, tmdb_id) — media_type = 'tv' ou 'movie'
PRESCHOOL_SHOWS = [
    # TV series
    ("Peppa Pig", "tv", 12225),
    ("Bluey", "tv", 82728),
    ("Pocoyo", "tv", 2437),
    ("Dora the Explorer", "tv", 79),
    ("Thomas & Friends", "tv", 2304),
    ("Paw Patrol", "tv", 57532),
    ("Bubble Guppies", "tv", 39107),
    ("Team Umizoomi", "tv", 31623),
    ("Doc McStuffins", "tv", 46262),
    ("Mickey Mouse Clubhouse", "tv", 3934),
    ("Sesame Street", "tv", 502),
    ("The Wiggles", "tv", 34921),
    ("Blippi", "tv", 125760),
    ("Cocomelon", "tv", 114718),
    ("Little Baby Bum", "tv", 225261),
]

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def get_tv_show_details(tv_id):
    """Récupère les détails d'une série depuis TMDB."""
    url = f"https://api.themoviedb.org/3/tv/{tv_id}"
    params = {"api_key": TMDB_KEY, "language": "fr-FR"}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"[WARN] TMDB n'a pas retourné de données pour {tv_id}: {resp.status_code}")
        return None
    return resp.json()

def show_exists(supabase_headers, tmdb_id):
    """Vérifie si une analyse existe déjà dans analysis_tasks ou mollo_scores."""
    # Vérifier analysis_tasks
    url = f"{SUPABASE_URL}/rest/v1/analysis_tasks?tmdb_id=eq.{tmdb_id}&select=tmdb_id&limit=1"
    r = requests.get(url, headers=supabase_headers)
    if r.status_code == 200 and r.json():
        return True
    # Vérifier mollo_scores
    url2 = f"{SUPABASE_URL}/rest/v1/mollo_scores?tmdb_id=eq.{tmdb_id}&select=tmdb_id&limit=1"
    r2 = requests.get(url2, headers=supabase_headers)
    if r2.status_code == 200 and r2.json():
        return True
    return False

def create_analysis_task(supabase_headers, tmdb_id, media_type, tmdb_data):
    """Crée une tâche d'analyse dans Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/analysis_tasks?on_conflict=tmdb_id"
    # Construction du metadata
    title = tmdb_data.get("name") or tmdb_data.get("title") or ""
    description = tmdb_data.get("overview") or ""
    poster_path = tmdb_data.get("poster_path")
    backdrop_path = tmdb_data.get("backdrop_path")
    first_air_date = tmdb_data.get("first_air_date")
    genre_ids = tmdb_data.get("genre_ids", [])
    # Éventuellement, on pourrait ajouter plus de champs plus tard
    metadata = {
        "title": title,
        "description": description,
        "poster_path": poster_path,
        "backdrop_path": backdrop_path,
        "first_air_date": first_air_date,
        "genres": genre_ids,
        # Ces champs seront utilisés pour la classification développementale
        "age_rating": None,  # à déterminer plus tard par l'analyse
    }
    data = {
        "tmdb_id": str(tmdb_id),
        "media_type": media_type,
        "metadata": metadata
    }
    resp = requests.post(url, json=data, headers=supabase_headers)
    if resp.status_code in (200, 201, 204):
        print(f"[OK] Tâche créée pour « {title} » (TMDB: {tmdb_id})")
        return True
    else:
        # Try to decode response text safely
        try:
            err_text = resp.text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception:
            err_text = str(resp.text)
        print(f"[FAIL] Échec création pour {tmdb_id}: {resp.status_code} {err_text}")
        return False

def main():
    if not all([SUPABASE_URL, SUPABASE_KEY, TMDB_KEY]):
        print("[ERROR] Variables d'environnement manquantes. Vérifiez .env (SUPABASE_URL, SUPABASE_KEY, TMDB_API_KEY).")
        return

    # Utiliser la clé service role si disponible pour bypasser RLS
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or SUPABASE_KEY

    # Headers pour Supabase
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    created_count = 0
    skipped_count = 0

    for name, media_type, tmdb_id in PRESCHOOL_SHOWS:
        try:
            # Vérification existence
            if show_exists(headers, tmdb_id):
                print(f"[SKIP] « {name} » existe déjà dans la base.")
                skipped_count += 1
                continue

            # Récupérer les détails depuis TMDB
            details = get_tv_show_details(tmdb_id)
            if not details:
                print(f"[WARN] Pas de détails TMDB pour {name} ({tmdb_id}), ignoré.")
                skipped_count += 1
                continue

            # Créer la tâche
            if create_analysis_task(headers, tmdb_id, media_type, details):
                created_count += 1
        except Exception as e:
            print(f"[ERROR] Erreur lors du traitement de {name}: {e}")
            skipped_count += 1

    print(f"\n[INFO] Résumé : {created_count} tâches créées, {skipped_count} ignorées (déjà existantes ou erreurs).")

if __name__ == "__main__":
    main()
