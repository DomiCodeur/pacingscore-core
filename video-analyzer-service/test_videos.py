import os
import requests
from datetime import datetime

def test_location_restrictions():
    """Test pour voir quels pays ont accès aux vidéos YouTube"""
    from dotenv import load_dotenv
    load_dotenv()
    
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    
    # Chercher des séries pour enfants
    url = f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16,10751&sort_by=popularity.desc&vote_average.gte=7.0&vote_count.gte=10&include_adult=false&page=1"
    r = requests.get(url)
    
    if r.status_code == 200:
        results = r.json().get('results', [])
        print(f"Found {len(results)} results")
        
        for i, item in enumerate(results[:5]):
            tv_id = item['id']
            v_url = f"https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={TMDB_API_KEY}"
            v_res = requests.get(v_url).json()
            video_url = None
            
            for v in v_res.get('results', []):
                if v['site'] == 'YouTube' and v['type'] in ['Trailer', 'Teaser']:
                    video_url = f"https://www.youtube.com/watch?v={v['key']}"
                    print(f"\n{i+1}. {item.get('name')} ({item.get('first_air_date', 'N/A')[:4]})")
                    print(f"   YouTube ID: {v['key']}")
                    print(f"   URL: {video_url}")
                    break
            
            if not video_url:
                print(f"\n{i+1}. {item.get('name')} - Pas de trailer YouTube disponible")

if __name__ == "__main__":
    test_location_restrictions()
