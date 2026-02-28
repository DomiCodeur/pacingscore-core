import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_french_trailers():
    """Recherche des trailers de dessins animés enfants disponibles en France"""
    
    # Rechercher des vidéos de trailers d'animation française
    queries = [
        "bande annonce animation française",
        "trailer dessin animé français",
        "bande annonce film enfants français",
        "trailer cartoon français",
        "bande annonce éducative enfants"
    ]
    
    results = []
    
    for query in queries:
        print(f"Recherche: {query}")
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",  # IMPORTANT: inclure les snippets
            "type": "video",
            "maxResults": 5,
            "regionCode": "FR",
            "videoDuration": "medium",  # Entre 4 et 20 minutes
            "relevanceLanguage": "fr",
            "safeSearch": "strict"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "error" in data:
                print(f"  [ERROR] YouTube API error: {data['error']['message']}")
                continue
                
            if "items" in data:
                for item in data["items"]:
                    try:
                        video_id = item["id"]["videoId"]
                        snippet = item.get("snippet", {})
                        title = snippet.get("title", "No title")
                        description = snippet.get("description", "")
                        
                        # Vérifier si c'est un trailer d'animation
                        if any(keyword in title.lower() for keyword in ["annonce", "trailer", "bande", "teaser", "promo"]):
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            # Vérifier la disponibilité avec yt-dlp (optionnel - peut être lent)
                            is_available = check_video_availability(video_url)
                            
                            if is_available:
                                print(f"  [OK] {title}")
                                results.append({
                                    "title": title,
                                    "url": video_url,
                                    "video_id": video_id,
                                    "description": description
                                })
                            else:
                                print(f"  [NO] Non disponible: {title}")
                    except KeyError as e:
                        print(f"  [SKIP] Structure inattendue: {e}")
        
        except Exception as e:
            print(f"  [ERROR] Erreur requete: {e}")
    
    return results

def check_video_availability(video_url):
    """Vérifie si une vidéo YouTube est disponible"""
    import subprocess
    import sys
    
    try:
        # Utiliser yt-dlp pour vérifier si la vidéo est téléchargeable
        cmd = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--get-url", video_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

if __name__ == "__main__":
    print("Recherche de vidéos YouTube disponibles en France...")
    videos = search_french_trailers()
    
    print(f"\n{len(videos)} vidéos trouvées et vérifiées:")
    for i, vid in enumerate(videos, 1):
        print(f"{i}. {vid['title']}")
        print(f"   URL: {vid['url']}")
        print()