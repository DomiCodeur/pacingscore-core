"""
Migration: Copy analysis_results -> video_analyses
"""
from supabase import create_client

def migrate():
    url = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
    key = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"
    supabase = create_client(url, key)
    
    print("Fetching analysis_results...")
    results = supabase.table("analysis_results").select("*").execute()
    old_data = results.data
    print(f"   {len(old_data)} records found")
    
    print("Fetching existing video_analyses...")
    existing = supabase.table("video_analyses").select("video_path, metadata->>tmdb_id, metadata->>fr_title").execute()
    existing_data = existing.data
    print(f"   {len(existing_data)} existing records")
    
    existing_keys = set()
    for item in existing_data:
        title = item.get('fr_title') or item.get('video_path')
        tmdb_id = item.get('tmdb_id')
        key = f"{title}:{tmdb_id}" if tmdb_id else title
        existing_keys.add(key)
    
    to_insert = []
    skipped = 0
    
    for old in old_data:
        title = old.get('series_title')
        if not title:
            url_val = old.get('video_url', '')
            title = url_val.split('/')[-1] if url_val else f"video_{old.get('id')}"
        
        tmdb_id = old.get('tmdb_id')
        key = f"{title}:{tmdb_id}" if tmdb_id else title
        
        if key in existing_keys:
            skipped += 1
            continue
        
        duration = old.get('video_duration', 0)
        num_scenes = old.get('num_scenes', 0)
        cuts_per_minute = (num_scenes / duration * 60) if duration > 0 else 0
        
        metadata = {
            "asl": old.get('average_shot_length'),
            "source": "python_analyzer",
            "fr_title": title,
            "tmdb_id": tmdb_id,
            "display_age": "0+",
            "description": old.get('series_overview', ''),
            "genres": old.get('series_genres', [])
        }
        
        new_record = {
            "video_path": title,
            "pacing_score": old.get('composite_score') or old.get('pacing_score', 0),
            "cuts_per_minute": cuts_per_minute,
            "metadata": metadata,
            "analyzed_at": old.get('created_at'),
            "age_rating": old.get('series_metadata', {}).get('display_age', '0+')
        }
        to_insert.append(new_record)
    
    print(f"\nMigration: {len(to_insert)} to insert, {skipped} already present")
    
    if to_insert:
        response = supabase.table("video_analyses").insert(to_insert).execute()
        print(f"   {len(response.data)} records migrated successfully")
    else:
        print("   No migration needed")
    
    final = supabase.table("video_analyses").select("*", count='exact').execute()
    print(f"\nTotal video_analyses: {final.count}")

if __name__ == "__main__":
    migrate()
