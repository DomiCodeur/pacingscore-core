import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def check_analysis_results_table():
    """Vérifie la structure de la table analysis_results"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Essayer de récupérer les colonnes via la table system_information
        result = supabase.rpc("column_info", {"table_name": "analysis_results"}).execute()
        print("Colonnes de la table analysis_results:")
        for col in result.data:
            print(f"  - {col['column_name']} ({col['data_type']})")
    except Exception as e:
        print(f"Erreur récupération colonnes: {e}")
        
        # Essayer une requête simple pour voir la structure
        try:
            result = supabase.table("analysis_results").select("*").limit(1).execute()
            print("Requête SELECT * a réussi")
            if result.data:
                print(f"Première ligne: {result.data[0]}")
                print("Colonnes disponibles:", list(result.data[0].keys()))
        except Exception as e2:
            print(f"Erreur requête SELECT: {e2}")

if __name__ == "__main__":
    check_analysis_results_table()
