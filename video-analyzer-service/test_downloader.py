import sys
sys.path.append('C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service')
from analyzer import YouTubeDownloader

downloader = YouTubeDownloader()
video_url = "https://www.dailymotion.com/video/xa0t7dk"
try:
    path = downloader.download_video_snippet(video_url, max_duration=30)
    print(f"Downloaded to: {path}")
except Exception as e:
    print(f"Error: {e}")