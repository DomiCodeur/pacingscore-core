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
import java.util.stream.Collectors;

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
               description = "Retourne une liste paginée de vidéos avec leurs scores de rythme (réel si disponible, sinon estimé), images et métadonnées. Tri par score décroissant.",
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
            @RequestParam(required = false) String search,
            @Parameter(in = ParameterIn.QUERY, description = "Filtrer par type de média (movie ou tv)", schema = @Schema(type = "string"))
            @RequestParam(required = false) String type) {
        
        try {
            // 1. Récupérer les estimations depuis metadata_estimations
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            
            StringBuilder query = new StringBuilder("?order=estimated_score.desc&limit=200");
            if (search != null && !search.isEmpty()) {
                query.append("&title=ilike.%").append(search).append("%");
            }
            if (!age.equals("0+")) {
                query.append("&age_rating_guess=eq.").append(age);
            }
            if (minScore > 0) {
                query.append("&estimated_score=gte.").append(minScore);
            }
            if (type != null && !type.isEmpty()) {
                query.append("&media_type=eq.").append(type);
            }
            
            String endpoint = supabaseConfig.getUrl() + "/rest/v1/metadata_estimations" + query;
            
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<List> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, List.class);
            
            List<Map<String, Object>> estimations = (List<Map<String, Object>>) response.getBody();
            if (estimations == null) estimations = new ArrayList<>();
            
            // 2. Si on a des estimations, récupérer les scores réels correspondants en batch
            List<String> tmdbIds = estimations.stream()
                .map(est -> String.valueOf(est.get("tmdb_id")))
                .collect(Collectors.toList());
            
            Map<String, Map<String, Object>> realScoresMap = new HashMap<>();
            if (!tmdbIds.isEmpty()) {
                // Construire la clause IN (malheureusement PostgREST n'accepte pas plus de 5 IDs dans un in? On peut faire une requête par lot de 5, ou alors une requête globale avec?tmdb_id=in.(id1,id2,...)
                // Simplifions: on fait une requête qui récupère tous les mollo_scores dont le tmdb_id est dans la liste
                String idsParam = String.join(",", tmdbIds);
                String scoresEndpoint = supabaseConfig.getUrl() + "/rest/v1/mollo_scores?tmdb_id=in.(" + idsParam + ")";
                ResponseEntity<List> scoresResponse = restTemplate.exchange(scoresEndpoint, HttpMethod.GET, entity, List.class);
                List<Map<String, Object>> realScores = (List<Map<String, Object>>) scoresResponse.getBody();
                if (realScores != null) {
                    for (Map<String, Object> scoreEntry : realScores) {
                        String id = String.valueOf(scoreEntry.get("tmdb_id"));
                        realScoresMap.put(id, scoreEntry);
                    }
                }
            }
            
            // 3. Construire la réponse finale (format compatible avec l'interface Show frontend)
            List<Map<String, Object>> result = new ArrayList<>();
            for (Map<String, Object> est : estimations) {
                Map<String, Object> mappedShow = new HashMap<>();
                String tmdbIdStr = String.valueOf(est.get("tmdb_id"));
                
                // Score: priorité au score réel s'il existe
                Map<String, Object> realScoreEntry = realScoresMap.get(tmdbIdStr);
                double compositeScore; // pacing_score
                boolean isVerified = false;
                Double averageShotLength = null; // peut être null
                Integer numScenes = null;
                Map<String, Object> analysisDetails = null;
                
                if (realScoreEntry != null && realScoreEntry.get("real_score") != null) {
                    Object rs = realScoreEntry.get("real_score");
                    if (rs instanceof Number) {
                        compositeScore = ((Number) rs).doubleValue();
                        isVerified = true;
                    } else {
                        compositeScore = 0;
                    }
                    
                    // Extraire les données de scene_details si présent
                    Object sceneDetailsObj = realScoreEntry.get("scene_details");
                    if (sceneDetailsObj instanceof Map) {
                        Map<String, Object> sceneDetails = (Map<String, Object>) sceneDetailsObj;
                        Object cpm = sceneDetails.get("cuts_per_minute");
                        if (cpm instanceof Number) {
                            averageShotLength = 60.0 / ((Number) cpm).doubleValue(); // estimation approximative
                        }
                        Object totalCuts = sceneDetails.get("total_cuts");
                        if (totalCuts instanceof Number) {
                            numScenes = ((Number) totalCuts).intValue();
                        }
                        // On peut aussi passer sceneDetails comme analysis_details
                        analysisDetails = sceneDetails;
                    }
                    
                    // vidéo URL
                    if (realScoreEntry.get("video_url") != null) {
                        mappedShow.put("video_path", realScoreEntry.get("video_url"));
                    } else {
                        mappedShow.put("video_path", "Analyse vidéo disponible");
                    }
                } else {
                    // Estimation TMDB
                    Object es = est.get("estimated_score");
                    if (es instanceof Number) {
                        compositeScore = ((Number) es).doubleValue();
                    } else {
                        compositeScore = 0;
                    }
                    mappedShow.put("video_path", "Estimation TMDB - Pas encore analysée");
                }
                
                // id: on utilise tmdb_id convertible en number (parser)
                try {
                    mappedShow.put("id", Integer.parseInt(tmdbIdStr));
                } catch (NumberFormatException e) {
                    mappedShow.put("id", 0);
                }
                
                // composite_score
                mappedShow.put("composite_score", compositeScore);
                
                // average_shot_length (null si pas d'analyse)
                mappedShow.put("average_shot_length", averageShotLength);
                
                // num_scenes (null si pas d'analyse)
                mappedShow.put("num_scenes", numScenes);
                
                // evaluation_label (calculé)
                String evalLabel;
                if (compositeScore >= 60) evalLabel = "LENT";
                else if (compositeScore >= 45) evalLabel = "BON";
                else if (compositeScore >= 25) evalLabel = "MODÉRÉ";
                else evalLabel = "RAPIDE";
                mappedShow.put("evaluation_label", evalLabel);
                
                // evaluation_description (texte libre)
                mappedShow.put("evaluation_description", "");
                
                // evaluation_color (déduit du score)
                String evalColor;
                if (compositeScore >= 60) evalColor = "green";
                else if (compositeScore >= 45) evalColor = "lime";
                else if (compositeScore >= 25) evalColor = "yellow";
                else evalColor = "red";
                mappedShow.put("evaluation_color", evalColor);
                
                // age_recommendation (provenance de age_rating_guess)
                String ageRating = (String) est.get("age_rating_guess");
                mappedShow.put("age_recommendation", ageRating != null ? ageRating : "0+");
                
                // media_type (movie ou tv)
                Object mediaType = est.get("media_type");
                if (mediaType != null) {
                    mappedShow.put("media_type", mediaType.toString());
                }
                
                // Titre
                String title = (String) est.get("title");
                if (title == null || title.isEmpty()) {
                    Map<String, Object> meta = parseMetadata(est.get("metadata"));
                    title = meta != null ? (String) meta.get("fr_title") : null;
                }
                mappedShow.put("title", title);
                
                // Description depuis metadata
                Map<String, Object> meta = parseMetadata(est.get("metadata"));
                if (meta != null) {
                    Object desc = meta.get("description");
                    if (desc != null) mappedShow.put("description", desc);
                    Object poster = meta.get("poster_path");
                    if (poster != null) {
                        String posterPath = poster.toString();
                        if (posterPath.startsWith("http")) {
                            mappedShow.put("poster_path", posterPath);
                        } else {
                            mappedShow.put("poster_path", "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath);
                        }
                    }
                }
                
                // Fallback poster si manquant
                if (!mappedShow.containsKey("poster_path") || mappedShow.get("poster_path") == null) {
                    mappedShow.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                }
                
                // analysis_details (null si pas d'analyse)
                mappedShow.put("analysis_details", analysisDetails);
                
                // Nouvelles données vidéo (si disponibles)
                if (realScoreEntry != null) {
                    Object vd = realScoreEntry.get("video_duration");
                    if (vd instanceof Number) {
                        mappedShow.put("video_duration", ((Number) vd).doubleValue());
                    }
                    Object cpm = realScoreEntry.get("cuts_per_minute");
                    if (cpm instanceof Number) {
                        mappedShow.put("cuts_per_minute", ((Number) cpm).doubleValue());
                    }
                    Object mi = realScoreEntry.get("motion_intensity");
                    if (mi instanceof Number) {
                        mappedShow.put("motion_intensity", ((Number) mi).doubleValue());
                    }
                    Object src = realScoreEntry.get("source");
                    if (src != null) {
                        mappedShow.put("source", src.toString());
                    }
                    Object vtype = realScoreEntry.get("video_type");
                    if (vtype != null) {
                        mappedShow.put("video_type", vtype.toString());
                    }
                }
                
                // Ajouter le tmdb_id pour le front si besoin
                mappedShow.put("tmdb_id", tmdbIdStr);
                
                result.add(mappedShow);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @Operation(summary = "Récupère les dernières séries/films ajoutés",
               description = "Retourne les shows les plus récemment ajoutés dans metadata_estimations, triés par created_at. Optionnel filter par media_type (movie/tv).",
               responses = {
                   @ApiResponse(responseCode = "200", description = "Liste récupérée avec succès",
                       content = @Content(mediaType = "application/json")),
                   @ApiResponse(responseCode = "500", description = "Erreur serveur")
               })
    @GetMapping("/latest")
    public ResponseEntity<List<Map<String, Object>>> getLatestShows(
            @Parameter(in = ParameterIn.QUERY, description = "Nombre d'éléments à retourner", schema = @Schema(type = "number", defaultValue = "10"))
            @RequestParam(defaultValue = "10") int limit,
            @Parameter(in = ParameterIn.QUERY, description = "Filtrer par type de média (movie ou tv)", schema = @Schema(type = "string"))
            @RequestParam(required = false) String type) {
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            
            StringBuilder query = new StringBuilder("?order=created_at.desc&limit=").append(limit);
            if (type != null && !type.isEmpty()) {
                query.append("&media_type=eq.").append(type);
            }
            query.append("&select=*");
            
            String endpoint = supabaseConfig.getUrl() + "/rest/v1/metadata_estimations" + query;
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<List> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, List.class);
            
            List<Map<String, Object>> estimations = (List<Map<String, Object>>) response.getBody();
            if (estimations == null) {
                return ResponseEntity.ok(new ArrayList<>());
            }
            
            // Récupérer les scores réels correspondants (batch)
            List<String> tmdbIds = estimations.stream()
                .map(est -> String.valueOf(est.get("tmdb_id")))
                .collect(Collectors.toList());
            
            Map<String, Map<String, Object>> realScoresMap = new HashMap<>();
            if (!tmdbIds.isEmpty()) {
                String idsParam = String.join(",", tmdbIds);
                String scoresEndpoint = supabaseConfig.getUrl() + "/rest/v1/mollo_scores?tmdb_id=in.(" + idsParam + ")";
                ResponseEntity<List> scoresResponse = restTemplate.exchange(scoresEndpoint, HttpMethod.GET, entity, List.class);
                List<Map<String, Object>> realScores = (List<Map<String, Object>>) scoresResponse.getBody();
                if (realScores != null) {
                    for (Map<String, Object> scoreEntry : realScores) {
                        String id = String.valueOf(scoreEntry.get("tmdb_id"));
                        realScoresMap.put(id, scoreEntry);
                    }
                }
            }
            
            // Construire la réponse finale (même format que getShows)
            List<Map<String, Object>> result = new ArrayList<>();
            for (Map<String, Object> est : estimations) {
                Map<String, Object> mappedShow = new HashMap<>();
                String tmdbIdStr = String.valueOf(est.get("tmdb_id"));
                Map<String, Object> realScoreEntry = realScoresMap.get(tmdbIdStr);
                
                double compositeScore;
                boolean isVerified = false;
                Double averageShotLength = null;
                Integer numScenes = null;
                Map<String, Object> analysisDetails = null;
                
                if (realScoreEntry != null && realScoreEntry.get("real_score") != null) {
                    Object rs = realScoreEntry.get("real_score");
                    if (rs instanceof Number) {
                        compositeScore = ((Number) rs).doubleValue();
                        isVerified = true;
                    } else {
                        compositeScore = 0;
                    }
                    
                    Object sceneDetailsObj = realScoreEntry.get("scene_details");
                    if (sceneDetailsObj instanceof Map) {
                        Map<String, Object> sceneDetails = (Map<String, Object>) sceneDetailsObj;
                        Object cpm = sceneDetails.get("cuts_per_minute");
                        if (cpm instanceof Number) {
                            averageShotLength = 60.0 / ((Number) cpm).doubleValue();
                        }
                        Object totalCuts = sceneDetails.get("total_cuts");
                        if (totalCuts instanceof Number) {
                            numScenes = ((Number) totalCuts).intValue();
                        }
                        analysisDetails = sceneDetails;
                    }
                    
                    if (realScoreEntry.get("video_url") != null) {
                        mappedShow.put("video_path", realScoreEntry.get("video_url"));
                    } else {
                        mappedShow.put("video_path", "Analyse vidéo disponible");
                    }
                } else {
                    Object es = est.get("estimated_score");
                    if (es instanceof Number) {
                        compositeScore = ((Number) es).doubleValue();
                    } else {
                        compositeScore = 0;
                    }
                    mappedShow.put("video_path", "Estimation TMDB - Pas encore analysée");
                }
                
                try {
                    mappedShow.put("id", Integer.parseInt(tmdbIdStr));
                } catch (NumberFormatException e) {
                    mappedShow.put("id", 0);
                }
                
                mappedShow.put("composite_score", compositeScore);
                mappedShow.put("average_shot_length", averageShotLength);
                mappedShow.put("num_scenes", numScenes);
                mappedShow.put("analysis_details", analysisDetails);
                mappedShow.put("is_verified", isVerified);
                
                // Évaluation label (avec formule Mollo: score sur 100)
                String evalLabel;
                if (compositeScore >= 60) evalLabel = "LENT";
                else if (compositeScore >= 45) evalLabel = "BON";
                else if (compositeScore >= 25) evalLabel = "MODÉRÉ";
                else evalLabel = "RAPIDE";
                mappedShow.put("evaluation_label", evalLabel);
                mappedShow.put("evaluation_description", "");
                
                String evalColor;
                if (compositeScore >= 60) evalColor = "green";
                else if (compositeScore >= 45) evalColor = "lime";
                else if (compositeScore >= 25) evalColor = "yellow";
                else evalColor = "red";
                mappedShow.put("evaluation_color", evalColor);
                
                // Âge
                String ageRating = (String) est.get("age_rating_guess");
                mappedShow.put("age_recommendation", ageRating != null ? ageRating : "0+");
                
                // media_type
                Object mediaType = est.get("media_type");
                if (mediaType != null) {
                    mappedShow.put("media_type", mediaType.toString());
                }
                
                // Titre
                String title = (String) est.get("title");
                if (title == null || title.isEmpty()) {
                    Map<String, Object> meta = parseMetadata(est.get("metadata"));
                    title = meta != null ? (String) meta.get("fr_title") : null;
                }
                mappedShow.put("title", title);
                
                // Description
                Map<String, Object> meta = parseMetadata(est.get("metadata"));
                if (meta != null) {
                    Object desc = meta.get("description");
                    if (desc != null) mappedShow.put("description", desc);
                    Object poster = meta.get("poster_path");
                    if (poster != null) {
                        String posterPath = poster.toString();
                        if (!posterPath.startsWith("http")) {
                            posterPath = "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath;
                        }
                        mappedShow.put("poster_path", posterPath);
                    }
                }
                
                if (!mappedShow.containsKey("poster_path") || mappedShow.get("poster_path") == null) {
                    mappedShow.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                }
                
                mappedShow.put("tmdb_id", tmdbIdStr);
                
                // If worker added source/video_type fields in mollo_scores, we could include them:
                if (realScoreEntry != null) {
                    Object vd = realScoreEntry.get("video_duration");
                    if (vd instanceof Number) {
                        mappedShow.put("video_duration", ((Number) vd).doubleValue());
                    }
                    Object cpm = realScoreEntry.get("cuts_per_minute");
                    if (cpm instanceof Number) {
                        mappedShow.put("cuts_per_minute", ((Number) cpm).doubleValue());
                    }
                    Object mi = realScoreEntry.get("motion_intensity");
                    if (mi instanceof Number) {
                        mappedShow.put("motion_intensity", ((Number) mi).doubleValue());
                    }
                    Object src = realScoreEntry.get("source");
                    if (src != null) {
                        mappedShow.put("source", src.toString());
                    }
                    Object vtype = realScoreEntry.get("video_type");
                    if (vtype != null) {
                        mappedShow.put("video_type", vtype.toString());
                    }
                }
                
                result.add(mappedShow);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}