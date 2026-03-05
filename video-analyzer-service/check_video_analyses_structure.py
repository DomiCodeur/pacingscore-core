from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_video_analyses_table():
    """Vérifie la structure de la table video_analyses"""
    try:
        # Essayer une requête simple pour voir toutes les colonnes
        result = supabase.table("video_analyses").select("*").limit(1).execute()
        
        if result.data:
            print("Colonnes de la table video_analyses:")
            columns = list(result.data[0].keys())
            for col in sorted(columns):
                print(f"  - {col}")
            
            # Vérifier si des colonnes liées à l'âge existent
            age_related = [col for col in columns if 'age' in col.lower() or 'rating' in col.lower()]
            if age_related:
                print(f"\nColonnes liées à l'âge trouvées: {age_related}")
            else:
                print("\nAucune colonne liée à l'âge trouvée.")
                print("La colonne 'age_rating' doit être ajoutée.")
        else:
            print("La table video_analyses est vide ou inaccessible.")
            
        # Compter le nombre total d'entrées
        count_result = supabase.table("video_analyses").select("*").execute()
        total_count = len(count_result.data) if count_result.data else 0
        print(f"\nNombre total de vidéos dans video_analyses: {total_count}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_video_analyses_table()