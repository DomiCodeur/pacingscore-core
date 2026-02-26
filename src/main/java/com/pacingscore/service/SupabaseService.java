package com.pacingscore.service;

import com.pacingscore.config.SupabaseConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class SupabaseService {
    
    @Autowired
    private SupabaseConfig supabaseConfig;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * Sauvegarde une analyse de série dans Supabase
     */
    public void saveShowAnalysis(TMDBService.ShowInfo show) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses";
        
        Map<String, Object> data = new HashMap<>();
        data.put("tmdb_id", show.getId());
        data.put("title", show.getTitle());
        data.put("description", show.getDescription());
        data.put("pacing_score", show.getPacingScore());
        data.put("age_rating", show.getAgeRating());
        
        // Stocker les données TMDB en JSON
        Map<String, Object> tmdbData = new HashMap<>();
        tmdbData.put("poster_path", show.getPosterPath());
        tmdbData.put("backdrop_path", show.getBackdropPath());
        tmdbData.put("first_air_date", show.getFirstAirDate());
        data.put("tmdb_data", tmdbData);
        
        // Configurer les headers
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(data, headers);
        
        try {
            restTemplate.postForEntity(endpoint, request, String.class);
            System.out.println("Sauvegardé: " + show.getTitle());
        } catch (Exception e) {
            System.err.println("Erreur sauvegarde: " + show.getTitle() + " - " + e.getMessage());
        }
    }
    
    /**
     * Vérifie si une série existe déjà dans la base
     */
    public boolean showExists(int tmdbId) {
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses";
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        headers.set("Prefer", "count=exact");
        
        HttpEntity<String> request = new HttpEntity<>(headers);
        
        try {
            // Rechercher par tmdb_id
            String url = endpoint + "?tmdb_id=eq." + tmdbId;
            ResponseEntity<String> response = restTemplate.exchange(
                url, HttpMethod.GET, request, String.class
            );
            
            // Si le count header indique qu'il y a des résultats
            String count = response.getHeaders().getFirst("Content-Range");
            return count != null && Integer.parseInt(count.split("/")[1]) > 0;
        } catch (Exception e) {
            return false;
        }
    }
}