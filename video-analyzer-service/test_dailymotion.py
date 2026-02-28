import yt_dlp
import os

video_url = "https://www.dailymotion.com/video/xa0t7dk"
output_path = "test_video.mp4"

ydl_opts = {
    'format': 'bestvideo[height<=480][ext=mp4]/best[height<=480]',
    'outtmpl': output_path,
    'noplaylist': True,
    'quiet': False,
    'no_warnings': False,
    'impersonate': 'Chrome-99',
    'impersonate_target': 'Chrome-99',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        print(f"Download successful: {info.get('title')}")
except Exception as e:
    print(f"Error: {e}")