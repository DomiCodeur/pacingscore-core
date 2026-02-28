from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Créer le client Supabase
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Exécuter le SQL directement via une fonction RPC
sql = "ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS analysis_date TIMESTAMPTZ DEFAULT NOW();"

try:
    # Essayer d'exécuter le SQL
    result = s.rpc('exec_sql', {'sql_query': sql}).execute()
    print("Colonne analysis_date ajoutée avec succès")
except Exception as e:
    print(f"Erreur: {e}")
    # Si la fonction RPC n'est pas disponible, essayer de vérifier la table
    try:
        # Vérifier si la colonne existe déjà
        result = s.table('analysis_results').select('analysis_date').limit(1).execute()
        print("La colonne analysis_date existe déjà")
    except Exception as e2:
        print(f"Erreur vérification: {e2}")