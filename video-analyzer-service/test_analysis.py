import sys
sys.path.append('C:/Users/mathi/Documents/GitHub/pacingscore-clean/video-analyzer-service')
from analyzer import VideoAnalyzer

video_path = r'C:\Users\mathi\AppData\Local\Temp\video_6c1b4fcc.mp4'
analyzer = VideoAnalyzer(threshold=27.0)
try:
    result = analyzer.analyze_video(video_path, analyze_motion=False, analyze_flashes=True)
    print(f"Analyse réussie: {result.get('success')}")
    if result.get('success'):
        print(f"Durée: {result.get('video_duration')}")
        print(f"Scènes: {result.get('num_scenes')}")
        print(f"ASL: {result.get('average_shot_length')}")
        print(f"Pacing score: {result.get('pacing_score')}")
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()