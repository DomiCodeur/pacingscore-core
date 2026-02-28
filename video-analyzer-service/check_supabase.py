
import os
import sys
import json
from supabase import create_client, Client

# Manually setting keys based on docker-compose.yml seen earlier
SUPABASE_URL = "https://gjkwsrzmaecmtfozkwmw.supabase.co"
# The service role key is usually needed for counting/bypass RLS if anon isn't enough, 
# but let's try the one from docker-compose first or check for others.
SUPABASE_KEY = "sb_publishable_2vEhYPJjXxrqyZRbYU2kSg_20NSSJ2t"

def check_results():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Trying 'video_analyses' instead of 'analysis_results' as common naming
        tables = ['analysis_results', 'video_analyses', 'movies', 'videos']
        for table in tables:
            try:
                response = supabase.table(table).select('id', count='exact').limit(1).execute()
                print(f"Table '{table}' count: {response.count}")
            except Exception as e:
                print(f"Table '{table}' error: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_results()
