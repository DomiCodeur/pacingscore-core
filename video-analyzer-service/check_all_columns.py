from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_columns():
    """Vérifie toutes les colonnes de la table analysis_results"""
    try:
        # Essayer une requête simple pour voir toutes les colonnes
        result = supabase.table("analysis_results").select("*").limit(1).execute()
        
        if result.data:
            print("Colonnes de la table analysis_results:")
            columns = list(result.data[0].keys())
            for col in sorted(columns):
                print(f"  - {col}")
            
            # Vérifier si des colonnes liées à l'âge existent
            age_related = [col for col in columns if 'age' in col.lower() or 'rating' in col.lower()]
            if age_related:
                print(f"\nColonnes liées à l'âge trouvées: {age_related}")
            else:
                print("\nAucune colonne liée à l'âge trouvée.")
                print("La colonne 'age_group' doit être ajoutée.")
        else:
            print("La table est vide ou inaccessible.")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_columns()