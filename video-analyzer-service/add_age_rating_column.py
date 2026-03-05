from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
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

def main():
    """Fonction principale"""
    print("Vérification de la colonne age_rating dans video_analyses")
    print("="*50)
    
    # Vérifier si la colonne age_rating existe
    age_rating_exists = check_age_rating_column()
    
    if not age_rating_exists:
        print("\n!!! La colonne 'age_rating' n'existe pas dans la table video_analyses")
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
        print("5. Une fois la colonne ajoutée, exécutez: python mollo_scan_6plus.py")
        print("\n" + "="*60)
    else:
        print("\nOK La colonne 'age_rating' existe dans la table video_analyses")
        print("\nVous pouvez exécuter: python mollo_scan_6plus.py")

if __name__ == "__main__":
    main()