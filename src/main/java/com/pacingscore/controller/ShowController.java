package com.pacingscore.controller;

import com.pacingscore.service.SupabaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/shows")
@CrossOrigin(origins = "*")
public class ShowController {
    
    @Autowired
    private SupabaseService supabaseService;
    
    @Autowired
    private RestTemplate restTemplate;
    
    /**
     * Récupérer toutes les séries analysées
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getShows(
            @RequestParam(defaultValue = "0+") String age,
            @RequestParam(defaultValue = "0") double minScore) {
        
        // Construire l'URL de requête Supabase
        StringBuilder query = new StringBuilder("?order=pacing_score.desc");
        
        if (!age.equals("0+")) {
            query.append("&age_rating=eq.").append(age);
        }
        
        if (minScore > 0) {
            query.append("&pacing_score=gte.").append(minScore);
        }
        
        String endpoint = "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses" + query;
        
        try {
            // Appeler Supabase directement
            String response = restTemplate.getForObject(endpoint, String.class);
            
            // Convertir JSON en liste
            // (Simplifié pour l'exemple)
            return ResponseEntity.ok(List.of());
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.ok(List.of());
        }
    }
    
    /**
     * Rechercher des séries par mots-clés
     */
    @GetMapping("/search")
    public ResponseEntity<List<Map<String, Object>>> searchShows(
            @RequestParam String q,
            @RequestParam(defaultValue = "0+") String age) {
        
        // Recherche basée sur le titre
        String endpoint = "https://gjkwsrzmaecmtfozkwmw.supabase.co/rest/v1/video_analyses";
        endpoint += "?title=ilike.%" + q + "%";
        
        if (!age.equals("0+")) {
            endpoint += "&age_rating=eq." + age;
        }
        
        endpoint += "&order=pacing_score.desc";
        
        try {
            String response = restTemplate.getForObject(endpoint, String.class);
            return ResponseEntity.ok(List.of());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.ok(List.of());
        }
    }
}