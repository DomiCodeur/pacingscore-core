package com.pacingscore.controller;

import com.pacingscore.service.VideoAnalyzerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.Map;

@RestController
@RequestMapping("/api/video-analysis")
@CrossOrigin(origins = "*")
public class VideoAnalysisController {
    
    @Autowired
    private VideoAnalyzerService videoAnalyzer;
    
    /**
     * Analyse une vidéo YouTube en temps réel
     * Détecte les cuts de scène et calcule le score
     */
    @PostMapping("/analyze")
    public ResponseEntity<Map<String, Object>> analyzeVideo(@RequestParam String videoUrl) {
        try {
            VideoAnalyzerService.VideoAnalysisResult result = videoAnalyzer.analyzeVideo(videoUrl);
            
            if (result.isSuccess()) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "videoDuration", result.getVideoDuration(),
                    "totalCuts", result.getTotalCuts(),
                    "cutsPerMinute", result.getCutsPerMinute(),
                    "pacingScore", result.getPacingScore(),
                    "evaluation", evaluateScore(result.getPacingScore())
                ));
            } else {
                return ResponseEntity.ok(Map.of(
                    "success", false,
                    "error", result.getError()
                ));
            }
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "error", "Erreur serveur: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Analyse un batch de vidéos
     */
    @PostMapping("/analyze-batch")
    public ResponseEntity<Map<String, Object>> analyzeBatch(@RequestBody Map<String, Object> request) {
        // Pour l'implémentation future
        return ResponseEntity.ok(Map.of(
            "message", "Endpoint en cours d'implémentation"
        ));
    }
    
    /**
     * Évalue le score et retourne une description
     */
    private Map<String, String> evaluateScore(double score) {
        String evaluation;
        String label;
        
        if (score >= 90) {
            evaluation = "Très calme - Parfait pour les tout-petits, rythme lent et rassurant";
            label = "EXCELLENT";
        } else if (score >= 70) {
            evaluation = "Calme - Bon rythme, adapté aux jeunes enfants, peu de changements de scène";
            label = "BON";
        } else if (score >= 50) {
            evaluation = "Modéré - Rythme normal, peut convenir à des enfants plus grands";
            label = "MOYEN";
        } else if (score >= 30) {
            evaluation = "Stimulant - Rythme rapide, attention à la durée de visionnage";
            label = "ATTENTION";
        } else {
            evaluation = "Très stimulant - Cuts fréquents, déconseillé aux jeunes enfants";
            label = "MAUVAIS";
        }
        
        return Map.of(
            "evaluation", evaluation,
            "label", label,
            "color", score >= 70 ? "green" : score >= 50 ? "yellow" : score >= 30 ? "orange" : "red"
        );
    }
}