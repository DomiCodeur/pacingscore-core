import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def debug_youtube_api():
    """Debug l'API YouTube"""
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": "test",
        "type": "video",
        "maxResults": 2
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        data = response.json()
        print(f"\nResponse Data (pretty):")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_youtube_api()
