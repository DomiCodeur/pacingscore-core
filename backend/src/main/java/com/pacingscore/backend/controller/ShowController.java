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
            @RequestParam(required = false) String type,
            @Parameter(in = ParameterIn.QUERY, description = "Nombre d'éléments à retourner (pagination)", schema = @Schema(type = "number", defaultValue = "50"))
            @RequestParam(required = false) Integer limit,
            @Parameter(in = ParameterIn.QUERY, description = "Offset pour pagination", schema = @Schema(type = "number", defaultValue = "0"))
            @RequestParam(required = false) Integer offset,
            @Parameter(in = ParameterIn.QUERY, description = "Ne retourner que les shows avec score réel (vérifiés)", schema = @Schema(type = "boolean", defaultValue = "false"))
            @RequestParam(required = false) Boolean verified) {
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            
            int queryLimit = (limit != null && limit > 0) ? limit : 50;
            int queryOffset = (offset != null && offset > 0) ? offset : 0;
            
            StringBuilder query = new StringBuilder("?order=created_at.desc");
            query.append("&limit=").append(queryLimit);
            if (queryOffset > 0) {
                query.append("&offset=").append(queryOffset);
            }
            if (search != null && !search.isEmpty()) {
                query.append("&title=ilike.%").append(search).append("%");
            }
            if (age != null && !age.equals("all") && !age.equals("0+") && !age.equals("0 ")) {
                query.append("&age_recommendation=eq.").append(age.replace(" ", "+"));
            }
            if (minScore > 0) {
                query.append("&composite_score=gte.").append(minScore);
            }
            if (type != null && !type.isEmpty()) {
                query.append("&media_type=eq.").append(type);
            }
            // Note: verified filter n'est plus utile car la vue ne contient que des shows vérifiés
            
            String endpoint = supabaseConfig.getUrl() + "/rest/v1/shows_verified" + query;
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<List> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, List.class);
            
            List<Map<String, Object>> shows = (List<Map<String, Object>>) response.getBody();
            if (shows == null) shows = new ArrayList<>();
            
            // Mapper directement au format Show
            List<Map<String, Object>> result = new ArrayList<>();
            for (Map<String, Object> row : shows) {
                Map<String, Object> mapped = new HashMap<>();
                
                // id: tmdb_id en integer
                String tmdbIdStr = String.valueOf(row.get("tmdb_id"));
                try {
                    mapped.put("id", Integer.parseInt(tmdbIdStr));
                } catch (NumberFormatException e) {
                    mapped.put("id", 0);
                }
                mapped.put("tmdb_id", tmdbIdStr);
                
                // Titre
                String title = (String) row.get("title");
                mapped.put("title", title != null ? title : "");
                
                // Poster
                Object poster = row.get("poster_path");
                if (poster != null) {
                    String posterPath = poster.toString();
                    if (posterPath.startsWith("http")) {
                        mapped.put("poster_path", posterPath);
                    } else {
                        mapped.put("poster_path", "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath);
                    }
                } else {
                    mapped.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                }
                
                // Score
                Object scoreObj = row.get("composite_score");
                double score = (scoreObj instanceof Number) ? ((Number) scoreObj).doubleValue() : 0;
                mapped.put("composite_score", score);
                
                // Évaluation couleur
                String color;
                if (score >= 60) color = "green";
                else if (score >= 45) color = "lime";
                else if (score >= 25) color = "yellow";
                else color = "red";
                mapped.put("evaluation_color", color);
                
                // Label
                String label;
                if (score >= 60) label = "LENT";
                else if (score >= 45) label = "BON";
                else if (score >= 25) label = "MODÉRÉ";
                else label = "RAPIDE";
                mapped.put("evaluation_label", label);
                mapped.put("evaluation_description", "");
                
                // Âge
                String ageRating = (String) row.get("age_recommendation");
                mapped.put("age_recommendation", ageRating != null ? ageRating : "0+");
                
                // média type
                Object mediaType = row.get("media_type");
                if (mediaType != null) {
                    mapped.put("media_type", mediaType.toString());
                }
                
                // Description
                Object desc = row.get("description");
                if (desc != null) mapped.put("description", desc.toString());
                
                // Vidéo
                Object videoUrl = row.get("video_url");
                if (videoUrl != null) mapped.put("video_path", videoUrl.toString());
                else mapped.put("video_path", "Analyse vidéo disponible");
                
                // Détails analyse
                Object sceneDetails = row.get("scene_details");
                if (sceneDetails instanceof Map) {
                    Map<String, Object> details = (Map<String, Object>) sceneDetails;
                    Integer numScenes = null;
                    Double cpm = null;
                    if (details.get("total_cuts") instanceof Number) {
                        numScenes = ((Number) details.get("total_cuts")).intValue();
                    }
                    if (details.get("cuts_per_minute") instanceof Number) {
                        cpm = ((Number) details.get("cuts_per_minute")).doubleValue();
                    }
                    mapped.put("num_scenes", numScenes);
                    mapped.put("cuts_per_minute", cpm);
                    mapped.put("analysis_details", details);
                }
                
                Object videoDur = row.get("video_duration");
                if (videoDur instanceof Number) {
                    mapped.put("video_duration", ((Number) videoDur).doubleValue());
                }
                
                Object motion = row.get("motion_intensity");
                if (motion instanceof Number) {
                    mapped.put("motion_intensity", ((Number) motion).doubleValue());
                }
                
                Object src = row.get("source");
                if (src != null) {
                    mapped.put("source", src.toString());
                }
                
                // is_verified toujours true car vue = vérifiés
                mapped.put("is_verified", true);
                
                result.add(mapped);
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
            @RequestParam(required = false) String type,
            @Parameter(in = ParameterIn.QUERY, description = "Offset pour pagination", schema = @Schema(type = "number", defaultValue = "0"))
            @RequestParam(required = false) Integer offset) {
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            
            StringBuilder query = new StringBuilder("?order=created_at.desc&limit=").append(limit);
            if (offset != null && offset > 0) {
                query.append("&offset=").append(offset);
            }
            if (type != null && !type.isEmpty()) {
                query.append("&media_type=eq.").append(type);
            }
            
            String endpoint = supabaseConfig.getUrl() + "/rest/v1/shows_verified" + query;
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<List> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, List.class);
            
            List<Map<String, Object>> shows = (List<Map<String, Object>>) response.getBody();
            if (shows == null) return ResponseEntity.ok(new ArrayList<>());
            
            // Mapper identique à getShows
            List<Map<String, Object>> result = new ArrayList<>();
            for (Map<String, Object> row : shows) {
                Map<String, Object> mapped = new HashMap<>();
                String tmdbIdStr = String.valueOf(row.get("tmdb_id"));
                try { mapped.put("id", Integer.parseInt(tmdbIdStr)); } catch (NumberFormatException e) { mapped.put("id", 0); }
                mapped.put("tmdb_id", tmdbIdStr);
                String title = (String) row.get("title");
                mapped.put("title", title != null ? title : "");
                Object poster = row.get("poster_path");
                if (poster != null) {
                    String posterPath = poster.toString();
                    if (!posterPath.startsWith("http")) {
                        posterPath = "https://image.tmdb.org/t/p/w500" + (posterPath.startsWith("/") ? "" : "/") + posterPath;
                    }
                    mapped.put("poster_path", posterPath);
                } else {
                    mapped.put("poster_path", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&q=80");
                }
                Object scoreObj = row.get("composite_score");
                double score = (scoreObj instanceof Number) ? ((Number) scoreObj).doubleValue() : 0;
                mapped.put("composite_score", score);
                String color = score >= 60 ? "green" : score >= 45 ? "lime" : score >= 25 ? "yellow" : "red";
                mapped.put("evaluation_color", color);
                String label = score >= 60 ? "LENT" : score >= 45 ? "BON" : score >= 25 ? "MODÉRÉ" : "RAPIDE";
                mapped.put("evaluation_label", label);
                mapped.put("evaluation_description", "");
                String ageRating = (String) row.get("age_recommendation");
                mapped.put("age_recommendation", ageRating != null ? ageRating : "0+");
                Object mediaType = row.get("media_type");
                if (mediaType != null) mapped.put("media_type", mediaType.toString());
                Object desc = row.get("description");
                if (desc != null) mapped.put("description", desc.toString());
                Object videoUrl = row.get("video_url");
                if (videoUrl != null) mapped.put("video_path", videoUrl.toString());
                else mapped.put("video_path", "Analyse vidéo disponible");
                Object sceneDetails = row.get("scene_details");
                if (sceneDetails instanceof Map) {
                    Map<String, Object> details = (Map<String, Object>) sceneDetails;
                    Integer numScenes = null; Double cpm = null;
                    if (details.get("total_cuts") instanceof Number) numScenes = ((Number) details.get("total_cuts")).intValue();
                    if (details.get("cuts_per_minute") instanceof Number) cpm = ((Number) details.get("cuts_per_minute")).doubleValue();
                    mapped.put("num_scenes", numScenes);
                    mapped.put("cuts_per_minute", cpm);
                    mapped.put("analysis_details", details);
                }
                Object videoDur = row.get("video_duration");
                if (videoDur instanceof Number) mapped.put("video_duration", ((Number) videoDur).doubleValue());
                Object motion = row.get("motion_intensity");
                if (motion instanceof Number) mapped.put("motion_intensity", ((Number) motion).doubleValue());
                Object src = row.get("source");
                if (src != null) mapped.put("source", src.toString());
                mapped.put("is_verified", true);
                
                result.add(mapped);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @Operation(summary = "Compte le nombre de shows avec score réel (analysés vidéo)",
               description = "Retourne le nombre total de shows qui ont été réellement analysés (présence d'un score dans mollo_scores).",
               responses = {
                   @ApiResponse(responseCode = "200", description = "Compte récupéré avec succès",
                       content = @Content(mediaType = "application/json")),
                   @ApiResponse(responseCode = "500", description = "Erreur serveur")
               })
    @GetMapping("/count/verified")
    public ResponseEntity<Map<String, Integer>> getVerifiedCount() {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("apikey", supabaseConfig.getKey());
            headers.set("Authorization", "Bearer " + supabaseConfig.getKey());
            headers.set("Prefer", "count=exact");
            
            String endpoint = supabaseConfig.getUrl() + "/rest/v1/mollo_scores?select=tmdb_id&limit=1";
            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<byte[]> response = restTemplate.exchange(endpoint, HttpMethod.GET, entity, byte[].class);
            
            // Header Content-Range: "0-0/671" ou "*/671" -> le total est après le dernier "/"
            String contentRange = response.getHeaders().getFirst("Content-Range");
            int totalCount = 0;
            if (contentRange != null) {
                int slashIdx = contentRange.lastIndexOf('/');
                if (slashIdx != -1 && slashIdx + 1 < contentRange.length()) {
                    String totalStr = contentRange.substring(slashIdx + 1);
                    // Parfois Supabase retourne "*,*" pour le range quand on ne demande pas de count exact
                    // Mais avec limit=1 on devrait avoir un nombre
                    try {
                        totalCount = Integer.parseInt(totalStr);
                    } catch (NumberFormatException e) {
                        // Si on ne peut pas parser, on laisse à 0
                    }
                }
            }
            
            Map<String, Integer> result = new HashMap<>();
            result.put("count", totalCount);
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}