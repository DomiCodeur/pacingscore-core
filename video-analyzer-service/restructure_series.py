import os
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def restructure_as_series():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Récupérer toutes les analyses
    data = supabase.table("video_analyses").select("*").execute().data
    print(f"Nombre total d'analyses : {len(data)}")
    
    # 2. Mots-clés des séries principales
    series_map = {
        "Petit Ours Brun": ["petit ours brun"],
        "Trotro": ["trotro"],
        "T'choupi": ["tchoupi"],
        "Peppa Pig": ["peppa pig"],
        "Bluey": ["bluey"],
        "Simon": ["simon le lapin", "simon"],
        "Masha et l'Ours": ["masha"],
        "Caillou": ["caillou"],
        "Pocoyo": ["pocoyo"],
        "Didou": ["didou"],
        "Puffin Rock": ["puffin rock"]
    }
    
    # 3. Groupement
    grouped_data = defaultdict(list)
    remaining_ids = []
    
    for item in data:
        title = item["video_path"].lower()
        matched = False
        
        for series_name, keywords in series_map.items():
            if any(kw in title for kw in keywords):
                grouped_data[series_name].append(item)
                matched = True
                break
                
        if not matched:
            # On garde les titres inconnus (ex: films Disney uniques)
            pass
            
    # 4. Suppression des doublons et création de l'enregistrement "Série"
    for series_name, items in grouped_data.items():
        if len(items) > 1:
            # Calculer la moyenne du score de pacing
            scores = [i["pacing_score"] for i in items]
            avg_score = int(sum(scores) / len(scores))
            
            # On garde le premier ID et on supprime les autres
            keep_item = items[0]
            to_delete = [i["id"] for i in items[1:]]
            
            print(f"Série {series_name}: {len(items)} épisodes trouvés. Score moyen {avg_score}%.")
            
            # Mise à jour du premier enregistrement
            supabase.table("video_analyses").update({
                "video_path": series_name, # On renomme en nom propre de la série
                "pacing_score": avg_score
            }).eq("id", keep_item["id"]).execute()
            
            # Suppression des autres épisodes
            if to_delete:
                supabase.table("video_analyses").delete().in_("id", to_delete).execute()
                print(f"  {len(to_delete)} épisodes supprimés.")

if __name__ == "__main__":
    restructure_as_series()
