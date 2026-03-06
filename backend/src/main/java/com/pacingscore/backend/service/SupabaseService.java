package com.pacingscore.backend.service;

import com.pacingscore.backend.config.SupabaseConfig;
import com.pacingscore.backend.service.TMDBService.ShowInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SupabaseService {
    
    @Autowired
    private SupabaseConfig supabaseConfig;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    // ============ NEW METHODS (Gemini Architecture) ============
    
    /**
     * Save a show estimation from TMDB into metadata_estimations table
     * Uses upsert on tmdb_id to avoid duplicates.
     */
    public void saveMetadataEstimation(ShowInfo show) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/metadata_estimations";

        Map<String, Object> data = new HashMap<>();
        data.put("tmdb_id", String.valueOf(show.getId()));
        data.put("title", show.getTitle());
        data.put("estimated_score", show.getPacingScore());
        data.put("age_rating_guess", show.getAgeRating());
        data.put("media_type", show.getMediaType()); // "movie" ou "tv"

        // Build metadata JSONB
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("description", show.getDescription());
        metadata.put("display_age", show.getAgeRating());
        metadata.put("fr_title", show.getTitle());
        metadata.put("tmdb_id", show.getId());
        metadata.put("poster_path", show.getPosterPath());
        metadata.put("backdrop_path", show.getBackdropPath());
        metadata.put("first_air_date", show.getFirstAirDate());
        metadata.put("genres", show.getGenres());
        metadata.put("networks", show.getNetwork());
        metadata.put("keywords", show.getKeywords());
        metadata.put("episode_runtime", show.getEpisodeRuntime());
        metadata.put("certifications", show.getCertifications());
        metadata.put("episode_count", show.getEpisodeCount());
        metadata.put("season_count", show.getSeasonCount());

        data.put("metadata", metadata);

        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Prefer", "resolution=merge-duplicates"); // upsert

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);

        try {
            URI uri = new URI(endpoint + "?on_conflict=tmdb_id");
            restTemplate.postForEntity(uri, request, String.class);
            System.out.println("Estimation saved/upserted: " + show.getTitle() + " (type: " + show.getMediaType() + ")");
        } catch (Exception e) {
            System.err.println("Error saving estimation: " + show.getTitle() + " - " + e.getMessage());
        }
    }
    
    /**
     * Create a video analysis task for the Python worker
     * Includes media_type to help worker choose search strategy
     */
    public void createAnalysisTask(int tmdbId, String mediaType) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks";

        Map<String, Object> data = new HashMap<>();
        data.put("tmdb_id", String.valueOf(tmdbId));
        data.put("media_type", mediaType); // "movie" ou "tv"
        // status defaults to 'pending' in DB

        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Prefer", "resolution=merge-duplicates"); // upsert on conflict

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);

        try {
            // Add on_conflict=tmdb_id to avoid duplicate key errors
            URI uri = new URI(endpoint + "?on_conflict=tmdb_id");
            restTemplate.postForEntity(uri, request, String.class);
            System.out.println("Analysis task created/upserted for TMDB ID: " + tmdbId + " (type: " + mediaType + ")");
        } catch (Exception e) {
            System.err.println("Error creating task for TMDB ID " + tmdbId + ": " + e.getMessage());
        }
    }
    
    /**
     * Check if a show already exists in metadata_estimations
     */
    public boolean showExists(int tmdbId) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/metadata_estimations";
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.set("Prefer", "count=exact");
        
        HttpEntity<String> request = new HttpEntity<>(headers);
        
        try {
            String url = endpoint + "?tmdb_id=eq." + tmdbId + "&select=tmdb_id";
            ResponseEntity<List> response = restTemplate.exchange(
                url, HttpMethod.GET, request, List.class
            );
            List<?> body = response.getBody();
            return body != null && !body.isEmpty();
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * Get metadata estimation by TMDB ID (for Python worker)
     */
    public Map<String, Object> getMetadataEstimation(int tmdbId) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/metadata_estimations";
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        
        HttpEntity<String> request = new HttpEntity<>(headers);
        
        try {
            String url = endpoint + "?tmdb_id=eq." + tmdbId + "&select=*";
            ResponseEntity<Map[]> response = restTemplate.exchange(
                url, HttpMethod.GET, request, Map[].class
            );
            if (response.getBody() != null && response.getBody().length > 0) {
                return response.getBody()[0];
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    /**
     * Save the real Mollo score (calculated by Python worker)
     */
    public void saveMolloScore(String tmdbId, double realScore, double asl, String videoUrl, 
                               Map<String, Object> sceneDetails, String sourceType, Double videoDuration) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/mollo_scores";
        
        Map<String, Object> data = new HashMap<>();
        data.put("tmdb_id", tmdbId);
        data.put("real_score", realScore);
        data.put("asl", asl);
        data.put("video_url", videoUrl);
        data.put("scene_details", sceneDetails);
        data.put("source_type", sourceType);
        if (videoDuration != null) {
            data.put("video_duration", videoDuration);
        }
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
        
        try {
            restTemplate.postForEntity(endpoint, request, String.class);
            System.out.println("Mollo score saved for TMDB ID: " + tmdbId);
        } catch (Exception e) {
            System.err.println("Error saving Mollo score for TMDB ID " + tmdbId + ": " + e.getMessage());
        }
    }
    
    /**
     * Update analysis task status
     */
    public void updateAnalysisTaskStatus(String taskId, String status) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?id=eq." + taskId;
        
        Map<String, Object> data = new HashMap<>();
        data.put("status", status);
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Prefer", "return=representation");
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
        
        try {
            restTemplate.exchange(endpoint, HttpMethod.PATCH, request, String.class);
        } catch (Exception e) {
            System.err.println("Error updating task " + taskId + ": " + e.getMessage());
        }
    }
    
    /**
     * Get next pending task (for Python worker)
     */
    public Map<String, Object> getNextPendingTask() {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks";
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        
        HttpEntity<String> request = new HttpEntity<>(headers);
        
        try {
            String url = endpoint + "?status=eq.pending&order=created_at.asc&limit=1&select=*";
            ResponseEntity<Map[]> response = restTemplate.exchange(
                url, HttpMethod.GET, request, Map[].class
            );
            if (response.getBody() != null && response.getBody().length > 0) {
                return response.getBody()[0];
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    // ============ DEPRECATED METHODS (for backward compatibility) ============
    
    /**
     * Save show analysis to video_analyses (LEGACY)
     * Deprecated: use saveMetadataEstimation + createAnalysisTask
     */
    @Deprecated
    public void saveShowAnalysis(ShowInfo show) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses";
        
        Map<String, Object> data = new HashMap<>();
        data.put("pacing_score", show.getPacingScore());
        data.put("age_rating", show.getAgeRating());
        data.put("cuts_per_minute", 0.0);
        data.put("video_path", "TMDB: " + show.getTitle());
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("description", show.getDescription());
        metadata.put("display_age", show.getAgeRating());
        metadata.put("fr_title", show.getTitle());
        metadata.put("tmdb_id", show.getId());
        
        Map<String, Object> tmdbData = new HashMap<>();
        tmdbData.put("poster_path", show.getPosterPath());
        tmdbData.put("backdrop_path", show.getBackdropPath());
        tmdbData.put("first_air_date", show.getFirstAirDate());
        tmdbData.put("tmdb_id", show.getId());
        tmdbData.put("fr_title", show.getTitle());
        metadata.put("tmdb_data", tmdbData);
        
        data.put("metadata", metadata);
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
        
        try {
            restTemplate.postForEntity(endpoint, request, String.class);
            System.out.println("Saved (legacy): " + show.getTitle());
        } catch (Exception e) {
            System.err.println("Error saving: " + show.getTitle() + " - " + e.getMessage());
        }
    }
    
    /**
     * Check if show exists in video_analyses (LEGACY)
     * Deprecated
     */
    @Deprecated
    public boolean showExistsLegacy(int tmdbId) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses";
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.set("Prefer", "count=exact");
        
        HttpEntity<String> request = new HttpEntity<>(headers);
        
        try {
            String url = endpoint + "?metadata->>tmdb_id=eq." + tmdbId;
            ResponseEntity<String> response = restTemplate.exchange(
                url, HttpMethod.GET, request, String.class
            );
            String count = response.getHeaders().getFirst("Content-Range");
            return count != null && Integer.parseInt(count.split("/")[1]) > 0;
        } catch (Exception e) {
            return false;
        }
    }
}