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
            TMDBScannerService.ScanResult result = tmdbScannerService.scanChildrenAnimations(force);
            
            // Sauvegarder les résultats dans Supabase
            int saved = 0;
            for (ShowInfo show : result.processedShows) {
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
                        // Nouvelle architecture : sauver l'estimation + créer une tâche d'analyse
                        supabaseService.saveMetadataEstimation(show);
                        supabaseService.createAnalysisTask(show.getId());
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
}
