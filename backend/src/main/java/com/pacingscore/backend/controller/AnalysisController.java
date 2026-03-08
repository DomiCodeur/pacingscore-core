package com.pacingscore.backend.controller;

import com.pacingscore.backend.service.TMDBService;
import com.pacingscore.backend.service.TMDBScannerService;
import com.pacingscore.backend.service.SupabaseService;
import com.pacingscore.backend.service.TMDBScannerService.ScanResult;
import com.pacingscore.backend.service.TMDBService.ShowInfo;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    @Autowired
    private TMDBScannerService tmdbScannerService;
    
    @Autowired
    private SupabaseService supabaseService;
    
    @Autowired
    private TMDBService tmdbService;
    
    /**
     * Endpoint pour scanner TOUS les dessins animés pour enfants sur TMDB
     * et les analyser automatiquement
     */
    @Operation(summary = "Scan automatique des dessins animés sur TMDB",
               description = "Scanne automatiquement tous les dessins animés pour enfants sur TMDB et les analyse",
               responses = {
                   @ApiResponse(responseCode = "200", description = "Scan terminé", content = @Content(mediaType = "text/plain")),
                   @ApiResponse(responseCode = "500", description = "Erreur serveur")
               })
    @PostMapping("/scan-tmdb")
    public ResponseEntity<String> scanTMDB(@RequestParam(required = false) boolean force) {
        try {
            TMDBScannerService.ScanResult tvResult = tmdbScannerService.scanChildrenAnimations(force);
            TMDBScannerService.ScanResult movieResult = tmdbScannerService.scanMovies(force);
            
            int totalAnalyzed = tvResult.analyzed + movieResult.analyzed;
            int totalAlready = tvResult.alreadyAnalyzed + movieResult.alreadyAnalyzed;
            int totalFailed = tvResult.failed + movieResult.failed;
            int totalProcessed = tvResult.processedShows.size() + movieResult.processedShows.size();
            
            return ResponseEntity.ok(
                "Scan TMDB terminé!\n" +
                "--- Séries TV ---\n" +
                "  Analysés: " + tvResult.analyzed + "\n" +
                "  Déjà présents: " + tvResult.alreadyAnalyzed + "\n" +
                "  Échoués: " + tvResult.failed + "\n" +
                "--- Films ---\n" +
                "  Analysés: " + movieResult.analyzed + "\n" +
                "  Déjà présents: " + movieResult.alreadyAnalyzed + "\n" +
                "  Échoués: " + movieResult.failed + "\n" +
                "--- Total ---\n" +
                "  Nouvelles entrées: " + totalAnalyzed + "\n" +
                "  Total traité: " + totalProcessed + "\n" +
                "  Erreurs: " + totalFailed
            );
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Erreur lors du scan: " + e.getMessage());
        }
    }
    
    /**
     * Endpoint pour populer avec une liste spécifique de dessins animés
     */
    @Operation(summary = "Peuplement automatique de la base",
               description = "Récupère des dessins animés enfants depuis TMDB et les sauvegarde dans Supabase",
               responses = {
                   @ApiResponse(responseCode = "200", description = "Population terminée", content = @Content(mediaType = "text/plain")),
                   @ApiResponse(responseCode = "500", description = "Erreur serveur")
               })
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
                        // Nouvelle architecture : créer une tâche d'analyse avec métadonnées complètes
                        supabaseService.createAnalysisTask(show);
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

    @PostMapping("/massive-import")
    public ResponseEntity<String> massiveImport() {
        try {
            String result = tmdbScannerService.performMassiveImport();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Erreur lors du massive import: " + e.getMessage());
        }
    }

    /* scan-diverse désactivé car scanner limité à l'animation */

    @PostMapping("/reset-failed")
    public ResponseEntity<String> resetFailed() {
        int count = supabaseService.resetFailedTasks();
        return ResponseEntity.ok("Réinitialisation terminée : " + count + " tâches remises en 'pending'.");
    }

    /**
     * Monitoring simple de la file d'analyse
     */
    @GetMapping("/queue-status")
    public ResponseEntity<Map<String, Integer>> getQueueStatus() {
        try {
            Map<String, Integer> counts = supabaseService.getAnalysisQueueStatus();
            return ResponseEntity.ok(counts);
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Integer> err = new HashMap<>();
            err.put("error", 1);
            return ResponseEntity.ok(err);
        }
    }
}
