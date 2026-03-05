#!/usr/bin/env python3
"""
Mollo Scan 6+ - Scanner et classer les vidéos pour enfants 6+ ans

Ce script:
1. Vérifie si la colonne age_group existe dans la table analysis_results
2. Si elle n'existe pas, guide l'utilisateur pour l'ajouter manuellement
3. Scanne les vidéos existantes et les classe par catégorie d'âge
4. Ajoute des vidéos adaptées aux 6+ ans si nécessaire
"""

import os
import sys
import requests
from supabase import create_client
from dotenv import load_dotenv

# Configuration
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
tmdb_key = os.getenv("TMDB_API_KEY")
supabase = create_client(url, key)

def check_age_rating_column():
    """Vérifie si la colonne age_rating existe dans video_analyses"""
    try:
        result = supabase.table("video_analyses").select("age_rating").limit(1).execute()
        return True
    except Exception as e:
        if "column video_analyses.age_rating does not exist" in str(e):
            return False
        else:
            print(f"Erreur inattendue: {e}")
            return False

def add_age_rating_column_manually():
    """Affiche les instructions pour ajouter la colonne manuellement"""
    print("\n" + "="*60)
    print("INSTRUCTIONS POUR AJOUTER LA COLONNE age_rating")
    print("="*60)
    print("\n1. Connectez-vous à votre tableau de bord Supabase")
    print("2. Allez dans 'SQL Editor' (Éditeur SQL)")
    print("3. Exécutez la requête suivante:")
    print()
    print("   ALTER TABLE video_analyses ADD COLUMN IF NOT EXISTS age_rating VARCHAR(10);")
    print()
    print("4. Cliquez sur 'Run' (Exécuter)")
    print("5. Une fois la colonne ajoutée, relancez ce script")
    print("\n" + "="*60)

def get_tmdb_age_rating(tmdb_id, title):
    """Récupère la classification par âge depuis TMDB"""
    if not tmdb_id:
        # Classification par défaut basée sur le titre
        if "peppa pig" in title.lower() or "caillou" in title.lower() or "pocoyo" in title.lower():
            return "0+"
        elif "bluey" in title.lower() or "paw patrol" in title.lower():
            return "3+"
        elif "spiderman" in title.lower() or "avengers" in title.lower():
            return "10+"
        else:
            return "6+"  # Valeur par défaut pour les vidéos non classées
    
    try:
        # Récupérer les informations de classification
        r = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}/content_ratings?api_key={tmdb_key}")
        data = r.json()
        
        # Chercher la classification française
        for rating in data.get('results', []):
            if rating.get('iso_3166_1') == 'FR':
                return f"{rating.get('rating')}+"
        
        # Si pas de classification française, utiliser la classification US
        for rating in data.get('results', []):
            if rating.get('iso_3166_1') == 'US':
                # Convertir la classification US en format européen
                us_rating = rating.get('rating')
                if us_rating == 'TV-Y': return '0+'
                elif us_rating == 'TV-Y7': return '3+'
                elif us_rating == 'TV-G': return '6+'
                elif us_rating == 'TV-PG': return '10+'
                elif us_rating == 'TV-14': return '12+'
                elif us_rating == 'TV-MA': return '16+'
        
        # Classification par défaut
        return "6+"
        
    except Exception as e:
        print(f"Erreur récupération classification TMDB pour {title}: {e}")
        return "6+"

def classify_existing_videos():
    """Classe les vidéos existantes par catégorie d'âge"""
    print("\nClassification des vidéos existantes...")
    
    # Récupérer toutes les vidéos depuis video_analyses
    result = supabase.table("video_analyses").select("*").execute()
    videos = result.data
    
    if not videos:
        print("Aucune vidéo trouvée dans la base de données.")
        return
    
    updated_count = 0
    
    for video in videos:
        video_id = video['id']
        title = video.get('title', '')
        
        # Extraire tmdb_id si disponible
        tmdb_data = video.get('tmdb_data')
        tmdb_id = None
        if isinstance(tmdb_data, dict):
            tmdb_id = tmdb_data.get('id')
        
        current_age_rating = video.get('age_rating')
        
        # Si la vidéo a déjà une catégorie d'âge, passer à la suivante
        if current_age_rating:
            continue
        
        # Déterminer la catégorie d'âge
        age_rating = get_tmdb_age_rating(tmdb_id, title)
        
        # Mettre à jour la vidéo avec la catégorie d'âge
        try:
            update_result = supabase.table("video_analyses").update({"age_rating": age_rating}).eq("id", video_id).execute()
            print(f"  OK {title} -> {age_rating}")
            updated_count += 1
        except Exception as e:
            print(f"  ERREUR mise à jour {title}: {e}")
    
    print(f"\n{updated_count} vidéos classées par âge.")

def scan_6plus_videos():
    """Scanne et ajoute des vidéos adaptées aux 6+ ans"""
    print("\nScan des vidéos 6+ ans...")
    print("(Cette fonction sera implémentée dans une prochaine version)")

def main():
    """Fonction principale"""
    print("Mollo Scan 6+ - Classification des vidéos pour enfants")
    print("="*50)
    
    # Vérifier si la colonne age_rating existe
    age_rating_exists = check_age_rating_column()
    
    if not age_rating_exists:
        print("\n!!! La colonne 'age_rating' n'existe pas dans la table video_analyses")
        add_age_rating_column_manually()
        return
    
    print("\nOK La colonne 'age_rating' existe dans la table video_analyses")
    
    # Classer les vidéos existantes
    classify_existing_videos()
    
    # Scanner des vidéos 6+ ans
    scan_6plus_videos()
    
    print("\n" + "="*50)
    print("Scan 6+ terminé!")
    print("\nProchaines étapes:")
    print("1. Relancez le backend Java (mvn spring-boot:run)")
    print("2. Rafraîchissez le front-end pour voir les vidéos classées par âge")
    print("3. Utilisez les filtres d'âge pour afficher uniquement les vidéos 6+ ans")
    print("4. Si nécessaire, ajoutez manuellement des vidéos 6+ ans via l'interface Supabase")

if __name__ == "__main__":
    main()