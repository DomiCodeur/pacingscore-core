from supabase_manager import supabase_manager
from datetime import datetime

def sync():
    # 1. Fetch from analysis_results (where success=True)
    res = supabase_manager.client.table("analysis_results").select("*").eq("success", True).execute()
    if not res.data:
        print("Nothing to sync.")
        return
    
    print(f"Syncing {len(res.data)} items.")
    for r in res.data:
        title = r.get("series_title")
        score = r.get("pacing_score")
        
        # We only use columns that exist in video_analyses:
        # id (uuid, auto), video_path (text), pacing_score (float), cuts_per_minute (float), metadata (jsonb), analyzed_at (timestamptz)
        
        duration = r.get("video_duration") or 60
        scenes = r.get("num_scenes") or 0
        cpm = (scenes / (duration / 60)) if duration > 0 else 0
        
        payload = { 
            "video_path": title, 
            "pacing_score": score,
            "cuts_per_minute": cpm,
            "metadata": { 
                "source": "dailymotion", 
                "video_key": r.get("video_key"),
                "asl": r.get("average_shot_length")
            },
            "analyzed_at": datetime.now().isoformat() 
        }
        
        try: 
            # Check if exists by video_path
            check = supabase_manager.client.table("video_analyses").select("id").eq("video_path", title).execute()
            if check.data:
                supabase_manager.client.table("video_analyses").update(payload).eq("video_path", title).execute()
                print(f"Synced (Update): {title}")
            else:
                supabase_manager.client.table("video_analyses").insert(payload).execute()
                print(f"Synced (Insert): {title}")
        except Exception as e: 
            print(f"ERR: {title} - {e}")

if __name__ == "__main__":
    sync()
