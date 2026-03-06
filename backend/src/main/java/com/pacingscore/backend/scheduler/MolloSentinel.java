package com.pacingscore.backend.scheduler;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import com.pacingscore.backend.service.TMDBScannerService;

@Component
@EnableScheduling
public class MolloSentinel {

    @Autowired
    private TMDBScannerService scanner;

    /**
     * Scan automatique quotidien à 02:00 du matin.
     * Scanne à la fois les séries TV et les films d'animation pour enfants.
     * Utilise l'option skip existants (force=false) pour éviter de réanalyser ce qui existe déjà.
     */
    @Scheduled(cron = "0 0 2 * * ?") // Tous les jours à 02:00
    public void dailyCrawl() {
        System.out.println("=== Démarrage du scan TMDB quotidien (MolloSentinel) ===");
        try {
            scanner.scanChildrenAnimations(false); // skip existants
            scanner.scanMovies(false); // skip existants
            System.out.println("=== Scan terminé avec succès ===");
        } catch (Exception e) {
            System.err.println("Erreur lors du scan automatique: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
