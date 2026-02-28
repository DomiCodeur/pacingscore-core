import os
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def test_tmdb():
    print(f"Testing TMDB API with key: {TMDB_API_KEY[:5]}...")
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={TMDB_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            results = r.json().get('results', [])
            print(f"Found {len(results)} results")
            if results:
                print(f"First result: {results[0].get('name')}")
        else:
            print(f"Error body: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_tmdb()
