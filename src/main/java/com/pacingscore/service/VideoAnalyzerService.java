package com.pacingscore.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class VideoAnalyzerService {
    
    @Value("${video.analyzer.temp-dir:./temp/videos}")
    private String tempDir;
    
    @Value("${video.analyzer.max-duration:300}")
    private int maxDurationSeconds; // Limiter à 5 min de vidéo pour l'analyse
    
    /**
     * Analyse une vidéo YouTube pour détecter la fréquence des cuts de scène
     * Utilise yt-dlp + FFmpeg pour l'analyse réelle
     */
    public VideoAnalysisResult analyzeVideo(String videoUrl) {
        VideoAnalysisResult result = new VideoAnalysisResult();
        
        try {
            // 1. Télécharger la vidéo (premières 5 minutes seulement)
            String videoPath = downloadVideoSnippet(videoUrl);
            
            if (videoPath == null) {
                result.setError("Impossible de télécharger la vidéo");
                return result;
            }
            
            // 2. Analyser la durée totale
            double duration = getVideoDuration(videoPath);
            result.setVideoDuration(duration);
            
            if (duration < 30) {
                // Vidéo trop courte pour une analyse fiable
                result.setCutsPerMinute(0);
                result.setPacingScore(0); // Très mauvais
                cleanup(videoPath);
                return result;
            }
            
            // 3. Détecter les changements de scène avec FFmpeg
            int totalCuts = detectSceneChanges(videoPath);
            result.setTotalCuts(totalCuts);
            
            // 4. Calculer la fréquence des cuts
            double cutsPerMinute = totalCuts / (duration / 60.0);
            result.setCutsPerMinute(cutsPerMinute);
            
            // 5. Calculer le score
            double score = calculatePacingScore(cutsPerMinute, duration);
            result.setPacingScore(score);
            
            // 6. Nettoyer
            cleanup(videoPath);
            
            result.setSuccess(true);
            
        } catch (Exception e) {
            result.setError(e.getMessage());
            result.setSuccess(false);
        }
        
        return result;
    }
    
    /**
     * Télécharge uniquement les premières minutes d'une vidéo YouTube
     * Utilise yt-dlp (doit être installé sur le système)
     */
    private String downloadVideoSnippet(String videoUrl) {
        try {
            // Créer le dossier temporaire
            File tempDirFile = new File(tempDir);
            if (!tempDirFile.exists()) {
                tempDirFile.mkdirs();
            }
            
            // Générer un nom de fichier unique
            String filename = "video_" + System.currentTimeMillis() + ".mp4";
            String outputPath = tempDir + File.separator + filename;
            
            // Commande yt-dlp pour télécharger uniquement les premières minutes
            // Note: yt-dlp doit être installé sur le serveur
            String[] command = {
                "yt-dlp",
                "--format", "best[height<=480]", // Résolution limitée pour économiser de l'espace
                "--download-sections", "*0:00-5:00", // Seulement les 5 premières minutes
                "--merge-output-format", "mp4",
                "--output", outputPath,
                videoUrl
            };
            
            Process process = Runtime.getRuntime().exec(command);
            
            // Attendre la fin du processus avec timeout
            boolean finished = process.waitFor(30, TimeUnit.SECONDS);
            
            if (!finished) {
                process.destroy();
                return null;
            }
            
            int exitCode = process.exitValue();
            
            if (exitCode == 0 && new File(outputPath).exists()) {
                return outputPath;
            } else {
                // Lire les erreurs
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                String line;
                while ((line = errorReader.readLine()) != null) {
                    System.err.println("yt-dlp error: " + line);
                }
                return null;
            }
            
        } catch (Exception e) {
            System.err.println("Erreur téléchargement vidéo: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Obtient la durée totale d'une vidéo
     */
    private double getVideoDuration(String videoPath) {
        try {
            String[] command = {
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                videoPath
            };
            
            Process process = Runtime.getRuntime().exec(command);
            
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String durationStr = reader.readLine();
            
            process.waitFor(10, TimeUnit.SECONDS);
            
            return Double.parseDouble(durationStr);
            
        } catch (Exception e) {
            System.err.println("Erreur durée vidéo: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * Détecte les changements de scène avec FFmpeg
     * Retourne le nombre total de cuts détectés
     */
    private int detectSceneChanges(String videoPath) {
        try {
            // Commande FFmpeg pour détecter les changements de scène
            // On utilise un seuil de 0.4 pour la détection (0.0 = changement subtil, 1.0 = changement radical)
            String[] command = {
                "ffmpeg",
                "-i", videoPath,
                "-vf", "select='gt(scene,0.4)',metadata=print:file=-",
                "-f", "null",
                "-"
            };
            
            Process process = Runtime.getRuntime().exec(command);
            
            BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            String line;
            int cutCount = 0;
            
            // Compter les lignes contenant "pts_time" qui indiquent un changement de scène
            while ((line = errorReader.readLine()) != null) {
                if (line.contains("pts_time")) {
                    cutCount++;
                }
            }
            
            process.waitFor(30, TimeUnit.SECONDS);
            
            return cutCount;
            
        } catch (Exception e) {
            System.err.println("Erreur détection cuts: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * Calcule le score de calme basé sur la fréquence des cuts
     * Plus de cuts = score plus bas
     */
    private double calculatePacingScore(double cutsPerMinute, double videoDuration) {
        // Formule : score = 100 - (cuts_per_minute × facteur)
        // Plus on a de cuts, plus le score baisse
        
        double score;
        
        if (cutsPerMinute <= 2) {
            // Très peu de cuts : excellent
            score = 95;
        } else if (cutsPerMinute <= 5) {
            // Quelques cuts : bon
            score = 75;
        } else if (cutsPerMinute <= 10) {
            // Cuts modérés : acceptable
            score = 50;
        } else if (cutsPerMinute <= 15) {
            // Beaucoup de cuts : mauvais
            score = 30;
        } else if (cutsPerMinute <= 20) {
            // Très nombreux cuts : très mauvais
            score = 15;
        } else {
            // Extrêmement nombreux cuts : excellent pour l'attention mais mauvais pour les enfants
            score = 5;
        }
        
        // Ajustement basé sur la durée
        // Une vidéo très courte (< 1 min) est souvent très intensive en cuts
        if (videoDuration < 60 && cutsPerMinute > 5) {
            score -= 10;
        }
        
        return Math.max(0, Math.min(100, score));
    }
    
    /**
     * Nettoie les fichiers temporaires
     */
    private void cleanup(String videoPath) {
        try {
            if (videoPath != null) {
                File file = new File(videoPath);
                if (file.exists()) {
                    file.delete();
                }
            }
        } catch (Exception e) {
            System.err.println("Erreur nettoyage: " + e.getMessage());
        }
    }
    
    // Classe de résultat d'analyse
    public static class VideoAnalysisResult {
        private boolean success;
        private String error;
        private double videoDuration;
        private int totalCuts;
        private double cutsPerMinute;
        private double pacingScore;
        
        // Getters and setters
        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }
        public String getError() { return error; }
        public void setError(String error) { this.error = error; }
        public double getVideoDuration() { return videoDuration; }
        public void setVideoDuration(double videoDuration) { this.videoDuration = videoDuration; }
        public int getTotalCuts() { return totalCuts; }
        public void setTotalCuts(int totalCuts) { this.totalCuts = totalCuts; }
        public double getCutsPerMinute() { return cutsPerMinute; }
        public void setCutsPerMinute(double cutsPerMinute) { this.cutsPerMinute = cutsPerMinute; }
        public double getPacingScore() { return pacingScore; }
        public void setPacingScore(double pacingScore) { this.pacingScore = pacingScore; }
        
        @Override
        public String toString() {
            return "VideoAnalysisResult{" +
                "success=" + success +
                ", error='" + error + '\'' +
                ", videoDuration=" + videoDuration +
                ", totalCuts=" + totalCuts +
                ", cutsPerMinute=" + cutsPerMinute +
                ", pacingScore=" + pacingScore +
                '}';
        }
    }
}