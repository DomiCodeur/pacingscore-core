"""
Gestionnaire Supabase pour PacingScore
"""
import os
from datetime import datetime
from typing import Dict, Any
try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client non installé. Installation nécessaire...")
    # On continuera sans Supabase pour les tests locaux


class SupabaseManager:
    """Gestionnaire de la base de données Supabase pour PacingScore"""
    
    def __init__(self):
        """Initialise le client Supabase"""
        from dotenv import load_dotenv
        load_dotenv()
        self.url = os.getenv("SUPABASE_URL")
        # On privilégie la clé secrète pour les opérations d'écriture/schema
        self.key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            print("Warning: Supabase credentials not configured. Using mock mode.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client: {e}")
                self.client = None
    
    def save_analysis_result(self, result: Dict[str, Any], video_url: str, series_title: str = None, tmdb_id: int = None, video_key: str = None) -> bool:
        """
        Sauvegarde les résultats d'analyse dans Supabase
        
        Args:
            result: Résultat de l'analyse
            video_url: URL de la vidéo analysée
            series_title: Titre de la série (optionnel)
            tmdb_id: ID TMDB unique (optionnel)
            video_key: ID YouTube unique (optionnel)
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        if not self.client:
            print("Supabase non configuré - résultat non sauvegardé")
            return False
        
        try:
            # Préparer les données pour la table analysis_results
            analysis_data = {
                "video_url": video_url,
                "series_title": series_title,
                "video_duration": result.get("video_duration"),
                "num_scenes": result.get("num_scenes"),
                "average_shot_length": result.get("average_shot_length"),
                "pacing_score": result.get("pacing_score"),
                "evaluation_label": result.get("evaluation", {}).get("label"),
                "evaluation_description": result.get("evaluation", {}).get("description"),
                "evaluation_color": result.get("evaluation", {}).get("color"),
                "scene_details": result.get("scene_details", []),
                "created_at": datetime.now().isoformat(),
                "success": result.get("success", False),
                "error": result.get("error"),
                # Ajout des nouvelles metadata
                "series_year": result.get("series_metadata", {}).get("year"),
                "series_overview": result.get("series_metadata", {}).get("overview"),
                "series_genres": result.get("series_metadata", {}).get("genres", []),
                "tmdb_id": tmdb_id,  # ID unique TMDB
                "video_key": video_key  # ID unique YouTube
            }
            
            # Insérer dans la table analysis_results
            response = self.client.table("analysis_results").insert(analysis_data).execute()
            
            if response.data:
                print(f"✓ Résultat sauvegardé dans Supabase (ID Supabase: {response.data[0].get('id')}, TMDB: {tmdb_id})")
                return True
            else:
                print("⚠ Erreur lors de la sauvegarde dans Supabase")
                return False
                
        except Exception as e:
            print(f"⚠ Erreur Supabase: {e}")
            return False
    
    def is_already_analyzed(self, tmdb_id: int, series_title: str) -> bool:
        """
        Vérifie si une série/film a déjà été analysé
        
        Args:
            tmdb_id: ID TMDB unique de la série
            series_title: Titre de la série pour fallback
            
        Returns:
            bool: True si déjà analysé
        """
        if not self.client:
            return False
        
        try:
            # Essayer d'abord avec le tmdb_id (méthode la plus fiable)
            if tmdb_id:
                response = self.client.table("analysis_results") \
                    .select("id") \
                    .eq("tmdb_id", tmdb_id) \
                    .execute()
                if len(response.data) > 0:
                    return True
            
            # Fallback avec le titre si pas d'ID
            if series_title:
                response = self.client.table("analysis_results") \
                    .select("id") \
                    .eq("series_title", series_title) \
                    .execute()
                if len(response.data) > 0:
                    return True
        
        except Exception as e:
            print(f"⚠ Erreur vérification doublons: {e}")
        
        return False
    
    def get_analysis_history(self, limit: int = 10) -> list:
        """
        Récupère l'historique des analyses
        
        Args:
            limit: Nombre de résultats à retourner
            
        Returns:
            list: Liste des analyses
        """
        if not self.client:
            print("Supabase non configuré - retourne liste vide")
            return []
        
        try:
            response = self.client.table("analysis_results") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data
        except Exception as e:
            print(f"⚠ Erreur Supabase lors de la récupération de l'historique: {e}")
            return []
    
    def update_analysis_status(self, analysis_id: int, status: str) -> bool:
        """
        Met à jour le statut d'une analyse
        
        Args:
            analysis_id: ID de l'analyse
            status: Nouveau statut
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        if not self.client:
            return False
        
        try:
            response = self.client.table("analysis_results") \
                .update({"status": status, "updated_at": datetime.now().isoformat()}) \
                .eq("id", analysis_id) \
                .execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"⚠ Erreur Supabase lors de la mise à jour du statut: {e}")
            return False


# Instance globale
supabase_manager = SupabaseManager()
