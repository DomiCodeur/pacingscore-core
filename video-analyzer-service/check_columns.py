from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Essayer de récupérer la première ligne pour voir les colonnes
try:
    r = s.table('analysis_results').select('*').limit(1).execute()
    if r.data:
        print("Colonnes existantes:")
        for key in r.data[0].keys():
            print(f" - {key}")
    else:
        print("Table vide")
except Exception as e:
    print(f"Erreur: {e}")
    # Essayer de vérifier le schéma via RPC si disponible
    try:
        r = s.rpc('table_info', {'table_name': 'analysis_results'}).execute()
        print(r.data)
    except Exception as e2:
        print(f"Erreur RPC: {e2}")