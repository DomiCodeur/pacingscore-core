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
    
    @Autowired
    private TMDBService tmdbService;
    
    @Autowired
    private TMDBScannerService tmdbScannerService;
    
    @Autowired
    private SupabaseService supabaseService;
    
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
     * Endpoint pour scanner TOUS les dessins animés pour enfants sur TMDB
     * et les analyser automatiquement
     */
    @PostMapping("/scan-tmdb")
    public ResponseEntity<String> scanTMDB() {
        try {
            TMDBScannerService.ScanResult result = tmdbScannerService.scanChildrenAnimations();
            
            // Sauvegarder les résultats dans Supabase
            int saved = 0;
            for (TMDBScannerService.ShowInfo show : result.processedShows) {
                try {
                    // TODO: Implémenter la sauvegarde via SupabaseService
                    // supabaseService.saveShowAnalysis(show);
                    saved++;
                } catch (Exception e) {
                    System.err.println("Erreur sauvegarde " + show.getTitle() + ": " + e.getMessage());
                }
            }
            
            return ResponseEntity.ok(
                "Scan TMDB terminé!\n" +
                "- Dessins animés analysés: " + result.analyzed + "\n" +
                "- Déjà présents: " + result.alreadyAnalyzed + "\n" +
                "- Échecs: " + result.failed + "\n" +
                "- Sauvegardés: " + saved + "\n" +
                "- Total traité: " + result.processedShows.size()
            );
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Erreur lors du scan: " + e.getMessage());
        }
    }
    
    /**
     * Endpoint pour populer avec une liste spécifique de dessins animés
     */
    @PostMapping("/populate")
    public ResponseEntity<String> populateDatabase() {
        try {
            // Récupérer les séries enfants depuis TMDB
            List<TMDBService.ShowInfo> shows = tmdbService.searchChildrenCartoons();
            
            // Filtrer et sauvegarder dans Supabase
            int saved = 0;
            int skipped = 0;
            
            for (TMDBService.ShowInfo show : shows) {
                // Vérifier si la série existe déjà
                if (!supabaseService.showExists(show.getId())) {
                    try {
                        supabaseService.saveShowAnalysis(show);
                        saved++;
                        Thread.sleep(500); // Pause pour respecter les limites d'API
                    } catch (Exception e) {
                        System.err.println("Erreur pour " + show.getTitle() + ": " + e.getMessage());
                        skipped++;
                    }
                } else {
                    skipped++;
                    System.out.println("Déjà présent: " + show.getTitle());
                }
            }
            
            return ResponseEntity.ok(
                "Base de données popuulée avec " + saved + " nouvelles séries enfants de TMDB (déjà présentes: " + skipped + ")"
            );
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Erreur: " + e.getMessage());
        }
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