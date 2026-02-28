from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Essayer d'ajouter la colonne analysis_date
sql = "ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS analysis_date TIMESTAMPTZ DEFAULT NOW();"

try:
    # Essayer d'appeler une fonction RPC pour exécuter du SQL
    r = s.rpc('exec_sql', {'sql_query': sql}).execute()
    print("Colonne ajoutée via RPC")
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
        r = s.rpc('exec_sql', {'sql_query': create_func_sql}).execute()
        print("Fonction exec_sql créée")
        # Maintenant ajouter la colonne
        r = s.rpc('exec_sql', {'sql_query': sql}).execute()
        print("Colonne analysis_date ajoutée")
    except Exception as e2:
        print(f"Erreur création fonction: {e2}")
        print("Il faut ajouter manuellement la colonne analysis_date via l'interface Supabase")