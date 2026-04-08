package com.pacingscore.backend.service;

import com.pacingscore.backend.config.SupabaseConfig;
import com.pacingscore.backend.service.TMDBService.ShowInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.ArrayList;
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
    /**
     * Réinitialise les tâches en échec pour qu'elles soient retraitées
     */
    public int resetFailedTasks() {
        try {
            String url = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?status=eq.failed";
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            headers.set("Content-Type", "application/json");
            headers.set("Accept", "application/json");
            headers.set("X-HTTP-Method-Override", "PATCH");

            // Simplifions le payload : seulement le champ à changer
            String jsonPayload = "{\"status\":\"pending\"}";
            HttpEntity<String> entity = new HttpEntity<>(jsonPayload, headers);

            // Utilise POST avec override car RestTemplate par défaut ne supporte pas PATCH
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
            int statusCode = response.getStatusCodeValue();
            String body = response.getBody();
            
            System.out.println("[DEBUG] Reset failed response status: " + statusCode);
            System.out.println("[DEBUG] Reset failed response body: " + body);
            
            // Si Supabase retourne un tableau JSON, on peut le parser approximativement
            if (body != null && !body.isBlank() && body.startsWith("[") && body.endsWith("]")) {
                // Compter les objets dans le tableau approximativement
                long count = body.chars().filter(ch -> ch == '{').count();
                return (int) count;
            }
            return 0;
        } catch (Exception e) {
            System.err.println("Erreur reset failed: " + e.getMessage());
            e.printStackTrace();
            return 0;
        }
    }

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
     * Récupère le statut de la file d'analyse (pour monitoring)
     * Retourne une map avec les comptes par statut
     */
    public Map<String, Integer> getAnalysisQueueStatus() {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?select=status&order=id.desc&limit=2000";
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        HttpEntity<String> entity = new HttpEntity<>(headers);
        try {
            ResponseEntity<String> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, String.class);
            String body = response.getBody();
            if (body == null) {
                return Map.of("error", 0);
            }
            // Compter les statuts
            int pending = 0, processing = 0, completed = 0, failed = 0;
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
            List<Map<String, Object>> tasks = mapper.readValue(body,
                mapper.getTypeFactory().constructCollectionType(List.class, Map.class));
            for (Map<String, Object> t : tasks) {
                String st = (String) t.get("status");
                switch (st) {
                    case "pending": pending++; break;
                    case "processing": processing++; break;
                    case "completed": completed++; break;
                    case "failed": failed++; break;
                }
            }
            Map<String, Integer> counts = new HashMap<>();
            counts.put("pending", pending);
            counts.put("processing", processing);
            counts.put("completed", completed);
            counts.put("failed", failed);
            counts.put("total", tasks.size());
            return counts;
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Integer> err = new HashMap<>();
            err.put("error", 1);
            return err;
        }
    }
    
    /**
     * Create a video analysis task for the Python worker
     * Includes media_type and full metadata JSONB to avoid needing metadata_estimations
     */
    public void createAnalysisTask(ShowInfo show) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks";

        Map<String, Object> data = new HashMap<>();
        data.put("tmdb_id", String.valueOf(show.getId()));
        data.put("media_type", show.getMediaType()); // "movie" ou "tv"

        // Build metadata JSONB : toutes les infos nécessaires pour le worker et frontend
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("title", show.getTitle());
        metadata.put("description", show.getDescription());
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
        metadata.put("age_rating", show.getAgeRating());
        data.put("metadata", metadata);

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
            System.out.println("Analysis task created/upserted for TMDB ID: " + show.getId() + " (type: " + show.getMediaType() + ")");
        } catch (Exception e) {
            System.err.println("Error creating task for TMDB ID " + show.getId() + ": " + e.getMessage());
        }
    }
    
    /**
     * Check if a show already exists (has analysis task or score)
     */
    public boolean showExists(int tmdbId) {
        // Check analysis_tasks first
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks";
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        HttpEntity<String> request = new HttpEntity<>(headers);
        try {
            String url = endpoint + "?tmdb_id=eq." + tmdbId + "&select=tmdb_id&limit=1";
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, request, String.class);
            if (response.getStatusCode().is2xxSuccessful()) {
                String body = response.getBody();
                if (body != null && !body.trim().isEmpty() && !body.equals("[]")) {
                    return true;
                }
            }
        } catch (Exception e) {
            // fallthrough to check mollo_scores
        }
        // Also check mollo_scores (already analyzed)
        try {
            String scoresEndpoint = supabaseConfig.getUrl() + "/rest/v1/mollo_scores?tmdb_id=eq." + tmdbId + "&select=tmdb_id&limit=1";
            ResponseEntity<String> response = restTemplate.exchange(scoresEndpoint, HttpMethod.GET, request, String.class);
            if (response.getStatusCode().is2xxSuccessful()) {
                String body = response.getBody();
                return body != null && !body.trim().isEmpty() && !body.equals("[]");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
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

    // ============ ADMIN METHODS ============

    /**
     * Récupère la liste des tâches échouées
     * @param limit nombre max de résultats (null = tous)
     * @param tmdbId filtre optionnel sur TMDB ID
     * @return liste des tâches avec métadonnées
     */
    public List<Map<String, Object>> getFailedTasks(Integer limit, String tmdbId) {
        try {
            StringBuilder endpoint = new StringBuilder(supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?status=eq.failed&order=created_at.desc");
            if (tmdbId != null && !tmdbId.isEmpty()) {
                endpoint.append("&tmdb_id=eq.").append(tmdbId);
            }
            if (limit != null && limit > 0) {
                endpoint.append("&limit=").append(limit);
            }
            // Sélectionne toutes les colonnes, y compris metadata (JSONB)
            endpoint.append("&select=*");

            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<String> response = restTemplate.exchange(endpoint.toString(), HttpMethod.GET, entity, String.class);
            String body = response.getBody();
            if (body == null || body.isBlank() || body.equals("[]")) {
                return new ArrayList<>();
            }
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
            List<Map<String, Object>> tasks = mapper.readValue(body,
                mapper.getTypeFactory().constructCollectionType(List.class, Map.class));
            
            // Enrichir avec le titre depuis metadata
            for (Map<String, Object> task : tasks) {
                Object meta = task.get("metadata");
                if (meta instanceof Map) {
                    Map<String, Object> metadata = (Map<String, Object>) meta;
                    String title = (String) metadata.getOrDefault("title", "Inconnu");
                    task.put("title", title);
                }
            }
            return tasks;
        } catch (Exception e) {
            System.err.println("Erreur getFailedTasks: " + e.getMessage());
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    /**
     * Réinitialise une tâche spécifique (la remet en pending)
     * @param taskId ID de la tâche
     * @return true si la tâche a été trouvée et mise à jour
     */
    public boolean resetTask(String taskId) {
        try {
            String url = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?id=eq." + taskId;
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            headers.set("Content-Type", "application/json");
            headers.set("Accept", "application/json");
            headers.set("X-HTTP-Method-Override", "PATCH");

            String jsonPayload = "{\"status\":\"pending\",\"error_message\":null}";
            HttpEntity<String> entity = new HttpEntity<>(jsonPayload, headers);

            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
            int statusCode = response.getStatusCodeValue();
            // Si la tâche existait, Supabase retourne 204 No Content ou 200 avec le JSON
            return statusCode == 204 || statusCode == 200 || statusCode == 201;
        } catch (Exception e) {
            System.err.println("Erreur resetTask: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Supprime une tâche spécifique
     * @param taskId ID de la tâche
     * @return true si la tâche a été supprimée
     */
    public boolean deleteTask(String taskId) {
        try {
            String url = supabaseConfig.getUrl() + "/rest/v1/analysis_tasks?id=eq." + taskId;
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.DELETE, entity, String.class);
            int statusCode = response.getStatusCodeValue();
            return statusCode == 204 || statusCode == 200;
        } catch (Exception e) {
            System.err.println("Erreur deleteTask: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}