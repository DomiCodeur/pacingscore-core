from supabase_manager import supabase_manager
res = supabase_manager.client.table("video_analyses").select("*").limit(1).execute()
if res.data:
    print(list(res.data[0].keys()))
else:
    print("EMPTY")
