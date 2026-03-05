package com.pacingscore.backend.controller;

import com.pacingscore.backend.config.SupabaseConfig;
import com.pacingscore.backend.service.SupabaseService;
import com.pacingscore.backend.service.TMDBService;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
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
    
    @Operation(summary = "Récupère la liste des vidéos analysées",
               description = "Retourne une liste paginée de vidéos avec leurs scores de rythme, images et métadonnées. Tri par score décroissant.",
               responses = {
                   @ApiResponse(responseCode = "200", description = "Liste récupérée avec succès",
                       content = @Content(mediaType = "application/json")),
                   @ApiResponse(responseCode = "500", description = "Erreur serveur")
               })
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getShows(
            @Parameter(in = ParameterIn.QUERY, description = "Tranche d'âge recommandée (ex: 0+, 3+, 6+, 10+, 16+)", schema = @Schema(type = "string", defaultValue = "0+"))
            @RequestParam(defaultValue = "0+") String age,
            @Parameter(in = ParameterIn.QUERY, description = "Score minimum de rythme (0-100)", schema = @Schema(type = "number", defaultValue = "0"))
            @RequestParam(defaultValue = "0") double minScore,
            @Parameter(in = ParameterIn.QUERY, description = "Filtrer par titre (recherche partielle)", schema = @Schema(type = "string"))
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
                    
                    // 1. FORCER LE TITRE
                    String title = (String) show.get("title");
                    Map<String, Object> meta = parseMetadata(show.get("metadata"));
                    if (meta != null && meta.get("fr_title") != null) {
                        title = (String) meta.get("fr_title");
                    } else if (title == null || title.isEmpty()) {
                        title = (String) show.get("video_path");
                    }
                    mappedShow.put("title", title);
                    
                    // 2. Age rating : prioriser age_rating si display_age vaut "0+" (défaut)
                    String displayAge = meta != null ? (String) meta.get("display_age") : null;
                    Object ageRatingObj = show.get("age_rating");
                    String ageRating = "0+";
                    if (ageRatingObj instanceof String) {
                        ageRating = (String) ageRatingObj;
                    } else if (ageRatingObj != null) {
                        ageRating = ageRatingObj.toString();
                    }
                    String finalAge = (displayAge != null && !displayAge.equals("0+")) ? displayAge : ageRating;
                    mappedShow.put("age_recommendation", finalAge);

                    // 3. Récupération image
                    String posterPath = null;
                    
                    // 3a. Vérifier tmdb_data->poster_path
                    if (show.containsKey("tmdb_data") && show.get("tmdb_data") instanceof Map) {
                        posterPath = (String) ((Map) show.get("tmdb_data")).get("poster_path");
                    }
                    
                    // 3b. Chercher par TMDB ID si pas d'image
                    if ((posterPath == null || posterPath.isEmpty()) && meta != null) {
                        Object tmdbIdObj = meta.get("tmdb_id");
                        if (tmdbIdObj != null) {
                            try {
                                int tmdbId = Integer.parseInt(tmdbIdObj.toString());
                                TMDBService.ShowInfo tmdbInfo = tmdbService.getShowDetailsById(tmdbId);
                                if (tmdbInfo != null && tmdbInfo.getPosterPath() != null && !tmdbInfo.getPosterPath().isEmpty()) {
                                    posterPath = tmdbInfo.getPosterPath();
                                    // Enrichir description si manquante
                                    if (mappedShow.get("description") == null && tmdbInfo.getDescription() != null) {
                                        mappedShow.put("description", tmdbInfo.getDescription());
                                    }
                                }
                            } catch (Exception e) { /* Silencieux */ }
                        }
                    }
                    
                    // 3c. Fallback par titre (fr + en)
                    if ((posterPath == null || posterPath.isEmpty()) && title != null) {
                        try {
                            TMDBService.ShowInfo tmdbInfo = tmdbService.findSingleShowWithFallback(title);
                            if (tmdbInfo != null && tmdbInfo.getPosterPath() != null && !tmdbInfo.getPosterPath().isEmpty()) {
                                posterPath = tmdbInfo.getPosterPath();
                                if (mappedShow.get("description") == null && tmdbInfo.getDescription() != null) {
                                    mappedShow.put("description", tmdbInfo.getDescription());
                                }
                            }
                        } catch (Exception e) { /* Silencieux */ }
                    }

                    // 3d. Appliquer le chemin (avec URL TMDB si nécessaire)
                    if (posterPath != null && !posterPath.isEmpty()) {
                        if (posterPath.startsWith("http")) {
                            mappedShow.put("poster_path", posterPath);
                        } else {
                            mappedShow.put("poster_path", "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath);
                        }
                    } else {
                        // FALLBACK ULTIME : image Unsplash (已验证加载)
                        mappedShow.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                    }
                    
                    // 4. Label d'évaluation (avec protection NaN)
                    Object pacingScoreObj = show.get("pacing_score");
                    double compositeScore = 0;
                    if (pacingScoreObj instanceof Number) {
                        double val = ((Number) pacingScoreObj).doubleValue();
                        compositeScore = Double.isNaN(val) ? 0 : val;
                    } else if (pacingScoreObj instanceof String) {
                        try {
                            String str = ((String) pacingScoreObj).trim();
                            if (!str.isEmpty()) {
                                double val = Double.parseDouble(str);
                                compositeScore = Double.isNaN(val) ? 0 : val;
                            }
                        } catch (NumberFormatException e) {
                            compositeScore = 0;
                        }
                    }
                    mappedShow.put("composite_score", compositeScore);
                    
                    if (compositeScore >= 60) mappedShow.put("evaluation_label", "LENT");
                    else if (compositeScore >= 45) mappedShow.put("evaluation_label", "BON");
                    else if (compositeScore >= 25) mappedShow.put("evaluation_label", "MODÉRÉ");
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
