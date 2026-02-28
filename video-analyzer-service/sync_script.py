from supabase_manager import supabase_manager
from datetime import datetime

def sync():
    res = supabase_manager.client.table("analysis_results").select("*").eq("success", True).execute()
    for r in res.data:
        title = r.get("series_title")
        payload = { 
            "title": title, 
            "video_path": title, 
            "pacing_score": r.get("pacing_score"), 
            "age_rating": "0-6", 
            "tmdb_data": { "source": "dailymotion", "id": r.get("video_key") }, 
            "last_updated": datetime.now().isoformat() 
        }
        try: 
            supabase_manager.client.table("video_analyses").upsert(payload, on_conflict="title").execute()
            print(f"OK: {title}")
        except Exception as e: 
            print(f"ERR: {title} - {e}")

if __name__ == "__main__":
    sync()
