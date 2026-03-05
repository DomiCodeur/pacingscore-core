from supabase import create_client
import sys

# Configuration
SUPABASE_URL = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwOTEwNTE3MiwiZXhwIjoyMDI0NjgxMTcyfQ.VjT6TxKKupXnWQ21FJK82CiGuvoR7dTxOiJgWJb7trk"

def main():
    try:
        print("Connexion a Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("Suppression des contenus...")
        data = supabase.table("video_analyses").delete().execute()
        print("- Table video_analyses nettoyee")
        
        data = supabase.table("analysis_results").delete().execute()
        print("- Table analysis_results nettoyee")
        
        print("Nettoyage termine avec succes!")
        return 0
        
    except Exception as e:
        print(f"Erreur: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())