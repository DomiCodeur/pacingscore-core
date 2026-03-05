from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def add_age_group_column():
    """Ajoute la colonne age_group à la table analysis_results"""
    sql = "ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS age_group VARCHAR(10);"
    
    try:
        # Essayer d'appeler une fonction RPC pour exécuter du SQL
        r = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
        print("Colonne age_group ajoutée via RPC")
        return True
    except Exception as e:
        print(f"Erreur RPC: {e}")
        
        # Essayer une autre méthode: créer une fonction SQL
        try:
            # Créer une fonction pour exécuter du SQL
            create_func_sql = """
            CREATE OR REPLACE FUNCTION public.exec_sql(sql_query text)
            RETURNS void
            LANGUAGE sql
            AS $$
            EXECUTE sql_query;
            $$;
            """
            r = supabase.rpc('exec_sql', {'sql_query': create_func_sql}).execute()
            print("Fonction exec_sql créée")
            
            # Maintenant ajouter la colonne
            r = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
            print("Colonne age_group ajoutée")
            return True
        except Exception as e2:
            print(f"Erreur création fonction: {e2}")
            print("Il faut ajouter manuellement la colonne age_group via l'interface Supabase")
            return False

if __name__ == "__main__":
    success = add_age_group_column()
    if success:
        print("\nLa colonne age_group a été ajoutée avec succès!")
        print("Vous pouvez maintenant exécuter mollo_scan_6plus.py pour peupler cette colonne.")
    else:
        print("\nÉchec de l'ajout de la colonne age_group.")