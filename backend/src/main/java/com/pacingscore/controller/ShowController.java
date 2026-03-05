package com.pacingscore.controller;

import com.pacingscore.config.SupabaseConfig;
import com.pacingscore.service.SupabaseService;
import com.pacingscore.service.TMDBService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;

@RestController
@RequestMapping("/api/shows")
@CrossOrigin(origins = "*")
public class ShowController {
    
    @Autowired
    private SupabaseService supabaseService;

    @Autowired
    private SupabaseConfig supabaseConfig;
    
    @Autowired
    private TMDBService tmdbService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    // Helper method to parse metadata from Supabase
    private Map<String, Object> parseMetadata(Object metaObj) {
        if (metaObj == null) {
            return new HashMap<>();
        }
        if (metaObj instanceof Map) {
            return (Map<String, Object>) metaObj;
        }
        if (metaObj instanceof String) {
            try {
                ObjectMapper mapper = new ObjectMapper();
                return mapper.readValue((String) metaObj, new com.fasterxml.jackson.core.type.TypeReference<Map<String,Object>>() {});
            } catch (Exception e) {
                e.printStackTrace();
                return new HashMap<>();
            }
        }
        return new HashMap<>();
    }
    
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getShows(
            @RequestParam(defaultValue = "0+") String age,
            @RequestParam(defaultValue = "0") double minScore,
            @RequestParam(required = false) String search) {
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("apikey", supabaseConfig.getKey());
        headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
        
        StringBuilder query = new StringBuilder("?order=pacing_score.desc&limit=200");
        if (search != null && !search.isEmpty()) {
            query.append("&title=ilike.%" + search + "%");
        }
        if (!age.equals("0+")) {
            query.append("&age_rating=eq.").append(age);
        }
        if (minScore > 0) {
            query.append("&pacing_score=gte.").append(minScore);
        }
        
        String endpoint = supabaseConfig.getUrl() + "/rest/v1/video_analyses" + query;
        
        try {
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<List> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, List.class);
            
            List<Map<String, Object>> shows = (List<Map<String, Object>>) response.getBody();
            List<Map<String, Object>> result = new ArrayList<>();
            
            if (shows != null) {
                for (Map<String, Object> show : shows) {
                    Map<String, Object> mappedShow = new HashMap<>(show);
                    
                    // 1. FORCER LE TITRE (video_path contient le nom dans ta base)
                    String title = (String) show.get("title");
                    Map<String, Object> meta = parseMetadata(show.get("metadata"));
                    if (meta != null && meta.get("fr_title") != null) title = (String) meta.get("fr_title"); else if (title == null || title.isEmpty()) title = (String) show.get("video_path");
                    mappedShow.put("title", title);
                    
                    // 2. Mapping des scores
                    mappedShow.put("composite_score", show.getOrDefault("pacing_score", 0));
                    if (meta != null && meta.get("display_age") != null) mappedShow.put("age_recommendation", meta.get("display_age")); else mappedShow.put("age_recommendation", show.getOrDefault("age_rating", "0+"));
                    
                    // 3. RECUPERATION IMAGE AUTOMATIQUE
                    String posterPath = null;
                    if (show.containsKey("tmdb_data") && show.get("tmdb_data") instanceof Map) {
                        posterPath = (String) ((Map) show.get("tmdb_data")).get("poster_path");
                    }
                    
                    // Si pas d'image, on cherche sur TMDB avec le titre
                    if ((posterPath == null || posterPath.isEmpty()) && title != null) {
                        try {
                            TMDBService.ShowInfo tmdbInfo = tmdbService.findSingleShow(title);
                            if (tmdbInfo != null) {
                                posterPath = tmdbInfo.getPosterPath();
                                // On en profite pour enrichir la description si elle manque
                                if (mappedShow.get("description") == null) mappedShow.put("description", tmdbInfo.getDescription());
                            }
                        } catch (Exception e) { /* Silencieux si TMDB échoue */ }
                    }

                    if (posterPath != null && !posterPath.isEmpty()) {
                        if (posterPath.startsWith("http")) {
                            mappedShow.put("poster_path", posterPath);
                        } else {
                            mappedShow.put("poster_path", "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath);
                        }
                    } else {
                        // FALLBACK ULTIME : Miniature Dailymotion si possible, sinon image Cartoon
                        String videoUrl = (String) show.get("video_url");
                        if (videoUrl != null && videoUrl.contains("dailymotion.com/video/")) {
                            String vidId = videoUrl.substring(videoUrl.lastIndexOf("/") + 1);
                            mappedShow.put("poster_path", "https://www.dailymotion.com/thumbnail/video/" + vidId);
                        } else {
                            mappedShow.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                        }
                    }
                    
                    // 4. Label d'évaluation
                    double score = 0;
                    Object s = show.get("pacing_score");
                    if (s instanceof Number) score = ((Number) s).doubleValue();
                    
                    if (score >= 60) mappedShow.put("evaluation_label", "LENT");
                    else if (score >= 45) mappedShow.put("evaluation_label", "BON");
                    else if (score >= 25) mappedShow.put("evaluation_label", "MODÉRÉ");
                    else mappedShow.put("evaluation_label", "RAPIDE");
                    
                    result.add(mappedShow);
                }
            }
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
