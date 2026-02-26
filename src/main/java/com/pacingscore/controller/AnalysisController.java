package com.pacingscore.controller;

import com.pacingscore.service.YouTubeCrawlerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.List;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    @Autowired
    private YouTubeCrawlerService crawlerService;
    
    /**
     * Endpoint pour démarrer l'analyse automatique
     * Recherche et analyse des vidéos YouTube
     */
    @PostMapping("/crawl")
    public ResponseEntity<List<YouTubeCrawlerService.VideoAnalysis>> crawlAndAnalyze(
            @RequestParam String searchTerm) {
        
        List<YouTubeCrawlerService.VideoAnalysis> results = crawlerService.crawlAndAnalyze(searchTerm);
        return ResponseEntity.ok(results);
    }
    
    /**
     * Endpoint pour populer la base de données avec des dessins animés
     */
    @PostMapping("/populate")
    public ResponseEntity<String> populateDatabase() {
        // Rechercher des catégories de dessins animés
        String[] searchTerms = {
            "dessin animé enfant calm",
            "dessin animé bébé",
            "cartoon for kids slow",
            "histoire pour les tout-petits",
            "dessin animé éducatif",
            "video calme enfants",
            "dodo enfants petit"
        };
        
        for (String term : searchTerms) {
            try {
                crawlerService.crawlAndAnalyze(term);
                Thread.sleep(1000); // Attendre entre les requêtes
            } catch (InterruptedException e) {
                // Continuer
            }
        }
        
        return ResponseEntity.ok("Base de données popuulée avec succès");
    }
    
    /**
     * Endpoint pour rechercher des vidéos par catégorie
     */
    @GetMapping("/search")
    public ResponseEntity<List<YouTubeCrawlerService.VideoAnalysis>> search(
            @RequestParam String query,
            @RequestParam(defaultValue = "0+") String age,
            @RequestParam(defaultValue = "0") double minScore) {
        
        // Filtrer les résultats
        List<YouTubeCrawlerService.VideoAnalysis> results = crawlerService.crawlAndAnalyze(query);
        
        // Filtrer par âge
        if (!age.equals("0+")) {
            results.removeIf(vid -> !vid.getAgeRating().equals(age));
        }
        
        // Filtrer par score minimum
        if (minScore > 0) {
            results.removeIf(vid -> vid.getPacingScore() < minScore);
        }
        
        return ResponseEntity.ok(results);
    }
}