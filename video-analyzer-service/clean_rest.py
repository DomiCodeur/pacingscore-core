import requests

def main():
    headers = {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDkxMDUxNzIsImV4cCI6MjAyNDY4MTE3Mn0.CC7yB7r3mxHsl-3ocHBBXxutGOLIf6uFDpnR9CzHNlA',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdqa3dzcnptYWVjbXRmb3prd213Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDkxMDUxNzIsImV4cCI6MjAyNDY4MTE3Mn0.CC7yB7r3mxHsl-3ocHBBXxutGOLIf6uFDpnR9CzHNlA',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # 1. Nettoyage video_analyses
    print("Nettoyage video_analyses...")
    response = requests.delete(
        'https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses',
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Erreur: {response.text}")
    
    # 2. Nettoyage analysis_results
    print("\nNettoyage analysis_results...")
    response = requests.delete(
        'https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/analysis_results',
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Erreur: {response.text}")

if __name__ == "__main__":
    main()