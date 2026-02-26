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
     * Endpoint pour populer la base de données avec des dessins animés connus
     */
    @PostMapping("/populate")
    public ResponseEntity<String> populateDatabase() {
        // Liste PRÉDÉFINIE de dessins animés connus (pas de recherche random)
        String[] cartoonTitles = {
            // Très calmes - Pour tout-petits
            "baby shark full episode",
            "cocomelon nursery rhymes",
            "super simple songs",
            "baby einstein collection",
            "bebu loulou grammont",
            "loulou de grammont dessin animé",
            "petit lapin blanc",
            "winnie the pooh",
            "berenstain bears",
            "barbapapa",
            
            // Calmes - Pour jeunes enfants
            "peppa pig full episodes",
            "bluey full episodes",
            "paw patrol full episodes",
            "dora the explorer",
            "spidey and his amazing friends",
            "miffy dessin animé",
            "sesame street episodes",
            "blue's clues full episodes",
            "totoro ghibli",
            "my neighbor totoro",
            
            // Modérés - Pour enfants plus grands
            "pokémon episodes",
            "diego et les explorateurs",
            "dinosaur train episodes",
            "thomas the tank engine",
            "mickey mouse clubhouse",
            "prince de la saveur",
            "la grande séquence",
            
            // Français
            "astérix et obélix dessin animé",
            "tintin dessin animé",
            "pimpin et le lapin",
            
            // Disney
            "snow white full movie",
            "lion king full movie",
            "pocahontas full movie",
            "kiki's delivery service",
            "spirited away"
        };
        
        int processed = 0;
        for (String cartoon : cartoonTitles) {
            try {
                System.out.println("Analyzing: " + cartoon);
                crawlerService.crawlAndAnalyze(cartoon);
                Thread.sleep(2000); // Attendre 2s entre les requêtes pour ne pas surcharger
                processed++;
            } catch (Exception e) {
                System.err.println("Erreur pour " + cartoon + ": " + e.getMessage());
            }
        }
        
        return ResponseEntity.ok("Base de données popuulée avec " + processed + " dessins animés connus");
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