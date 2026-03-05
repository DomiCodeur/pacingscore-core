from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
ENV_PATH = 'C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service/.env'
load_dotenv(ENV_PATH)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def create_exec_sql_function():
    """Crée la fonction exec_sql pour exécuter des requêtes SQL"""
    create_function_sql = """
    CREATE OR REPLACE FUNCTION public.exec_sql(sql_query text)
    RETURNS void
    LANGUAGE plpgsql
    AS $$
    BEGIN
        EXECUTE sql_query;
    END;
    $$;
    """
    
    try:
        # Essayer de créer la fonction via une requête directe
        # Cela ne fonctionnera probablement pas via l'API standard
        # Mais essayons quand même
        result = supabase.rpc('exec_sql', {'sql_query': create_function_sql}).execute()
        print("Fonction exec_sql créée avec succès")
        return True
    except Exception as e:
        print(f"Erreur création fonction exec_sql: {e}")
        print("\nLa fonction exec_sql doit être créée manuellement via l'interface Supabase SQL Editor")
        print("Avec la requête SQL suivante:")
        print(create_function_sql)
        return False

def add_age_group_column():
    """Ajoute la colonne age_group à la table analysis_results"""
    sql = "ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS age_group VARCHAR(10);"
    
    try:
        result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
        print("Colonne age_group ajoutée avec succès")
        return True
    except Exception as e:
        print(f"Erreur ajout colonne age_group: {e}")
        print("\nLa colonne age_group doit être ajoutée manuellement via l'interface Supabase SQL Editor")
        print("Avec la requête SQL suivante:")
        print(sql)
        return False

if __name__ == "__main__":
    print("Création de la fonction exec_sql...")
    func_created = create_exec_sql_function()
    
    if func_created:
        print("\nAjout de la colonne age_group...")
        add_age_group_column()
    else:
        print("\nSans la fonction exec_sql, la colonne age_group doit être ajoutée manuellement.")
        print("\nRequête SQL à exécuter dans Supabase SQL Editor:")
        print("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS age_group VARCHAR(10);")