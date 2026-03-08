"""
Supabase Manager for PacingScore - Direct HTTP implementation
Avoids supabase-py client issues and mirrors backend's SupabaseService.
"""
import os
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase database operations for PacingScore via REST API"""
    
    def __init__(self):
        """Initialize Supabase connection parameters"""
        self.url = os.getenv("SUPABASE_URL")
        # Prefer service role key for bypassing RLS; fallback to anon/publishable
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            print("Error: SUPABASE_URL and SUPABASE_KEY are required")
            self.initialized = False
            return
        
        self.initialized = True
        print("Supabase manager initialized (direct HTTP)")
        
        # Common headers - Prefer minimal responses
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def _request(self, method: str, endpoint: str, json: Dict = None, params: Dict = None, headers: Dict = None) -> Optional[requests.Response]:
        """Internal helper to make authenticated requests to Supabase REST API"""
        if not self.initialized:
            logger.error("Supabase manager not initialized")
            return None
        
        url = f"{self.url}/rest/v1/{endpoint}"
        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)
        
        try:
            response = requests.request(method, url, json=json, params=params, headers=req_headers, timeout=30)
            if response.status_code >= 400:
                logger.error(f"Supabase error {response.status_code} on {method} {endpoint}: {response.text[:300]}")
                return None
            return response
        except requests.RequestException as e:
            logger.error(f"Supabase request failed for {method} {endpoint}: {e}")
            return None

    # ============ NEW METHODS (Gemini Architecture) ============
    
    def get_metadata_estimation(self, tmdb_id: str) -> Optional[Dict]:
        """
        DEPRECATED: Ne pas utiliser. Les métadonnées sont directement dans la tâche.
        Gardé pour compatibilité ancien code, mais retourne None.
        """
        return None
    
    def get_next_pending_task(self) -> Optional[Dict]:
        """
        Retrieve the next pending task and atomically mark it as 'processing'.
        Orders by created_at (oldest first) to ensure FIFO.
        Returns the task dict or None.
        """
        # 1. Fetch first pending task (ordered by creation)
        params = {
            "status": "eq.pending",
            "order": "created_at.asc",
            "limit": "1",
            "select": "*"
        }
        response = self._request("GET", "analysis_tasks", params=params)
        if not response or response.status_code != 200:
            return None
        
        tasks = response.json()
        if not tasks:
            return None
        
        task = tasks[0]
        task_id = task.get("id")
        
        # 2. Atomically mark it as processing
        if task_id:
            update_params = {"id": f"eq.{task_id}"}
            update_data = {"status": "processing"}
            patch_response = self._request("PATCH", "analysis_tasks", json=update_data, params=update_params)
            if patch_response and patch_response.status_code in (200, 204):
                print(f"Task {task_id} claimed for processing")
                return task
            else:
                print(f"Failed to claim task {task_id}, another worker may have claimed it")
                return None
        
        return task
    
    def update_analysis_task_status(self, task_id: str, status: str, error_message: str = None) -> bool:
        """Update task status (processing -> completed/failed)"""
        endpoint = f"analysis_tasks?id=eq.{task_id}"
        data = {"status": status}
        if error_message:
            data["error_message"] = error_message
        # updated_at column may not exist in the schema; skip it
        response = self._request("PATCH", endpoint, json=data)
        return response is not None and response.status_code in (200, 204)
    
    def save_mollo_score(self, tmdb_id: str, real_score: float, asl: float, video_url: str, scene_details: List[Dict],
                         source: str = None, video_type: str = None,
                         cuts_per_minute: float = None, video_duration: float = None, motion_intensity: float = None,
                         metadata: Dict = None) -> bool:
        """Save the actual Mollo score to mollo_scores table (upsert on tmdb_id)"""
        data = {
            "tmdb_id": tmdb_id,
            "real_score": real_score,
            "asl": asl,
            "video_url": video_url,
            "scene_details": scene_details,
            "analyzed_at": datetime.now().isoformat()
        }
        # Include optional fields if provided
        if source is not None:
            data["source"] = source
        if video_type is not None:
            data["video_type"] = video_type
        if cuts_per_minute is not None:
            data["cuts_per_minute"] = cuts_per_minute
        if video_duration is not None:
            data["video_duration"] = video_duration
        if motion_intensity is not None:
            data["motion_intensity"] = motion_intensity
        if metadata is not None:
            data["metadata"] = metadata
        
        logger.info(f"[DEBUG] Saving mollo_score: tmdb_id={tmdb_id}, data_keys={list(data.keys())}")
        # Use merge-duplicates to perform upsert
        params = {"on_conflict": "tmdb_id"}
        headers = {"Prefer": "resolution=merge-duplicates"}
        response = self._request("POST", "mollo_scores", json=data, params=params, headers=headers)
        logger.info(f"[DEBUG] Response status: {response.status_code if response else 'None'}, text: {response.text[:200] if response else 'None'}")
        if response and response.status_code in (200, 201):
            logger.info(f"Mollo score saved for TMDB ID {tmdb_id} (score: {real_score:.1f}, ASL: {asl:.2f}s)")
            return True
        else:
            status = response.status_code if response else 'no response'
            text = response.text if response else 'None'
            logger.error(f"Failed to save mollo_score for TMDB ID {tmdb_id}. Status: {status}, Response: {text[:300]}")
            return False
    
    def mark_task_completed(self, task_id: str) -> bool:
        return self.update_analysis_task_status(task_id, "completed")
    
    def mark_task_failed(self, task_id: str, error: str) -> bool:
        return self.update_analysis_task_status(task_id, "failed", error_message=error)


# Global instance
supabase_manager = SupabaseManager()
