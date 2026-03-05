"""
Supabase Manager for PacingScore
"""
import os
from datetime import datetime
from typing import Dict, Any

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not installed. Required for production.")
    Client = None


class SupabaseManager:
    """Manages Supabase database operations for PacingScore"""
    
    def __init__(self):
        """Initialize Supabase client"""
        from dotenv import load_dotenv
        load_dotenv()
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            print("Warning: Supabase credentials missing. Using mock mode.")
            self.client = None
        else:
            try:
                self.client = create_client(self.url, self.key)
                print("Supabase client initialized")
            except Exception as e:
                print(f"Warning: Supabase init failed: {e}")
                self.client = None
    
    def save_analysis_result(self, result: Dict[str, Any], video_url: str, series_title: str = None, tmdb_id: int = None, video_key: str = None) -> bool:
        """Save analysis result to video_analyses table"""
        if not self.client:
            print("Supabase not configured - result not saved")
            return False
        
        try:
            # Determine title
            title = series_title
            if not title:
                if video_url:
                    title = video_url.split('/')[-1]
                else:
                    title = f"video_{result.get('video_duration', 0)}s"
            
            # Calculate cuts per minute
            duration = result.get("video_duration", 0)
            num_scenes = result.get("num_scenes", 0)
            cuts_per_minute = (num_scenes / duration * 60) if duration > 0 else 0
            
            # Build metadata JSON
            metadata = {
                "asl": result.get("average_shot_length"),
                "source": "python_analyzer",
                "fr_title": title,
                "tmdb_id": tmdb_id,
                "display_age": result.get("series_metadata", {}).get("display_age", "0+"),
                "description": result.get("series_overview", ""),
                "genres": result.get("series_genres", [])
            }
            
            # Build record for video_analyses
            analysis_data = {
                "video_path": title,
                "pacing_score": result.get("composite_score") or result.get("pacing_score", 0),
                "cuts_per_minute": cuts_per_minute,
                "metadata": metadata,
                "analyzed_at": datetime.now().isoformat(),
                "age_rating": result.get("series_metadata", {}).get("display_age", "0+")
            }
            
            # Utiliser Upsert au lieu de Insert pour éviter les doublons sur video_path
            response = self.client.table("video_analyses").upsert(analysis_data, on_conflict="video_path").execute()
            
            if response.data:
                print(f"Result saved to video_analyses (ID: {response.data[0].get('id')}, Title: {title})")
                return True
            else:
                print("Failed to save to video_analyses")
                return False
                
        except Exception as e:
            print(f"Supabase error: {e}")
            return False
    
    def is_already_analyzed(self, tmdb_id: int, series_title: str) -> bool:
        """Check if a show/movie has already been analyzed"""
        if not self.client:
            return False
        
        try:
            if tmdb_id:
                response = self.client.table("video_analyses") \
                    .select("id") \
                    .eq("metadata->>tmdb_id", tmdb_id) \
                    .execute()
                if len(response.data) > 0:
                    return True
            
            if series_title:
                response = self.client.table("video_analyses") \
                    .select("id") \
                    .eq("metadata->>fr_title", series_title) \
                    .execute()
                if len(response.data) > 0:
                    return True
        except Exception as e:
            print(f"Duplicate check error: {e}")
        
        return False
    
    def get_analysis_history(self, limit: int = 10) -> list:
        """Get analysis history"""
        if not self.client:
            return []
        
        try:
            response = self.client.table("video_analyses") \
                .select("*") \
                .order("analyzed_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    
    def update_analysis_status(self, analysis_id: int, status: str) -> bool:
        """Update analysis status (not used currently)"""
        if not self.client:
            return False
        
        try:
            response = self.client.table("video_analyses") \
                .update({"status": status, "updated_at": datetime.now().isoformat()}) \
                .eq("id", analysis_id) \
                .execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Status update error: {e}")
            return False


# Global instance
supabase_manager = SupabaseManager()

